import re
from collections import Counter

# Common technical skills list
COMMON_SKILLS = [
    'python','java','javascript','typescript','c++','c#','go','rust','kotlin','swift',
    'react','angular','vue','nodejs','express','django','flask','fastapi','spring',
    'sql','mysql','postgresql','mongodb','redis','sqlite','oracle',
    'aws','azure','gcp','docker','kubernetes','terraform','ansible','jenkins','ci/cd',
    'git','linux','bash','html','css','rest','graphql','grpc','microservices',
    'machine learning','deep learning','nlp','tensorflow','pytorch','scikit-learn',
    'data analysis','pandas','numpy','spark','hadoop','kafka',
    'agile','scrum','jira','figma','photoshop',
]

def tokenize(text: str) -> list[str]:
    text = text.lower()
    # remove punctuation except hyphen inside words
    text = re.sub(r'[^\w\s\-]', ' ', text)
    tokens = text.split()
    return tokens

def extract_keywords(text: str, min_len: int = 3) -> list[str]:
    """Extract meaningful words from text (simple, no NLTK dependency required)."""
    STOPWORDS = {
        'the','and','for','are','but','not','you','all','any','can','had','her',
        'was','one','our','out','day','get','has','him','his','how','man','new',
        'now','old','see','two','way','who','boy','did','its','let','put','say',
        'she','too','use','with','this','that','have','from','they','will','been',
        'into','more','also','when','than','then','just','your','like','some',
        'what','well','also','back','after','over','good','time','know','take',
        'people','into','year','make','work','could','other','their','would',
    }
    tokens = tokenize(text)
    return [t for t in tokens if len(t) >= min_len and t not in STOPWORDS and not t.isdigit()]

def compute_ats_score(resume_text: str, job_description: str) -> dict:
    """
    Returns a dict with:
      - overall_score (0-100)
      - keyword_score, skills_score (0-100 each)
      - matched_keywords, missing_keywords
      - matched_skills, missing_skills
    """
    resume_tokens  = set(extract_keywords(resume_text))
    jd_keywords    = extract_keywords(job_description)

    # Deduplicate while preserving frequency order
    seen = set()
    unique_jd_kw = []
    for kw in jd_keywords:
        if kw not in seen:
            seen.add(kw)
            unique_jd_kw.append(kw)

    # ── Keyword matching ─────────────────────────────────────────────────────
    matched_kw  = [kw for kw in unique_jd_kw if kw in resume_tokens]
    missing_kw  = [kw for kw in unique_jd_kw if kw not in resume_tokens]
    kw_score    = (len(matched_kw) / len(unique_jd_kw) * 100) if unique_jd_kw else 0

    # ── Skill matching ───────────────────────────────────────────────────────
    jd_lower      = job_description.lower()
    resume_lower  = resume_text.lower()
    jd_skills     = [s for s in COMMON_SKILLS if s in jd_lower]
    matched_skills= [s for s in jd_skills if s in resume_lower]
    missing_skills= [s for s in jd_skills if s not in resume_lower]
    skills_score  = (len(matched_skills) / len(jd_skills) * 100) if jd_skills else 50

    overall = round(kw_score * 0.6 + skills_score * 0.4, 1)

    return {
        'overall_score':    min(overall, 100),
        'keyword_score':    round(kw_score, 1),
        'skills_score':     round(skills_score, 1),
        'matched_keywords': matched_kw[:40],
        'missing_keywords': missing_kw[:40],
        'matched_skills':   matched_skills,
        'missing_skills':   missing_skills,
    }
