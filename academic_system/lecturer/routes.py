from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from functools import wraps
from academic_system.models import db, Instructor, Section, Enrollment, Student, Course, Semester, Grade

lecturer_bp = Blueprint('lecturer', __name__)

def lecturer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'lecturer':
            flash('Bạn cần đăng nhập với tài khoản giảng viên', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@lecturer_bp.route('/')
@lecturer_bp.route('/dashboard')
@lecturer_required
def dashboard():
    instructor_id = session.get('instructor_id')
    if not instructor_id:
        flash('Không tìm thấy thông tin giảng viên', 'danger')
        return redirect(url_for('auth.login'))
    
    instructor = Instructor.query.get_or_404(instructor_id)
    
    # Lấy số lớp đang dạy
    sections_count = Section.query.filter_by(instructor_id=instructor_id).count()
    
    # Lấy số sinh viên đang dạy
    total_students = db.session.query(Enrollment).join(Section).filter(
        Section.instructor_id == instructor_id,
        Enrollment.status == 'active'
    ).count()
    
    return render_template('lecturer/dashboard.html',
                         instructor=instructor,
                         sections_count=sections_count,
                         total_students=total_students)

@lecturer_bp.route('/sections')
@lecturer_required
def sections():
    instructor_id = session.get('instructor_id')
    if not instructor_id:
        return redirect(url_for('auth.login'))
    
    sections_list = Section.query.filter_by(instructor_id=instructor_id)\
        .join(Course).join(Semester).all()
    
    return render_template('lecturer/sections.html', sections=sections_list)

@lecturer_bp.route('/section/<int:section_id>/students')
@lecturer_required
def section_students(section_id):
    instructor_id = session.get('instructor_id')
    section = Section.query.get_or_404(section_id)
    
    # Kiểm tra quyền
    if section.instructor_id != instructor_id:
        flash('Bạn không có quyền truy cập lớp này', 'danger')
        return redirect(url_for('lecturer.sections'))
    
    enrollments = Enrollment.query.filter_by(section_id=section_id).all()
    
    students_data = []
    for enrollment in enrollments:
        grade = Grade.query.filter_by(enrollment_id=enrollment.id).first()
        students_data.append({
            'enrollment': enrollment,
            'student': enrollment.student,
            'grade': grade
        })
    
    return render_template('lecturer/section_students.html',
                         section=section,
                         students_data=students_data)

@lecturer_bp.route('/section/<int:section_id>/grade/<int:enrollment_id>', methods=['GET', 'POST'])
@lecturer_required
def grade_student(section_id, enrollment_id):
    instructor_id = session.get('instructor_id')
    section = Section.query.get_or_404(section_id)
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    
    # Kiểm tra quyền
    if section.instructor_id != instructor_id or enrollment.section_id != section_id:
        flash('Bạn không có quyền thực hiện thao tác này', 'danger')
        return redirect(url_for('lecturer.sections'))
    
    if request.method == 'POST':
        score = request.form.get('score')
        grade_letter = request.form.get('grade_letter')
        
        if score:
            try:
                score_float = float(score)
                if score_float < 0 or score_float > 10:
                    flash('Điểm số phải từ 0 đến 10', 'danger')
                    return render_template('lecturer/grade_student.html',
                                         section=section,
                                         enrollment=enrollment)
            except ValueError:
                flash('Điểm số không hợp lệ', 'danger')
                return render_template('lecturer/grade_student.html',
                                     section=section,
                                     enrollment=enrollment)
            
            # Tìm hoặc tạo grade
            grade = Grade.query.filter_by(enrollment_id=enrollment_id).first()
            if grade:
                grade.score = score_float
                grade.grade_letter = grade_letter
                grade.submitted_by = instructor_id
            else:
                grade = Grade(
                    enrollment_id=enrollment_id,
                    score=score_float,
                    grade_letter=grade_letter,
                    submitted_by=instructor_id
                )
                db.session.add(grade)
            
            db.session.commit()
            flash('Nhập điểm thành công', 'success')
            return redirect(url_for('lecturer.section_students', section_id=section_id))
        else:
            flash('Vui lòng nhập điểm số', 'danger')
    
    grade = Grade.query.filter_by(enrollment_id=enrollment_id).first()
    return render_template('lecturer/grade_student.html',
                         section=section,
                         enrollment=enrollment,
                         grade=grade)

@lecturer_bp.route('/section/<int:section_id>/report')
@lecturer_required
def section_report(section_id):
    instructor_id = session.get('instructor_id')
    section = Section.query.get_or_404(section_id)
    
    # Kiểm tra quyền
    if section.instructor_id != instructor_id:
        flash('Bạn không có quyền truy cập lớp này', 'danger')
        return redirect(url_for('lecturer.sections'))
    
    enrollments = Enrollment.query.filter_by(section_id=section_id).all()
    
    # Thống kê
    total_students = len(enrollments)
    graded_count = 0
    total_score = 0
    grade_distribution = {'A': 0, 'B+': 0, 'B': 0, 'C+': 0, 'C': 0, 'D': 0, 'F': 0}
    
    for enrollment in enrollments:
        grade = Grade.query.filter_by(enrollment_id=enrollment.id).first()
        if grade and grade.score:
            graded_count += 1
            total_score += float(grade.score)
            if grade.grade_letter:
                grade_distribution[grade.grade_letter] = grade_distribution.get(grade.grade_letter, 0) + 1
    
    avg_score = total_score / graded_count if graded_count > 0 else 0
    
    return render_template('lecturer/section_report.html',
                         section=section,
                         enrollments=enrollments,
                         total_students=total_students,
                         graded_count=graded_count,
                         avg_score=round(avg_score, 2),
                         grade_distribution=grade_distribution)

@lecturer_bp.route('/student/<int:student_id>/profile')
@lecturer_required
def view_student_profile(student_id):
    student = Student.query.get_or_404(student_id)
    
    # Lấy tất cả điểm của sinh viên
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
    
    return render_template('lecturer/student_profile.html',
                         student=student,
                         grades_data=grades_data)

