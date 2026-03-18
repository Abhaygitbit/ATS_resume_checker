from flask import Blueprint, request, jsonify, session, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
from database.db import db
import requests as http_req

auth_bp = Blueprint('auth', __name__)

# ── Google sign-in (via Firebase ID token sent from frontend) ───────────────

@auth_bp.route('/api/auth/google', methods=['POST'])
def google_login():
    data = request.get_json()
    id_token = data.get('idToken')
    if not id_token:
        return jsonify({'error': 'No token provided'}), 400

    # Verify token with Firebase REST API
    verify_url = (
        'https://identitytoolkit.googleapis.com/v1/accounts:lookup'
        '?key={api_key}'
    )
    # We trust the decoded info sent from the frontend for MVP;
    # in production, verify with firebase-admin SDK (see setup guide).
    user_info = data.get('user', {})
    uid       = user_info.get('uid')
    email     = user_info.get('email')
    name      = user_info.get('displayName', email)
    photo     = user_info.get('photoURL', '')

    if not uid or not email:
        return jsonify({'error': 'Invalid user info'}), 400

    user = User.query.filter_by(firebase_uid=uid).first()
    if not user:
        user = User.query.filter_by(email=email).first()
        if user:
            user.firebase_uid = uid
            user.photo_url    = photo
        else:
            user = User(firebase_uid=uid, email=email, name=name, photo_url=photo)
            db.session.add(user)
    else:
        user.name      = name
        user.photo_url = photo

    db.session.commit()
    login_user(user, remember=True)

    return jsonify({
        'success': True,
        'user': {
            'id':      user.id,
            'name':    user.name,
            'email':   user.email,
            'photo':   user.photo_url,
            'isAdmin': user.is_admin,
        }
    })


@auth_bp.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'success': True})


@auth_bp.route('/api/auth/me')
def me():
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': {
                'id':      current_user.id,
                'name':    current_user.name,
                'email':   current_user.email,
                'photo':   current_user.photo_url,
                'isAdmin': current_user.is_admin,
            }
        })
    return jsonify({'authenticated': False})
