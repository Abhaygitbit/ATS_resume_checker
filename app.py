from flask import Flask, render_template, send_from_directory
from flask_login import LoginManager
from config import Config
from database.db import db, init_db
from models.user import User
from routes.auth_routes import auth_bp
from routes.resume_routes import resume_bp
from routes.admin_routes import admin_bp
from flask_cors import CORS
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, supports_credentials=True)
    db.init_app(app)

    # Flask-Login
    login_manager = LoginManager(app)
    login_manager.login_view = 'index'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(admin_bp)

    # Frontend routes (SPA-style)
    @app.route('/')
    def index():
        return render_template('index.html', firebase_config=app.config['FIREBASE_CONFIG'])

    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html', firebase_config=app.config['FIREBASE_CONFIG'])

    @app.route('/upload')
    def upload():
        return render_template('upload.html', firebase_config=app.config['FIREBASE_CONFIG'])

    @app.route('/report/<int:resume_id>')
    def report(resume_id):
        return render_template('report.html', firebase_config=app.config['FIREBASE_CONFIG'], resume_id=resume_id)

    @app.route('/admin')
    def admin():
        return render_template('admin.html', firebase_config=app.config['FIREBASE_CONFIG'])

    # Create tables on first run
    with app.app_context():
        db.create_all()
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
