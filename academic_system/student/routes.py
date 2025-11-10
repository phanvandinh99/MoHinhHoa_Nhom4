from flask import Blueprint, render_template, session, redirect, url_for, flash
from functools import wraps
from academic_system.models import db, Student, Enrollment, Section, Course, Semester, Grade

student_bp = Blueprint('student', __name__)

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'student':
            flash('Bạn cần đăng nhập với tài khoản sinh viên', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@student_bp.route('/')
@student_bp.route('/dashboard')
@student_required
def dashboard():
    student_id = session.get('student_id')
    if not student_id:
        flash('Không tìm thấy thông tin sinh viên', 'danger')
        return redirect(url_for('auth.login'))
    
    student = Student.query.get_or_404(student_id)
    
    # Lấy số lớp đang học
    active_enrollments = Enrollment.query.filter_by(
        student_id=student_id, 
        status='active'
    ).count()
    
    # Lấy điểm trung bình
    grades = db.session.query(Grade).join(Enrollment).filter(
        Enrollment.student_id == student_id
    ).all()
    
    avg_score = 0
    if grades:
        total = sum(float(g.score) for g in grades if g.score)
        avg_score = total / len(grades)
    
    return render_template('student/dashboard.html', 
                         student=student,
                         active_enrollments=active_enrollments,
                         avg_score=round(avg_score, 2))

@student_bp.route('/schedule')
@student_required
def schedule():
    student_id = session.get('student_id')
    if not student_id:
        return redirect(url_for('auth.login'))
    
    # Lấy tất cả các lớp đang học
    enrollments = Enrollment.query.filter_by(
        student_id=student_id,
        status='active'
    ).join(Section).join(Course).join(Semester).all()
    
    return render_template('student/schedule.html', enrollments=enrollments)

@student_bp.route('/grades')
@student_required
def grades():
    student_id = session.get('student_id')
    if not student_id:
        return redirect(url_for('auth.login'))
    
    # Lấy tất cả điểm số
    enrollments = Enrollment.query.filter_by(student_id=student_id).all()
    
    grades_data = []
    for enrollment in enrollments:
        grade = Grade.query.filter_by(enrollment_id=enrollment.id).first()
        grades_data.append({
            'enrollment': enrollment,
            'grade': grade,
            'course': enrollment.section.course,
            'section': enrollment.section,
            'semester': enrollment.section.semester
        })
    
    return render_template('student/grades.html', grades_data=grades_data)

@student_bp.route('/profile')
@student_required
def profile():
    student_id = session.get('student_id')
    if not student_id:
        return redirect(url_for('auth.login'))
    
    student = Student.query.get_or_404(student_id)
    return render_template('student/profile.html', student=student)

