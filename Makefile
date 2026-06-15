# Định nghĩa các lệnh phím tắt giả lập
.PHONY: install format fix lint clean datagame-init dashboard-init web-run

# 1. Cài đặt các thư viện lõi + thư viện dev từ file pyproject.toml
install:
	pip install --upgrade pip
	pip install --editable .[dev] --config-settings editable_mode=compat

# 2. Tự động format căn lề, bẻ dòng theo chuẩn PEP8 bằng Ruff
format:
	ruff format

# 3. Lệnh "Thần Kỳ" - Tự động phát hiện và sửa các lỗi code vặt, sắp xếp import bằng Ruff
fix:
	ruff check --fix

# 4. Kiểm tra toàn diện lỗi PEP8 bằng Ruff (soi lỗi) và Pylint (soi logic)
lint:
	ruff check
	pylint src/ dashboard/ webui/ main.py

# 5. Combo "Dọn dẹp tối cao" - Tự động format, sửa lỗi vặt rồi chạy quét kiểm tra lại toàn bộ dự án
clean: format fix lint

# 6. Khởi tạo cấu trúc bảng và đồng bộ dữ liệu phôi từ CSV vào SQLite cho Data Game
datagame-init:
	PYTHONPATH=. python database/create_table_data_game_in_db.py
	PYTHONPATH=. python database/import_csv_to_db.py

# 7. Khởi tạo cấu trúc các bảng hệ thống, quản lý phân quyền, workflow và tài khoản root cho Dashboard
dashboard-init:
	PYTHONPATH=. python database/create_table_system_user_in_db.py

# 8. Khởi chạy Web Server FastAPI tập trung (Phục vụ chung cho cả Wiki hiển thị và API Dashboard)
web-run:
	uvicorn main:app --reload --host 127.0.0.1 --port 8000
