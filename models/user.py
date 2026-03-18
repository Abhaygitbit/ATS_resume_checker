from database.db import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id          = db.Column(db.Integer, primary_key=True)
    firebase_uid= db.Column(db.String(128), unique=True, nullable=True)
    email       = db.Column(db.String(255), unique=True, nullable=False)
    name        = db.Column(db.String(255), nullable=False)
    photo_url   = db.Column(db.String(512), nullable=True)
    is_admin    = db.Column(db.Boolean, default=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    resumes = db.relationship('Resume', backref='owner', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.email}>'
