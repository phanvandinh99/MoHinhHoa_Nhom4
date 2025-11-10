from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from academic_system.models import db, User, Student, Instructor

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Vui lòng nhập đầy đủ thông tin', 'danger')
            return render_template('auth/login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:  # Đơn giản hóa, trong thực tế nên hash password
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            
            # Lấy thông tin bổ sung theo role
            if user.role == 'student':
                student = Student.query.filter_by(user_id=user.id).first()
                if student:
                    session['student_id'] = student.id
                    session['full_name'] = student.full_name
                return redirect(url_for('student.dashboard'))
            elif user.role == 'lecturer':
                instructor = Instructor.query.filter_by(user_id=user.id).first()
                if instructor:
                    session['instructor_id'] = instructor.id
                    session['full_name'] = instructor.full_name
                return redirect(url_for('lecturer.dashboard'))
            elif user.role == 'admin':
                session['full_name'] = 'Administrator'
                return redirect(url_for('admin.dashboard'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Đã đăng xuất thành công', 'info')
    return redirect(url_for('auth.login'))

