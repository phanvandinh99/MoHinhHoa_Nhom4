from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from functools import wraps
from academic_system.models import db, Student, Enrollment, Section, Course, Semester, Grade
from datetime import datetime

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

@student_bp.route('/enroll')
@student_required
def enroll():
    student_id = session.get('student_id')
    if not student_id:
        return redirect(url_for('auth.login'))
    
    # Lấy học kỳ hiện tại (giả sử là học kỳ đầu tiên trong danh sách)
    current_semester = Semester.query.order_by(Semester.id.desc()).first()
    
    if not current_semester:
        flash('Chưa có học kỳ nào trong hệ thống', 'warning')
        return redirect(url_for('student.dashboard'))
    
    # Lấy tất cả lớp học phần của học kỳ hiện tại
    sections = Section.query.filter_by(semester_id=current_semester.id)\
        .join(Course).join(Semester).all()
    
    # Lấy các lớp đã đăng ký của sinh viên
    enrolled_section_ids = [e.section_id for e in Enrollment.query.filter_by(
        student_id=student_id,
        status='active'
    ).all()]
    
    # Thêm thông tin số lượng đã đăng ký và còn trống
    sections_data = []
    for section in sections:
        enrolled_count = Enrollment.query.filter_by(
            section_id=section.id,
            status='active'
        ).count()
        is_enrolled = section.id in enrolled_section_ids
        available = section.max_capacity - enrolled_count
        
        sections_data.append({
            'section': section,
            'enrolled_count': enrolled_count,
            'available': available,
            'is_enrolled': is_enrolled,
            'is_full': available <= 0
        })
    
    return render_template('student/enroll.html',
                         sections_data=sections_data,
                         current_semester=current_semester)

@student_bp.route('/enroll/<int:section_id>', methods=['POST'])
@student_required
def enroll_section(section_id):
    student_id = session.get('student_id')
    if not student_id:
        return redirect(url_for('auth.login'))
    
    section = Section.query.get_or_404(section_id)
    student = Student.query.get_or_404(student_id)
    
    # Kiểm tra đã đăng ký chưa
    existing = Enrollment.query.filter_by(
        student_id=student_id,
        section_id=section_id
    ).first()
    
    if existing:
        if existing.status == 'active':
            flash('Bạn đã đăng ký lớp này rồi', 'warning')
        else:
            existing.status = 'active'
            existing.enroll_date = datetime.utcnow().date()
            db.session.commit()
            flash('Đăng ký lại thành công', 'success')
        return redirect(url_for('student.enroll'))
    
    # Kiểm tra lớp còn chỗ không
    enrolled_count = Enrollment.query.filter_by(
        section_id=section_id,
        status='active'
    ).count()
    
    if enrolled_count >= section.max_capacity:
        flash('Lớp học đã đầy, không thể đăng ký', 'danger')
        return redirect(url_for('student.enroll'))
    
    # Tạo enrollment mới
    enrollment = Enrollment(
        student_id=student_id,
        section_id=section_id,
        status='active',
        enroll_date=datetime.utcnow().date()
    )
    db.session.add(enrollment)
    db.session.commit()
    
    flash(f'Đăng ký lớp {section.section_code} thành công!', 'success')
    return redirect(url_for('student.enroll'))

@student_bp.route('/enroll/<int:section_id>/drop', methods=['POST'])
@student_required
def drop_section(section_id):
    student_id = session.get('student_id')
    if not student_id:
        return redirect(url_for('auth.login'))
    
    enrollment = Enrollment.query.filter_by(
        student_id=student_id,
        section_id=section_id,
        status='active'
    ).first()
    
    if not enrollment:
        flash('Không tìm thấy đăng ký này', 'danger')
        return redirect(url_for('student.enroll'))
    
    enrollment.status = 'dropped'
    db.session.commit()
    
    flash('Hủy đăng ký thành công', 'success')
    return redirect(url_for('student.enroll'))

