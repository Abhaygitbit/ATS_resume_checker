import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ats-secret-key-change-in-production')
    
    # SQLite by default — swap for MySQL in production
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///ats_database.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}

    # Firebase config — fill in your project credentials
    FIREBASE_API_KEY            = os.environ.get('FIREBASE_API_KEY', '')
    FIREBASE_AUTH_DOMAIN        = os.environ.get('FIREBASE_AUTH_DOMAIN', '')
    FIREBASE_PROJECT_ID         = os.environ.get('FIREBASE_PROJECT_ID', '')
    FIREBASE_STORAGE_BUCKET     = os.environ.get('FIREBASE_STORAGE_BUCKET', '')
    FIREBASE_MESSAGING_SENDER_ID= os.environ.get('FIREBASE_MESSAGING_SENDER_ID', '')
    FIREBASE_APP_ID             = os.environ.get('FIREBASE_APP_ID', '')

    FIREBASE_CONFIG = {
        "apiKey":            FIREBASE_API_KEY,
        "authDomain":        FIREBASE_AUTH_DOMAIN,
        "projectId":         FIREBASE_PROJECT_ID,
        "storageBucket":     FIREBASE_STORAGE_BUCKET,
        "messagingSenderId": FIREBASE_MESSAGING_SENDER_ID,
        "appId":             FIREBASE_APP_ID,
        "databaseURL":       ""
    }
