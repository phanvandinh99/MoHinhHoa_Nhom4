from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from functools import wraps
from academic_system.models import db, User, Student, Instructor, Course, Section, Enrollment, Grade, Semester, Attendance

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'admin':
            flash('Bạn cần đăng nhập với tài khoản quản trị viên', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    # Thống kê tổng quan
    total_students = Student.query.count()
    active_students = Student.query.filter_by(is_active=True).count()
    total_instructors = Instructor.query.count()
    active_instructors = Instructor.query.filter_by(is_active=True).count()
    total_courses = Course.query.count()
    total_sections = Section.query.count()
    
    return render_template('admin/dashboard.html',
                         total_students=total_students,
                         active_students=active_students,
                         total_instructors=total_instructors,
                         active_instructors=active_instructors,
                         total_courses=total_courses,
                         total_sections=total_sections)

# ========== QUẢN LÝ SINH VIÊN ==========
@admin_bp.route('/students')
@admin_required
def students():
    students_list = Student.query.join(User).all()
    return render_template('admin/students.html', students=students_list)

@admin_bp.route('/students/add', methods=['GET', 'POST'])
@admin_required
def add_student():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        student_code = request.form.get('student_code')
        date_of_birth = request.form.get('date_of_birth')
        email = request.form.get('email')
        
        if not all([username, password, full_name, student_code]):
            flash('Vui lòng điền đầy đủ thông tin bắt buộc', 'danger')
            return render_template('admin/add_student.html')
        
        # Kiểm tra username và student_code đã tồn tại
        if User.query.filter_by(username=username).first():
            flash('Tên đăng nhập đã tồn tại', 'danger')
            return render_template('admin/add_student.html')
        
        if Student.query.filter_by(student_code=student_code).first():
            flash('Mã sinh viên đã tồn tại', 'danger')
            return render_template('admin/add_student.html')
        
        # Tạo user
        user = User(username=username, password=password, role='student')
        db.session.add(user)
        db.session.flush()
        
        # Tạo student
        student = Student(
            user_id=user.id,
            full_name=full_name,
            student_code=student_code,
            date_of_birth=date_of_birth if date_of_birth else None,
            email=email if email else None,
            is_active=True
        )
        db.session.add(student)
        db.session.commit()
        
        flash('Thêm sinh viên thành công', 'success')
        return redirect(url_for('admin.students'))
    
    return render_template('admin/add_student.html')

@admin_bp.route('/students/<int:student_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)
    
    if request.method == 'POST':
        student.full_name = request.form.get('full_name')
        student.student_code = request.form.get('student_code')
        student.date_of_birth = request.form.get('date_of_birth') or None
        student.email = request.form.get('email') or None
        
        # Kiểm tra student_code trùng
        existing = Student.query.filter_by(student_code=student.student_code).first()
        if existing and existing.id != student_id:
            flash('Mã sinh viên đã tồn tại', 'danger')
            return render_template('admin/edit_student.html', student=student)
        
        db.session.commit()
        flash('Cập nhật thông tin sinh viên thành công', 'success')
        return redirect(url_for('admin.students'))
    
    return render_template('admin/edit_student.html', student=student)

@admin_bp.route('/students/<int:student_id>/toggle', methods=['POST'])
@admin_required
def toggle_student(student_id):
    student = Student.query.get_or_404(student_id)
    student.is_active = not student.is_active
    db.session.commit()
    
    status = 'kích hoạt' if student.is_active else 'vô hiệu hóa'
    flash(f'Đã {status} sinh viên thành công', 'success')
    return redirect(url_for('admin.students'))

# ========== QUẢN LÝ GIẢNG VIÊN ==========
@admin_bp.route('/instructors')
@admin_required
def instructors():
    instructors_list = Instructor.query.join(User).all()
    return render_template('admin/instructors.html', instructors=instructors_list)

@admin_bp.route('/instructors/add', methods=['GET', 'POST'])
@admin_required
def add_instructor():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        instructor_code = request.form.get('instructor_code')
        department = request.form.get('department')
        email = request.form.get('email')
        
        if not all([username, password, full_name, instructor_code]):
            flash('Vui lòng điền đầy đủ thông tin bắt buộc', 'danger')
            return render_template('admin/add_instructor.html')
        
        if User.query.filter_by(username=username).first():
            flash('Tên đăng nhập đã tồn tại', 'danger')
            return render_template('admin/add_instructor.html')
        
        if Instructor.query.filter_by(instructor_code=instructor_code).first():
            flash('Mã giảng viên đã tồn tại', 'danger')
            return render_template('admin/add_instructor.html')
        
        user = User(username=username, password=password, role='lecturer')
        db.session.add(user)
        db.session.flush()
        
        instructor = Instructor(
            user_id=user.id,
            full_name=full_name,
            instructor_code=instructor_code,
            department=department if department else None,
            email=email if email else None,
            is_active=True
        )
        db.session.add(instructor)
        db.session.commit()
        
        flash('Thêm giảng viên thành công', 'success')
        return redirect(url_for('admin.instructors'))
    
    return render_template('admin/add_instructor.html')

@admin_bp.route('/instructors/<int:instructor_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_instructor(instructor_id):
    instructor = Instructor.query.get_or_404(instructor_id)
    
    if request.method == 'POST':
        instructor.full_name = request.form.get('full_name')
        instructor.instructor_code = request.form.get('instructor_code')
        instructor.department = request.form.get('department') or None
        instructor.email = request.form.get('email') or None
        
        existing = Instructor.query.filter_by(instructor_code=instructor.instructor_code).first()
        if existing and existing.id != instructor_id:
            flash('Mã giảng viên đã tồn tại', 'danger')
            return render_template('admin/edit_instructor.html', instructor=instructor)
        
        db.session.commit()
        flash('Cập nhật thông tin giảng viên thành công', 'success')
        return redirect(url_for('admin.instructors'))
    
    return render_template('admin/edit_instructor.html', instructor=instructor)

@admin_bp.route('/instructors/<int:instructor_id>/toggle', methods=['POST'])
@admin_required
def toggle_instructor(instructor_id):
    instructor = Instructor.query.get_or_404(instructor_id)
    instructor.is_active = not instructor.is_active
    db.session.commit()
    
    status = 'kích hoạt' if instructor.is_active else 'vô hiệu hóa'
    flash(f'Đã {status} giảng viên thành công', 'success')
    return redirect(url_for('admin.instructors'))

# ========== QUẢN LÝ MÔN HỌC ==========
@admin_bp.route('/courses')
@admin_required
def courses():
    courses_list = Course.query.all()
    return render_template('admin/courses.html', courses=courses_list)

@admin_bp.route('/courses/add', methods=['GET', 'POST'])
@admin_required
def add_course():
    if request.method == 'POST':
        course_code = request.form.get('course_code')
        name = request.form.get('name')
        credits = request.form.get('credits')
        description = request.form.get('description')
        
        if not all([course_code, name, credits]):
            flash('Vui lòng điền đầy đủ thông tin bắt buộc', 'danger')
            return render_template('admin/add_course.html')
        
        if Course.query.filter_by(course_code=course_code).first():
            flash('Mã môn học đã tồn tại', 'danger')
            return render_template('admin/add_course.html')
        
        try:
            credits_int = int(credits)
        except ValueError:
            flash('Số tín chỉ không hợp lệ', 'danger')
            return render_template('admin/add_course.html')
        
        course = Course(
            course_code=course_code,
            name=name,
            credits=credits_int,
            description=description if description else None
        )
        db.session.add(course)
        db.session.commit()
        
        flash('Thêm môn học thành công', 'success')
        return redirect(url_for('admin.courses'))
    
    return render_template('admin/add_course.html')

@admin_bp.route('/courses/<int:course_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        course.course_code = request.form.get('course_code')
        course.name = request.form.get('name')
        course.credits = int(request.form.get('credits'))
        course.description = request.form.get('description') or None
        
        existing = Course.query.filter_by(course_code=course.course_code).first()
        if existing and existing.id != course_id:
            flash('Mã môn học đã tồn tại', 'danger')
            return render_template('admin/edit_course.html', course=course)
        
        db.session.commit()
        flash('Cập nhật môn học thành công', 'success')
        return redirect(url_for('admin.courses'))
    
    return render_template('admin/edit_course.html', course=course)

@admin_bp.route('/courses/<int:course_id>/delete', methods=['POST'])
@admin_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    # Kiểm tra xem có lớp học phần nào đang sử dụng môn học này không
    if Section.query.filter_by(course_id=course_id).first():
        flash('Không thể xóa môn học vì đang có lớp học phần sử dụng', 'danger')
        return redirect(url_for('admin.courses'))
    
    db.session.delete(course)
    db.session.commit()
    flash('Xóa môn học thành công', 'success')
    return redirect(url_for('admin.courses'))

# ========== QUẢN LÝ LỚP HỌC PHẦN (PHÂN BỔ GIẢNG VIÊN) ==========
@admin_bp.route('/sections')
@admin_required
def sections():
    sections_list = Section.query.join(Course).join(Instructor).join(Semester).all()
    return render_template('admin/sections.html', sections=sections_list)

@admin_bp.route('/sections/add', methods=['GET', 'POST'])
@admin_required
def add_section():
    if request.method == 'POST':
        course_id = request.form.get('course_id')
        instructor_id = request.form.get('instructor_id')
        semester_id = request.form.get('semester_id')
        section_code = request.form.get('section_code')
        schedule_info = request.form.get('schedule_info')
        max_capacity = request.form.get('max_capacity')
        
        if not all([course_id, instructor_id, semester_id, section_code, max_capacity]):
            flash('Vui lòng điền đầy đủ thông tin bắt buộc', 'danger')
            courses = Course.query.all()
            instructors = Instructor.query.filter_by(is_active=True).all()
            semesters = Semester.query.all()
            return render_template('admin/add_section.html',
                                 courses=courses,
                                 instructors=instructors,
                                 semesters=semesters)
        
        # Kiểm tra section_code đã tồn tại trong cùng học kỳ và môn học
        existing = Section.query.filter_by(
            course_id=course_id,
            section_code=section_code,
            semester_id=semester_id
        ).first()
        
        if existing:
            flash('Mã lớp học phần đã tồn tại cho môn học này trong học kỳ này', 'danger')
            courses = Course.query.all()
            instructors = Instructor.query.filter_by(is_active=True).all()
            semesters = Semester.query.all()
            return render_template('admin/add_section.html',
                                 courses=courses,
                                 instructors=instructors,
                                 semesters=semesters)
        
        try:
            max_capacity_int = int(max_capacity)
        except ValueError:
            flash('Sức chứa không hợp lệ', 'danger')
            courses = Course.query.all()
            instructors = Instructor.query.filter_by(is_active=True).all()
            semesters = Semester.query.all()
            return render_template('admin/add_section.html',
                                 courses=courses,
                                 instructors=instructors,
                                 semesters=semesters)
        
        section = Section(
            course_id=int(course_id),
            instructor_id=int(instructor_id),
            semester_id=int(semester_id),
            section_code=section_code,
            schedule_info=schedule_info if schedule_info else None,
            max_capacity=max_capacity_int
        )
        db.session.add(section)
        db.session.commit()
        
        flash('Tạo lớp học phần và phân bổ giảng viên thành công', 'success')
        return redirect(url_for('admin.sections'))
    
    courses = Course.query.all()
    instructors = Instructor.query.filter_by(is_active=True).all()
    semesters = Semester.query.all()
    return render_template('admin/add_section.html',
                         courses=courses,
                         instructors=instructors,
                         semesters=semesters)

@admin_bp.route('/sections/<int:section_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_section(section_id):
    section = Section.query.get_or_404(section_id)
    
    if request.method == 'POST':
        section.course_id = int(request.form.get('course_id'))
        section.instructor_id = int(request.form.get('instructor_id'))
        section.semester_id = int(request.form.get('semester_id'))
        section.section_code = request.form.get('section_code')
        section.schedule_info = request.form.get('schedule_info') or None
        section.max_capacity = int(request.form.get('max_capacity'))
        
        # Kiểm tra section_code trùng
        existing = Section.query.filter_by(
            course_id=section.course_id,
            section_code=section.section_code,
            semester_id=section.semester_id
        ).first()
        
        if existing and existing.id != section_id:
            flash('Mã lớp học phần đã tồn tại', 'danger')
            courses = Course.query.all()
            instructors = Instructor.query.filter_by(is_active=True).all()
            semesters = Semester.query.all()
            return render_template('admin/edit_section.html',
                                 section=section,
                                 courses=courses,
                                 instructors=instructors,
                                 semesters=semesters)
        
        db.session.commit()
        flash('Cập nhật lớp học phần thành công', 'success')
        return redirect(url_for('admin.sections'))
    
    courses = Course.query.all()
    instructors = Instructor.query.filter_by(is_active=True).all()
    semesters = Semester.query.all()
    return render_template('admin/edit_section.html',
                         section=section,
                         courses=courses,
                         instructors=instructors,
                         semesters=semesters)

@admin_bp.route('/sections/<int:section_id>/delete', methods=['POST'])
@admin_required
def delete_section(section_id):
    section = Section.query.get_or_404(section_id)
    
    # Kiểm tra xem có sinh viên nào đang học không
    if Enrollment.query.filter_by(section_id=section_id, status='active').first():
        flash('Không thể xóa lớp học phần vì đang có sinh viên đăng ký', 'danger')
        return redirect(url_for('admin.sections'))
    
    db.session.delete(section)
    db.session.commit()
    flash('Xóa lớp học phần thành công', 'success')
    return redirect(url_for('admin.sections'))

# ========== BÁO CÁO TỔNG HỢP ==========
@admin_bp.route('/reports')
@admin_required
def reports():
    # Thống kê tổng hợp
    total_students = Student.query.count()
    total_instructors = Instructor.query.count()
    total_courses = Course.query.count()
    total_sections = Section.query.count()
    total_enrollments = Enrollment.query.filter_by(status='active').count()
    
    # Điểm trung bình toàn trường
    grades = Grade.query.all()
    avg_score = 0
    if grades:
        total = sum(float(g.score) for g in grades if g.score)
        avg_score = total / len(grades)
    
    # Phân bố điểm
    grade_distribution = {'A': 0, 'B+': 0, 'B': 0, 'C+': 0, 'C': 0, 'D': 0, 'F': 0}
    for grade in grades:
        if grade.grade_letter:
            grade_distribution[grade.grade_letter] = grade_distribution.get(grade.grade_letter, 0) + 1
    
    return render_template('admin/reports.html',
                         total_students=total_students,
                         total_instructors=total_instructors,
                         total_courses=total_courses,
                         total_sections=total_sections,
                         total_enrollments=total_enrollments,
                         avg_score=round(avg_score, 2),
                         grade_distribution=grade_distribution)

@admin_bp.route('/attendance')
@admin_required
def attendance():
    # Lấy tất cả các lớp học phần
    sections = Section.query.join(Course).join(Semester).join(Instructor).all()
    
    # Thống kê điểm danh cho mỗi lớp
    sections_attendance = []
    for section in sections:
        # Lấy số sinh viên đã đăng ký
        enrollments_count = Enrollment.query.filter_by(
            section_id=section.id,
            status='active'
        ).count()
        
        # Lấy số buổi đã điểm danh
        attendances = Attendance.query.filter_by(section_id=section.id).all()
        sessions_marked = len(set((att.session_number for att in attendances)))
        
        # Tính tỷ lệ điểm danh
        total_possible = enrollments_count * section.total_sessions
        total_marked = len(attendances)
        attendance_percentage = (total_marked / total_possible * 100) if total_possible > 0 else 0
        
        sections_attendance.append({
            'section': section,
            'enrollments_count': enrollments_count,
            'sessions_marked': sessions_marked,
            'total_sessions': section.total_sessions,
            'attendance_percentage': round(attendance_percentage, 1),
            'total_marked': total_marked
        })
    
    return render_template('admin/attendance.html',
                         sections_attendance=sections_attendance)

@admin_bp.route('/attendance/section/<int:section_id>')
@admin_required
def section_attendance_detail(section_id):
    section = Section.query.get_or_404(section_id)
    
    # Lấy tất cả sinh viên đã đăng ký
    enrollments = Enrollment.query.filter_by(
        section_id=section_id,
        status='active'
    ).all()
    
    # Lấy tất cả điểm danh
    attendances = Attendance.query.filter_by(section_id=section_id).all()
    
    # Tạo dictionary để dễ truy cập
    attendance_dict = {}
    for att in attendances:
        key = (att.enrollment_id, att.session_number)
        attendance_dict[key] = att
    
    # Tổng hợp thống kê điểm danh cho mỗi sinh viên
    students_attendance = []
    for enrollment in enrollments:
        present_count = 0
        absent_count = 0
        late_count = 0
        excused_count = 0
        
        # Tạo bảng điểm danh chi tiết
        session_details = []
        for session_num in range(1, section.total_sessions + 1):
            key = (enrollment.id, session_num)
            if key in attendance_dict:
                att = attendance_dict[key]
                session_details.append({
                    'session_number': session_num,
                    'status': att.status,
                    'date': att.attendance_date,
                    'notes': att.notes
                })
                if att.status == 'present':
                    present_count += 1
                elif att.status == 'absent':
                    absent_count += 1
                elif att.status == 'late':
                    late_count += 1
                elif att.status == 'excused':
                    excused_count += 1
            else:
                session_details.append({
                    'session_number': session_num,
                    'status': None,
                    'date': None,
                    'notes': None
                })
        
        attendance_rate = (present_count / section.total_sessions * 100) if section.total_sessions > 0 else 0
        
        students_attendance.append({
            'enrollment': enrollment,
            'student': enrollment.student,
            'present_count': present_count,
            'absent_count': absent_count,
            'late_count': late_count,
            'excused_count': excused_count,
            'attendance_rate': round(attendance_rate, 1),
            'session_details': session_details
        })
    
    return render_template('admin/section_attendance_detail.html',
                         section=section,
                         students_attendance=students_attendance,
                         total_sessions=section.total_sessions)

