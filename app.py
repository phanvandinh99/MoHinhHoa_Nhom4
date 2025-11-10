from academic_system import create_app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        from academic_system.models import db
        # Tạo bảng nếu chưa có (không cần thiết nếu đã chạy SQL)
        # db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)

