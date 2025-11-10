from flask import Flask, session, redirect, url_for
from academic_system.config import Config
from academic_system.models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    # Import và đăng ký blueprints
    from academic_system.auth import auth_bp
    from academic_system.student.routes import student_bp
    from academic_system.lecturer.routes import lecturer_bp
    from academic_system.admin.routes import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(lecturer_bp, url_prefix='/lecturer')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    @app.route('/')
    def index():
        if 'user_id' in session:
            role = session.get('role')
            if role == 'student':
                return redirect(url_for('student.dashboard'))
            elif role == 'lecturer':
                return redirect(url_for('lecturer.dashboard'))
            elif role == 'admin':
                return redirect(url_for('admin.dashboard'))
        return redirect(url_for('auth.login'))
    
    return app

