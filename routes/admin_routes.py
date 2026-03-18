from flask import Blueprint, jsonify, abort
from flask_login import login_required, current_user
from models.user import User
from models.resume import Resume, Analysis
from database.db import db

admin_bp = Blueprint('admin', __name__)

def require_admin():
    if not current_user.is_authenticated or not current_user.is_admin:
        abort(403)

@admin_bp.route('/api/admin/users')
@login_required
def all_users():
    require_admin()
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify([{
        'id':         u.id,
        'name':       u.name,
        'email':      u.email,
        'is_admin':   u.is_admin,
        'created_at': u.created_at.strftime('%Y-%m-%d'),
        'resume_count': len(u.resumes),
    } for u in users])


@admin_bp.route('/api/admin/resumes')
@login_required
def all_resumes():
    require_admin()
    resumes = Resume.query.order_by(Resume.created_at.desc()).all()
    return jsonify([{
        'id':           r.id,
        'user_id':      r.user_id,
        'user_email':   r.owner.email,
        'original_name': r.original_name,
        'ats_score':    r.ats_score,
        'status':       r.status,
        'created_at':   r.created_at.strftime('%Y-%m-%d %H:%M'),
    } for r in resumes])


@admin_bp.route('/api/admin/stats')
@login_required
def stats():
    require_admin()
    total_users   = User.query.count()
    total_resumes = Resume.query.count()
    analyzed      = Resume.query.filter_by(status='analyzed').count()
    avg_score     = db.session.query(db.func.avg(Resume.ats_score)).scalar() or 0
    return jsonify({
        'total_users':   total_users,
        'total_resumes': total_resumes,
        'analyzed':      analyzed,
        'avg_ats_score': round(float(avg_score), 1),
    })


@admin_bp.route('/api/admin/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
def toggle_admin(user_id):
    require_admin()
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot modify your own admin status'}), 400
    user.is_admin = not user.is_admin
    db.session.commit()
    return jsonify({'success': True, 'is_admin': user.is_admin})


@admin_bp.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    require_admin()
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot delete yourself'}), 400
    db.session.delete(user)
    db.session.commit()
    return jsonify({'success': True})
