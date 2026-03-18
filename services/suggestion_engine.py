def generate_suggestions(score_data: dict, section_data: dict) -> list[str]:
    suggestions = []
    overall     = score_data.get('overall_score', 0)
    kw_score    = score_data.get('keyword_score', 0)
    sk_score    = score_data.get('skills_score', 0)
    missing_kw  = score_data.get('missing_keywords', [])
    missing_sk  = score_data.get('missing_skills', [])
    miss_sec    = section_data.get('missing', [])

    # Score-based top-level advice
    if overall < 40:
        suggestions.append('⚠️ Your ATS score is low. Heavily tailor your resume to the job description.')
    elif overall < 60:
        suggestions.append('📈 Moderate match. Add more job-specific keywords and skills to improve.')
    elif overall < 80:
        suggestions.append('✅ Good match! A few targeted tweaks will push you into the top tier.')
    else:
        suggestions.append('🌟 Excellent ATS match! Your resume is well-aligned with this role.')

    # Keyword suggestions
    if kw_score < 50 and missing_kw:
        top = missing_kw[:8]
        suggestions.append(f'🔑 Incorporate these missing keywords: {", ".join(top)}.')
    if missing_kw:
        suggestions.append('📝 Mirror the exact phrasing from the job description where possible.')

    # Skills suggestions
    if missing_sk:
        suggestions.append(f'💡 Consider adding or demonstrating these skills: {", ".join(missing_sk[:6])}.')
    if sk_score < 40:
        suggestions.append('🛠️ Your listed skills have low overlap with the job requirements — review the JD carefully.')

    # Section suggestions
    for sec in miss_sec:
        label = sec.capitalize()
        if sec == 'summary':
            suggestions.append('📄 Add a concise Professional Summary at the top — ATS scanners reward it.')
        elif sec == 'skills':
            suggestions.append('🧰 Create a dedicated Skills section with relevant technologies and tools.')
        elif sec == 'experience':
            suggestions.append('💼 Add a Work Experience section with quantifiable achievements.')
        elif sec == 'education':
            suggestions.append('🎓 Include an Education section with your degree(s) and institution(s).')
        elif sec == 'certifications':
            suggestions.append('📜 Add relevant certifications to stand out.')
        elif sec == 'projects':
            suggestions.append('🚀 Include a Projects section to showcase hands-on experience.')
        else:
            suggestions.append(f'📌 Consider adding a {label} section.')

    # General best practices
    suggestions.append('📐 Use standard section headings (Experience, Education, Skills) — avoid creative alternatives.')
    suggestions.append('🔠 Use a clean, single-column ATS-friendly format (no tables, graphics, or text boxes).')
    suggestions.append('📊 Quantify achievements: use numbers, percentages, and timeframes.')

    return suggestions
