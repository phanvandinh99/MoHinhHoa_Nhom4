# Student Academic Information Management System

## 📌 Chức năng theo vai trò

### 👨‍🎓 Sinh viên
- Đăng nhập
- Xem thời khóa biểu
- Xem điểm số
- Xem hồ sơ cá nhân

### 👨‍🏫 Giảng viên
- Xem các lớp học phần được phân công
- Nhập điểm cho sinh viên
- Xem báo cáo kết quả học tập của lớp
- Xem hồ sơ sinh viên

### 👨‍💼 Quản trị viên
- Quản lý sinh viên (thêm, sửa, vô hiệu hóa)
- Quản lý giảng viên (thêm, sửa, vô hiệu hóa)
- Quản lý môn học
- Tạo báo cáo tổng hợp

---

## ▶️ Cách chạy dự án

### 1. Chuẩn bị cơ sở dữ liệu
Chạy file SQL đã cung cấp để tạo cơ sở dữ liệu `academic_db` và chèn dữ liệu mẫu:

### 2. Cài đặt môi trường Python
# Tạo môi trường ảo
python -m venv venv

# Kích hoạt môi trường
# Trên Windows:
venv\Scripts\activate
# Trên macOS/Linux:
source venv/bin/activate

# Cài thư viện cần thiết
pip install flask flask-sqlalchemy pymysql python-dotenv

### 3. Cấu hình kết nối cơ sở dữ liệu
