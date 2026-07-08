# database/init_system_db.py
"""Script khởi tạo và tự động nâng cấp các bảng quản trị hệ thống Dashboard.

Vị trí: Quy hoạch tập trung trong folder database/
Bảo toàn hoàn toàn dữ liệu của các bảng game khác khi chạy lại.
"""

import hashlib
import os
import sqlite3
from database_utils import parse_file_md_schema
from database_manager import create_a_table

# 📐 QUY HOẠCH ĐƯỜNG DẪN CHUẨN
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "sys_templates")
DB_PATH = os.path.normpath(os.path.join(BASE_DIR, "db", "game_tu_tien.db"))


def hash_password(password: str) -> str:
    """Hàm băm mật khẩu đơn giản bằng SHA-256 để lưu vào DB bảo mật."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def init_dashboard_system() -> None:
    """Khởi tạo cấu trúc bảng quản trị, tự động bổ dung cột an toàn nếu đã tồn tại DB."""
    print("====== 🛡️ KHỞI TẠO & KIỂM TRA HỆ THỐNG CƠ SỞ DỮ LIỆU DASHBOARD ======")

    if not os.path.exists(TEMPLATE_DIR):
        print(f"❌ Không tìm thấy thư mục template tại: {TEMPLATE_DIR}")
        return

    # Tự động tạo thư mục 'db' nếu chưa có để tránh lỗi SQLite không tìm thấy đường dẫn file
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    print(f"🔮 Đang quét các file cấu trúc từ: {TEMPLATE_DIR}")
    print("✨ Gọi hàm core kết hợp để tự động khởi tạo hệ thống bảng...")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    count = 0

    # Duyệt qua các file template .md
    for file_name in os.listdir(TEMPLATE_DIR):
        if file_name.endswith(".md"):
            file_path = os.path.join(TEMPLATE_DIR, file_name)

            try:
                # 1. Gọi hàm util dùng chung để lấy cục dữ liệu schema sạch từ file .md
                schema_data = parse_file_md_schema(file_path)

                table_name = schema_data.get("id_he_thong")
                cac_cot_du_lieu = schema_data.get("cac_cot_du_lieu")

                if not table_name or not cac_cot_du_lieu:
                    print(f"⚠️ Bỏ qua {file_name}: Cấu trúc front matter thiếu trường cốt lõi.")
                    continue

                # 2. Gọi trực tiếp hàm create_a_table xịn của bạn để tạo bảng
                if create_a_table(cursor, table_name, cac_cot_du_lieu):
                    count += 1

            except Exception as e:
                print(f"❌ Lỗi khi xử lý file {file_name}: {e}")

    conn.commit()
    conn.close()

    print(f"\n🎉 Đại công cáo thành! Đã khởi tạo xong {count} bảng tại: {DB_PATH}")


def create_account_rootdev() -> None:
    """Tạo tài khoản rootdev mặc định nếu chưa tồn tại.
    
    Tự động map đúng tên cột dựa theo file cấu hình sys_users.md để tránh lỗi lệch tên trường.
    """
    # Tìm file cấu hình của sys_users để bóc tên cột chuẩn
    sys_users_md = os.path.join(TEMPLATE_DIR, "sys_users.md")
    if not os.path.exists(sys_users_md):
        print("⚠️ Không tìm thấy file template 'sys_users.md'. Bỏ qua bước tạo tài khoản root.")
        return

    try:
        schema_data = parse_file_md_schema(sys_users_md)
        cac_cot = schema_data.get("cac_cot_du_lieu", [])
        
        # Bốc tên cột thực tế (Cột index 1 là username, index 2 là password)
        # Đề phòng trường hợp bạn đặt tiếng Anh (username/password_hash) hoặc tiếng Việt (ten_dang_nhap/mat_khau)
        col_username = list(cac_cot[1].keys())[0]
        col_password = list(cac_cot[2].keys())[0]
        col_role = list(cac_cot[3].keys())[0] if len(cac_cot) > 3 else None
    except Exception as e:
        print(f"❌ Không thể đọc cấu trúc trường của sys_users để tạo acc: {e}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Kiểm tra xem bảng quản trị có tồn tại không
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sys_users';")
    if cursor.fetchone() is None:
        print("⚠️ Bảng 'sys_users' chưa tồn tại. Vui lòng khởi tạo hệ thống trước.")
        conn.close()
        return

    # Kiểm tra xem tài khoản rootdev đã tồn tại chưa bằng cột động vừa lấy
    cursor.execute(f"SELECT * FROM sys_users WHERE {col_username} = ?", ("rootdev",))
    if cursor.fetchone() is not None:
        print("ℹ️ Tài khoản 'rootdev' đã tồn tại. Không cần tạo lại.")
        conn.close()
        return

    # Tạo tài khoản rootdev với mật khẩu mặc định
    mat_khau_bam = hash_password("dev2026@")
    try:
        cursor.execute(
            f"INSERT INTO sys_users ({col_username}, {col_password}, {col_role}) VALUES (?, ?, ?)",
            ("rootdev", mat_khau_bam, "root")
        )
        conn.commit()
        print(f"✅ Tài khoản 'rootdev' đã được tạo thành công với mật khẩu mặc định 'dev2026@'.")
    except sqlite3.Error as e:
        print(f"❌ Lỗi ghi tài khoản rootdev vào DB: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    # Bước 1: Khởi tạo tất cả các bảng trống hệ thống
    init_dashboard_system()
    
    # Bước 2: Điền tài khoản Admin tối cao vào sảnh
    create_account_rootdev()