from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum('student', 'lecturer', 'admin'), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref='user', uselist=False, cascade='all, delete-orphan')
    instructor = db.relationship('Instructor', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'

class Semester(db.Model):
    __tablename__ = 'semesters'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    
    sections = db.relationship('Section', backref='semester', lazy=True)
    
    def __repr__(self):
        return f'<Semester {self.name}>'

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    
    sections = db.relationship('Section', backref='course', lazy=True)
    
    def __repr__(self):
        return f'<Course {self.course_code}>'

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    student_code = db.Column(db.String(20), unique=True, nullable=False)
    date_of_birth = db.Column(db.Date)
    email = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    
    enrollments = db.relationship('Enrollment', backref='student', lazy=True)
    
    def __repr__(self):
        return f'<Student {self.student_code}>'

class Instructor(db.Model):
    __tablename__ = 'instructors'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    instructor_code = db.Column(db.String(20), unique=True, nullable=False)
    department = db.Column(db.String(100))
    email = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    
    sections = db.relationship('Section', backref='instructor', lazy=True)
    
    def __repr__(self):
        return f'<Instructor {self.instructor_code}>'

class Section(db.Model):
    __tablename__ = 'sections'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructors.id'), nullable=False)
    semester_id = db.Column(db.Integer, db.ForeignKey('semesters.id'), nullable=False)
    section_code = db.Column(db.String(10), nullable=False)
    schedule_info = db.Column(db.String(255))
    max_capacity = db.Column(db.Integer, default=50)
    
    enrollments = db.relationship('Enrollment', backref='section', lazy=True)
    
    __table_args__ = (
        db.UniqueConstraint('course_id', 'section_code', 'semester_id', name='unique_section'),
    )
    
    def __repr__(self):
        return f'<Section {self.section_code}>'

class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)
    enroll_date = db.Column(db.Date, default=datetime.utcnow)
    status = db.Column(db.Enum('active', 'dropped', 'completed'), default='active')
    
    grade = db.relationship('Grade', backref='enrollment', uselist=False, cascade='all, delete-orphan')
    
    __table_args__ = (
        db.UniqueConstraint('student_id', 'section_id', name='unique_enrollment'),
    )
    
    def __repr__(self):
        return f'<Enrollment {self.id}>'

class Grade(db.Model):
    __tablename__ = 'grades'
    
    id = db.Column(db.Integer, primary_key=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollments.id'), unique=True, nullable=False)
    score = db.Column(db.Numeric(4, 2))
    grade_letter = db.Column(db.String(3))
    submitted_by = db.Column(db.Integer, db.ForeignKey('instructors.id'), nullable=False)
    submitted_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Grade {self.id}>'

