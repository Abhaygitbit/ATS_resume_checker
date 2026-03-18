from flask import Blueprint, request, jsonify, send_file, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from database.db import db
from models.resume import Resume, Analysis
from services.parser import extract_text, detect_sections
from services.ats_score import compute_ats_score
from services.suggestion_engine import generate_suggestions
from services.report_generator import generate_pdf_report
import os, uuid, json, io

resume_bp = Blueprint('resume', __name__)

ALLOWED = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED


@resume_bp.route('/api/resumes/upload', methods=['POST'])
@login_required
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['resume']
    jd   = request.form.get('job_description', '')

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only PDF and DOCX files are allowed'}), 400

    original_name = file.filename
    ext           = original_name.rsplit('.', 1)[1].lower()
    unique_name   = f'{uuid.uuid4().hex}.{ext}'
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    save_path = os.path.join(upload_folder, unique_name)
    file.save(save_path)

    resume = Resume(
        user_id       = current_user.id,
        filename      = unique_name,
        original_name = original_name,
        file_path     = save_path,
        file_type     = ext,
        job_description = jd,
        status        = 'pending',
    )
    db.session.add(resume)
    db.session.flush()  # get resume.id

    # ── Parse & Analyse ──────────────────────────────────────────────────────
    try:
        raw_text = extract_text(save_path)
        resume.raw_text = raw_text

        score_data   = compute_ats_score(raw_text, jd)
        section_data = detect_sections(raw_text)
        suggestions  = generate_suggestions(score_data, section_data)

        resume.ats_score = score_data['overall_score']
        resume.status    = 'analyzed'

        analysis = Analysis(
            resume_id       = resume.id,
            keyword_score   = score_data['keyword_score'],
            skills_score    = score_data['skills_score'],
            section_score   = len(section_data['found']) / max(len(section_data['found']) + len(section_data['missing']), 1) * 100,
            matched_keywords= json.dumps(score_data['matched_keywords']),
            missing_keywords= json.dumps(score_data['missing_keywords']),
            matched_skills  = json.dumps(score_data['matched_skills']),
            missing_skills  = json.dumps(score_data['missing_skills']),
            sections_found  = json.dumps(section_data['found']),
            sections_missing= json.dumps(section_data['missing']),
            suggestions     = json.dumps(suggestions),
        )
        db.session.add(analysis)
    except Exception as e:
        resume.status = 'error'
        print(f'Analysis error: {e}')

    db.session.commit()
    return jsonify({'success': True, 'resume_id': resume.id}), 201


@resume_bp.route('/api/resumes', methods=['GET'])
@login_required
def list_resumes():
    resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.created_at.desc()).all()
    return jsonify([_resume_to_dict(r) for r in resumes])


@resume_bp.route('/api/resumes/<int:resume_id>', methods=['GET'])
@login_required
def get_resume(resume_id):
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    data   = _resume_to_dict(resume)
    if resume.analysis:
        a = resume.analysis
        data['analysis'] = {
            'keyword_score':    a.keyword_score,
            'skills_score':     a.skills_score,
            'section_score':    a.section_score,
            'matched_keywords': a.get_matched_keywords(),
            'missing_keywords': a.get_missing_keywords(),
            'matched_skills':   a.get_matched_skills(),
            'missing_skills':   a.get_missing_skills(),
            'sections_found':   a.get_sections_found(),
            'sections_missing': a.get_sections_missing(),
            'suggestions':      a.get_suggestions(),
        }
    return jsonify(data)


@resume_bp.route('/api/resumes/<int:resume_id>/report', methods=['GET'])
@login_required
def download_report(resume_id):
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    if not resume.analysis:
        return jsonify({'error': 'No analysis found'}), 404
    pdf_bytes = generate_pdf_report(resume, resume.analysis, current_user)
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'ats_report_{resume_id}.pdf'
    )


@resume_bp.route('/api/resumes/<int:resume_id>', methods=['DELETE'])
@login_required
def delete_resume(resume_id):
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    try:
        if os.path.exists(resume.file_path):
            os.remove(resume.file_path)
    except Exception:
        pass
    db.session.delete(resume)
    db.session.commit()
    return jsonify({'success': True})


def _resume_to_dict(r: Resume) -> dict:
    return {
        'id':           r.id,
        'original_name': r.original_name,
        'file_type':    r.file_type,
        'ats_score':    r.ats_score,
        'status':       r.status,
        'created_at':   r.created_at.strftime('%Y-%m-%d %H:%M'),
    }
