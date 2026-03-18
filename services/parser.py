import pdfplumber
from docx import Document
import os, re

def extract_text(file_path: str) -> str:
    """Extract raw text from PDF or DOCX."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return _extract_pdf(file_path)
    elif ext == '.docx':
        return _extract_docx(file_path)
    return ''

def _extract_pdf(path: str) -> str:
    text = []
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text.append(t)
    except Exception as e:
        print(f'PDF extraction error: {e}')
    return '\n'.join(text)

def _extract_docx(path: str) -> str:
    try:
        doc = Document(path)
        return '\n'.join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as e:
        print(f'DOCX extraction error: {e}')
        return ''

# ── Section detection ────────────────────────────────────────────────────────

SECTION_PATTERNS = {
    'contact':     r'\b(contact|email|phone|address|linkedin|github)\b',
    'summary':     r'\b(summary|objective|profile|about)\b',
    'experience':  r'\b(experience|work history|employment|career)\b',
    'education':   r'\b(education|degree|university|college|school|academic)\b',
    'skills':      r'\b(skills|technologies|tech stack|competencies|expertise)\b',
    'projects':    r'\b(projects|portfolio|work samples)\b',
    'certifications': r'\b(certifications?|certificates?|courses?|training)\b',
    'awards':      r'\b(awards?|honors?|achievements?|recognition)\b',
}

def detect_sections(text: str) -> dict:
    text_lower = text.lower()
    found, missing = [], []
    for section, pattern in SECTION_PATTERNS.items():
        if re.search(pattern, text_lower):
            found.append(section)
        else:
            missing.append(section)
    return {'found': found, 'missing': missing}
