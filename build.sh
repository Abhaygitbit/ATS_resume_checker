#!/usr/bin/env bash

# Install system dependencies for Pillow and PyMuPDF
apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libfreetype6-dev

# Install Python dependencies
pip install -r requirements.txt
```

---

## ✅ Fix 4 — Update Render Build Command

Go to **Render Dashboard → Your Service → Settings → Build Command** and change it to:
```
pip install --upgrade pip setuptools wheel && pip install -r requirements.txt
```

---

## ✅ Fix 5 — Clean up `requirements.txt`

Also replace `PyMuPDF` — it also causes build issues on Render free tier. Your final clean `requirements.txt`:
```
Flask==3.0.3
Flask-Login==0.6.3
Flask-SQLAlchemy==3.1.1
SQLAlchemy==2.0.30
pdfplumber==0.11.0
python-docx==1.1.2
reportlab==4.2.0
Werkzeug==3.0.3
requests==2.29.0
python-dotenv==1.0.1
Pillow==10.1.0
gunicorn==22.0.0
Flask-CORS==4.0.1
nltk==3.8.1