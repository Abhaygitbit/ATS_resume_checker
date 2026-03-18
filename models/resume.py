from database.db import db
from datetime import datetime
import json

class Resume(db.Model):
    __tablename__ = 'resumes'

    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename        = db.Column(db.String(255), nullable=False)
    original_name   = db.Column(db.String(255), nullable=False)
    file_path       = db.Column(db.String(512), nullable=False)
    file_type       = db.Column(db.String(10), nullable=False)
    job_description = db.Column(db.Text, nullable=True)
    raw_text        = db.Column(db.Text, nullable=True)
    ats_score       = db.Column(db.Float, nullable=True)
    status          = db.Column(db.String(50), default='pending')  # pending/analyzed/error
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    analysis = db.relationship('Analysis', backref='resume', lazy=True, uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Resume {self.original_name} score={self.ats_score}>'


class Analysis(db.Model):
    __tablename__ = 'analyses'

    id                  = db.Column(db.Integer, primary_key=True)
    resume_id           = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False)
    keyword_score       = db.Column(db.Float, default=0)
    skills_score        = db.Column(db.Float, default=0)
    section_score       = db.Column(db.Float, default=0)
    matched_keywords    = db.Column(db.Text, default='[]')   # JSON list
    missing_keywords    = db.Column(db.Text, default='[]')
    matched_skills      = db.Column(db.Text, default='[]')
    missing_skills      = db.Column(db.Text, default='[]')
    sections_found      = db.Column(db.Text, default='[]')
    sections_missing    = db.Column(db.Text, default='[]')
    suggestions         = db.Column(db.Text, default='[]')
    created_at          = db.Column(db.DateTime, default=datetime.utcnow)

    def get_matched_keywords(self):
        return json.loads(self.matched_keywords or '[]')

    def get_missing_keywords(self):
        return json.loads(self.missing_keywords or '[]')

    def get_matched_skills(self):
        return json.loads(self.matched_skills or '[]')

    def get_missing_skills(self):
        return json.loads(self.missing_skills or '[]')

    def get_sections_found(self):
        return json.loads(self.sections_found or '[]')

    def get_sections_missing(self):
        return json.loads(self.sections_missing or '[]')

    def get_suggestions(self):
        return json.loads(self.suggestions or '[]')
