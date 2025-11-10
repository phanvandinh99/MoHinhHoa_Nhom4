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
🛠️ Công nghệ áp dụng
Ngôn ngữ
Python 3.8+
Web Framework
Flask
Cơ sở dữ liệu
MySQL 5.7+
ORM
SQLAlchemy
Giao diện
HTML + CSS + Bootstrap 5
Quản lý môi trường
python-dotenv
MySQL Driver
PyMySQL

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
**⚠️ BẮT BUỘC:** Tạo file `.env` trong thư mục gốc với nội dung sau:

**Cách 1: Tạo thủ công**
1. Tạo file mới tên `.env` trong thư mục `MoHinhHoa_Nhom4`
2. Copy nội dung sau vào file:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=academic_db
DB_PORT=3306
SECRET_KEY=dev-secret-key-change-in-production
FLASK_ENV=development
FLASK_DEBUG=True
```

**Cách 2: Dùng PowerShell**
```powershell
@"
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=academic_db
DB_PORT=3306
SECRET_KEY=dev-secret-key-change-in-production
FLASK_ENV=development
FLASK_DEBUG=True
"@ | Out-File -FilePath .env -Encoding utf8
```

**⚠️ QUAN TRỌNG:** 
- Thay `your_mysql_password` bằng mật khẩu MySQL thực tế của bạn
- Nếu MySQL không có mật khẩu, để trống: `DB_PASSWORD=`
- Đảm bảo database `academic_db` đã được tạo (đã chạy file `Database/data.sql`)

### 4. Chạy ứng dụng
**⚠️ QUAN TRỌNG:** Phải chạy từ **thư mục gốc** của dự án (không phải từ trong `academic_system`)

```bash
# Đảm bảo bạn đang ở thư mục gốc: MoHinhHoa_Nhom4
cd C:\Users\DINH\Desktop\MoHinhHoa_Nhom4

# Sau đó chạy
python app.py
```

Hoặc nếu đang ở trong thư mục `academic_system`, quay về thư mục gốc:
```bash
cd ..
python app.py
```

Ứng dụng sẽ chạy tại: `http://localhost:5000`

### 5. Tài khoản mẫu
- **Sinh viên:** `duc_anh` / `123`
- **Giảng viên:** `lecturer_a` / `123`
- **Quản trị viên:** `admin_main` / `123`

---

## 📁 Cấu trúc thư mục

```
MoHinhHoa_Nhom4/
├── academic_system/
│   ├── __init__.py          # Khởi tạo Flask app
│   ├── config.py            # Cấu hình database
│   ├── models.py            # SQLAlchemy models
│   ├── auth.py              # Authentication routes
│   ├── student/             # Module Sinh viên
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── lecturer/            # Module Giảng viên
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── admin/               # Module Quản trị viên
│   │   ├── __init__.py
│   │   └── routes.py
│   └── templates/           # HTML templates
│       ├── base.html
│       ├── auth/
│       ├── student/
│       ├── lecturer/
│       └── admin/
├── Database/
│   └── data.sql            # File SQL tạo database
├── app.py                  # File chạy ứng dụng
├── requirements.txt        # Dependencies
└── README.md
```

---

## ✨ Tính năng đã triển khai

### Sinh viên
- ✅ Đăng nhập/Đăng xuất
- ✅ Xem dashboard với thống kê
- ✅ Xem thời khóa biểu các lớp đang học
- ✅ Xem điểm số tất cả môn học
- ✅ Xem hồ sơ cá nhân

### Giảng viên
- ✅ Đăng nhập/Đăng xuất
- ✅ Xem dashboard với thống kê
- ✅ Xem danh sách lớp học phần được phân công
- ✅ Xem danh sách sinh viên trong lớp
- ✅ Nhập điểm cho sinh viên
- ✅ Xem báo cáo kết quả học tập của lớp
- ✅ Xem hồ sơ sinh viên

### Quản trị viên
- ✅ Đăng nhập/Đăng xuất
- ✅ Xem dashboard với thống kê tổng quan
- ✅ Quản lý sinh viên (thêm, sửa, vô hiệu hóa/kích hoạt)
- ✅ Quản lý giảng viên (thêm, sửa, vô hiệu hóa/kích hoạt)
- ✅ Quản lý môn học (thêm, sửa, xóa)
- ✅ Xem báo cáo tổng hợp toàn trường

---

## 🔒 Bảo mật

- Session-based authentication
- Role-based access control (RBAC)
- Password validation (cần cải thiện: hash password trong production)

---

## 📝 Lưu ý

- Mật khẩu hiện tại lưu dạng plain text (chỉ dùng cho development)
- Trong production, nên sử dụng password hashing (bcrypt, werkzeug.security)
- Cần cấu hình `.env` file với thông tin database chính xác
