-- --------------------------------------------------------
-- Student Academic Information Management System
-- --------------------------------------------------------

-- 1. Tạo và sử dụng CSDL
DROP DATABASE IF EXISTS academic_db;
CREATE DATABASE academic_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE academic_db;

-- 2. Bảng users: tài khoản hệ thống
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    role ENUM('student', 'lecturer', 'admin') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Bảng semesters: học kỳ
CREATE TABLE semesters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(20) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL
);

-- 4. Bảng courses: môn học
CREATE TABLE courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    credits INT NOT NULL,
    description TEXT
);

-- 5. Bảng students: thông tin sinh viên (nghiệp vụ)
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    student_code VARCHAR(20) NOT NULL UNIQUE,
    date_of_birth DATE,
    email VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,  -- ✅ Thêm: hỗ trợ deactivate
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 6. Bảng instructors: thông tin giảng viên (nghiệp vụ)
CREATE TABLE instructors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    instructor_code VARCHAR(20) NOT NULL UNIQUE,
    department VARCHAR(100),
    email VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,  -- ✅ Thêm: hỗ trợ deactivate
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 7. Bảng sections: lớp học phần
CREATE TABLE sections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    instructor_id INT NOT NULL,
    semester_id INT NOT NULL,
    section_code VARCHAR(10) NOT NULL,
    schedule_info VARCHAR(255),
    max_capacity INT DEFAULT 50,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (instructor_id) REFERENCES instructors(id) ON DELETE RESTRICT,
    FOREIGN KEY (semester_id) REFERENCES semesters(id) ON DELETE CASCADE,
    UNIQUE(course_id, section_code, semester_id)  -- ✅ Cải tiến: tránh xung đột mã lớp
);

-- 8. Bảng enrollments: đăng ký học
CREATE TABLE enrollments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    section_id INT NOT NULL,
    enroll_date DATE DEFAULT (CURRENT_DATE),
    status ENUM('active', 'dropped', 'completed') DEFAULT 'active',
    UNIQUE(student_id, section_id),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (section_id) REFERENCES sections(id) ON DELETE CASCADE
);

-- 9. Bảng grades: điểm số
CREATE TABLE grades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    enrollment_id INT NOT NULL UNIQUE,
    score DECIMAL(4,2),
    grade_letter VARCHAR(3),
    submitted_by INT NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (enrollment_id) REFERENCES enrollments(id) ON DELETE CASCADE,
    FOREIGN KEY (submitted_by) REFERENCES instructors(id) ON DELETE RESTRICT
);

-- ====================================================================
-- CHÈN DỮ LIỆU MẪU – ĐÃ CẬP NHẬT is_active = TRUE (mặc định)
-- ====================================================================

-- Bước 1: Users (12 tài khoản)
INSERT INTO users (username, password, role) VALUES
-- Sinh viên (5)
('duc_anh', '123', 'student'),
('ha_linh', '123', 'student'),
('phong_nguyen', '123', 'student'),
('linh_chi', '123', 'student'),
('minh_hieu', '123', 'student'),
-- Giảng viên (5)
('lecturer_a', '123', 'lecturer'),
('lecturer_b', '123', 'lecturer'),
('lecturer_c', '123', 'lecturer'),
('lecturer_d', '123', 'lecturer'),
('lecturer_e', '123', 'lecturer'),
-- Admin (2)
('admin_main', '123', 'admin'),
('admin_backup', '123', 'admin');

-- Bước 2: Semesters
INSERT INTO semesters (name, start_date, end_date) VALUES
('2025_1', '2025-08-01', '2025-12-15'),
('2024_2', '2025-01-10', '2025-05-30'),
('2024_1', '2024-08-05', '2024-12-20'),
('2023_2', '2024-01-08', '2024-05-25'),
('2023_1', '2023-08-07', '2023-12-18');

-- Bước 3: Courses
INSERT INTO courses (course_code, name, credits, description) VALUES
('CS101', 'Lập trình cơ bản', 3, 'Nhập môn lập trình với Python'),
('CS201', 'Cấu trúc dữ liệu', 3, 'Cấu trúc dữ liệu và giải thuật'),
('MATH202', 'Toán rời rạc', 3, 'Toán học cho khoa học máy tính'),
('ENG101', 'Tiếng Anh học thuật', 2, 'Kỹ năng đọc và viết học thuật'),
('PHYS101', 'Vật lý đại cương', 3, 'Cơ học và điện từ cơ bản');

-- Bước 4: Students (is_active mặc định TRUE)
INSERT INTO students (user_id, full_name, student_code, date_of_birth, email, is_active) VALUES
(1, 'DucAnh', 'SV2021001', '2003-05-12', 'ducanh@gmail.com', TRUE),
(2, 'HaLinh', 'SV2021002', '2003-08-22', 'halinh@gmail.com', TRUE),
(3, 'PhongNguyen', 'SV2021003', '2002-11-30', 'phongnguyen@gmail.com', TRUE),
(4, 'LinhCHi', 'SV2021004', '2004-01-15', 'linhchi@gmail.com', TRUE),
(5, 'MinhHieu', 'SV2021005', '2003-03-07', 'minhhieu@gmail.com', TRUE);

-- Bước 5: Instructors (is_active mặc định TRUE)
INSERT INTO instructors (user_id, full_name, instructor_code, department, email, is_active) VALUES
(6, 'Nguyen Huynh Duc', 'GV001', 'Công nghệ Thông tin', 'huynhduoc@gmail.com', TRUE),
(7, 'Tran Thi Thu Thao', 'GV002', 'Công nghệ Thông tin', 'tthao@gmail.com', TRUE),
(8, 'Le Quoc Cuong', 'GV003', 'Toán ứng dụng', 'lqc@gmail.com', TRUE),
(9, 'Pham Minh Chinh', 'GV004', 'Ngoại ngữ', 'pmchinh123@gmail.com', TRUE),
(10, 'Hoang Thu Trang', 'GV005', 'Vật lý', 'httrang111@gmail.com', TRUE);

-- Bước 6: Sections
INSERT INTO sections (course_id, instructor_id, semester_id, section_code, schedule_info, max_capacity) VALUES
(1, 1, 1, 'CS101-01', 'Thứ 2,4 - 7h-9h - Phòng A101', 40),
(2, 2, 1, 'CS201-01', 'Thứ 3,5 - 13h-15h - Phòng B202', 35),
(3, 3, 1, 'MATH202-01', 'Thứ 2,4 - 15h-17h - Phòng A103', 50),
(4, 4, 1, 'ENG101-01', 'Thứ 7 - 8h-11h - Phòng C301', 30),
(5, 5, 1, 'PHYS101-01', 'Thứ 3,5 - 8h-10h - Phòng A105', 45);

-- Bước 7: Enrollments
INSERT INTO enrollments (student_id, section_id) VALUES
(1, 1), (1, 2), (1, 3),
(2, 1), (2, 2), (2, 4), (2, 5),
(3, 1), (3, 3), (3, 4),
(4, 2), (4, 3), (4, 5),
(5, 1), (5, 4), (5, 5);

-- Bước 8: Grades
INSERT INTO grades (enrollment_id, score, grade_letter, submitted_by) VALUES
-- DucAnh
(1, 8.5, 'A', 1),
(2, 7.0, 'B+', 2),
(3, 9.0, 'A', 3),
-- HaLinh
(4, 7.5, 'B+', 1),
(5, 6.5, 'B', 2),
(6, 8.0, 'A', 4),
(7, 5.5, 'C+', 5),
-- PhongNguyen
(8, 9.2, 'A', 1),
(9, 8.0, 'A', 3),
(10, 7.8, 'B+', 4),
-- LinhCHi
(11, 6.0, 'B', 2),
(12, 8.5, 'A', 3),
(13, 7.2, 'B+', 5),
-- MinhHieu
(14, 5.0, 'C', 1),
(15, 8.8, 'A', 4),
(16, 6.8, 'B', 5);