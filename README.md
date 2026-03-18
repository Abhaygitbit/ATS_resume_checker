# ATS Resume Analyzer — Setup Guide

## Quick Start (SQLite — zero config)
```bash
pip install -r requirements.txt
cp .env.example .env   # fill in Firebase keys
python app.py          # → http://localhost:5000
```

---

## STEP 1 — Firebase / Google OAuth

1. https://console.firebase.google.com → Create project
2. Authentication → Get started → Enable Google sign-in
3. Project Settings → General → Your apps → Web app (</>)
4. Copy the firebaseConfig values into .env:

```
FIREBASE_API_KEY=AIza...
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=123456789
FIREBASE_APP_ID=1:123:web:abc
```

5. Firebase Console → Authentication → Settings → Authorized domains
   Add: localhost  (dev)  and  your-app.onrender.com  (prod)

---

## STEP 2 — Switch to MySQL (Production)

```bash
pip install pymysql
```

Create DB:
```sql
CREATE DATABASE ats_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ats_user'@'localhost' IDENTIFIED BY 'StrongPass123!';
GRANT ALL PRIVILEGES ON ats_db.* TO 'ats_user'@'localhost';
FLUSH PRIVILEGES;
```

Update .env:
```
DATABASE_URL=mysql+pymysql://ats_user:StrongPass123!@localhost:3306/ats_db
```

Tables are auto-created on app startup (db.create_all()).
For cloud MySQL (PlanetScale / Railway / Aiven): replace localhost:3306 with cloud host.

---

## STEP 3 — Make yourself Admin

After logging in once via Google:
```bash
python
>>> from app import create_app
>>> from models.user import User
>>> from database.db import db
>>> app = create_app()
>>> with app.app_context():
...     u = User.query.filter_by(email='your@email.com').first()
...     u.is_admin = True
...     db.session.commit()
```

Then visit /admin

---

## STEP 4 — Deploy to Render

1. Push to GitHub
2. render.com → New Web Service → connect repo
3. Build: pip install -r requirements.txt
4. Start: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2
5. Add all Firebase env vars in Render dashboard
6. Add Render URL to Firebase Authorized Domains

---

## API Reference

POST  /api/auth/google              Firebase Google login
POST  /api/auth/logout              Log out
GET   /api/auth/me                  Current user
POST  /api/resumes/upload           Upload resume + JD
GET   /api/resumes                  List resumes
GET   /api/resumes/<id>             Resume + analysis detail
GET   /api/resumes/<id>/report      Download PDF
DELETE /api/resumes/<id>            Delete resume
GET   /api/admin/users              All users (admin only)
GET   /api/admin/resumes            All resumes (admin only)
GET   /api/admin/stats              Platform stats (admin only)
POST  /api/admin/users/<id>/toggle-admin  Promote/demote
DELETE /api/admin/users/<id>        Delete user
