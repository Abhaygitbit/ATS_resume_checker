from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import io

PRIMARY   = colors.HexColor('#2563EB')
SUCCESS   = colors.HexColor('#16A34A')
WARNING   = colors.HexColor('#D97706')
DANGER    = colors.HexColor('#DC2626')
LIGHT_BG  = colors.HexColor('#F1F5F9')
DARK_TEXT = colors.HexColor('#1E293B')

def _score_color(score):
    if score >= 75: return SUCCESS
    if score >= 50: return WARNING
    return DANGER

def generate_pdf_report(resume, analysis, user) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )
    styles = getSampleStyleSheet()
    story  = []

    # Title
    title_style = ParagraphStyle('Title', parent=styles['Title'],
        fontSize=22, textColor=PRIMARY, spaceAfter=4, alignment=TA_CENTER)
    story.append(Paragraph('ATS Resume Analysis Report', title_style))
    story.append(Spacer(1, 0.3*cm))

    sub_style = ParagraphStyle('Sub', parent=styles['Normal'],
        fontSize=10, textColor=colors.grey, alignment=TA_CENTER)
    story.append(Paragraph(f'Generated on {datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC")}', sub_style))
    story.append(HRFlowable(width='100%', thickness=1, color=LIGHT_BG, spaceAfter=12))

    # Candidate info
    h2 = ParagraphStyle('H2', parent=styles['Heading2'], textColor=DARK_TEXT, fontSize=13, spaceAfter=6)
    normal = ParagraphStyle('N', parent=styles['Normal'], fontSize=10, leading=14)

    story.append(Paragraph('Candidate Information', h2))
    info_data = [
        ['Name',  user.name],
        ['Email', user.email],
        ['Resume', resume.original_name],
        ['Submitted', resume.created_at.strftime('%Y-%m-%d %H:%M')],
    ]
    info_table = Table(info_data, colWidths=[4*cm, 12*cm])
    info_table.setStyle(TableStyle([
        ('FONTSIZE',  (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (0,-1), PRIMARY),
        ('FONTNAME',  (0,0), (0,-1), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white, LIGHT_BG]),
        ('GRID', (0,0), (-1,-1), 0.3, colors.lightgrey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.5*cm))

    # Score summary
    story.append(Paragraph('ATS Score Summary', h2))
    overall = resume.ats_score or 0
    score_color = _score_color(overall)
    score_style = ParagraphStyle('Score', parent=styles['Normal'],
        fontSize=36, textColor=score_color, alignment=TA_CENTER, spaceAfter=4)
    story.append(Paragraph(f'{overall:.1f}/100', score_style))

    score_data = [
        ['Metric', 'Score', 'Weight'],
        ['Keyword Match', f'{analysis.keyword_score:.1f}%', '60%'],
        ['Skills Match',  f'{analysis.skills_score:.1f}%',  '40%'],
        ['Overall ATS',   f'{overall:.1f}%',                '—'],
    ]
    st = Table(score_data, colWidths=[8*cm, 4*cm, 4*cm])
    st.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
        ('GRID', (0,0), (-1,-1), 0.3, colors.lightgrey),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(st)
    story.append(Spacer(1, 0.5*cm))

    # Keywords
    story.append(Paragraph('Keyword Analysis', h2))
    matched_kw = analysis.get_matched_keywords()
    missing_kw = analysis.get_missing_keywords()

    kw_data = [['✅ Matched Keywords', '❌ Missing Keywords']]
    max_rows = max(len(matched_kw), len(missing_kw), 1)
    for i in range(min(max_rows, 15)):
        m = matched_kw[i] if i < len(matched_kw) else ''
        x = missing_kw[i] if i < len(missing_kw) else ''
        kw_data.append([m, x])
    kw_t = Table(kw_data, colWidths=[8*cm, 8*cm])
    kw_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
        ('GRID', (0,0), (-1,-1), 0.3, colors.lightgrey),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(kw_t)
    story.append(Spacer(1, 0.5*cm))

    # Sections
    story.append(Paragraph('Resume Sections', h2))
    found_sec   = analysis.get_sections_found()
    missing_sec = analysis.get_sections_missing()
    sec_data = [['✅ Sections Present', '❌ Sections Missing']]
    max_s = max(len(found_sec), len(missing_sec), 1)
    for i in range(max_s):
        f = found_sec[i].capitalize() if i < len(found_sec) else ''
        m = missing_sec[i].capitalize() if i < len(missing_sec) else ''
        sec_data.append([f, m])
    sec_t = Table(sec_data, colWidths=[8*cm, 8*cm])
    sec_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
        ('GRID', (0,0), (-1,-1), 0.3, colors.lightgrey),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(sec_t)
    story.append(Spacer(1, 0.5*cm))

    # Suggestions
    story.append(Paragraph('Improvement Suggestions', h2))
    for sug in analysis.get_suggestions():
        story.append(Paragraph(f'• {sug}', normal))
        story.append(Spacer(1, 0.15*cm))

    story.append(Spacer(1, 1*cm))
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'],
        fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    story.append(HRFlowable(width='100%', thickness=0.5, color=colors.lightgrey))
    story.append(Paragraph('Generated by ATS Resume Analyzer • Powered by AI', footer_style))

    doc.build(story)
    return buf.getvalue()
