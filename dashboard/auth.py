# dashboard/auth.py
"""Module xử lý xác thực tài khoản, kiểm tra hạn dùng và quyền hạn cho hệ thống Dashboard."""

import hashlib
import os
import sqlite3
import time
from typing import Optional, Dict, Any, List

# 📐 QUY HOẠCH ĐƯỜNG DẪN CHUẨN (Từ dashboard/ đi ra gốc rồi vào database/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.normpath(os.path.join(BASE_DIR, "..", "database", "db", "game_tu_tien.db"))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Đối chiếu mật khẩu người dùng nhập vào với mã băm trong DB."""
    current_hash = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
    return current_hash == hashed_password


def get_user_permissions(cursor: sqlite3.Cursor, user_id: int) -> List[str]:
    """Truy vấn danh sách các system_id mà user được phép truy cập quản trị."""
    cursor.execute(
        "SELECT system_id FROM sys_permissions WHERE user_id = ?;",
        (user_id,),
    )
    return [row[0] for row in cursor.fetchall()]


def check_username_available(username: str) -> bool:
    """Kiểm tra tên tài khoản đã tồn tại trong DB hay chưa (Dùng khi tạo mới account).

    Trả về True nếu chưa tồn tại (hợp lệ để tạo).
    Trả về False nếu đã tồn tại.
    """
    if not os.path.exists(DB_PATH):
        return False

    conn = sqlite3.connect(DB_PATH)
    user_cursor = conn.cursor()

    try:
        user_cursor.execute("SELECT 1 FROM sys_users WHERE username = ?;", (username,))
        row = user_cursor.fetchone()
        return row is None
    except sqlite3.Error as e:
        print(f"❌ Lỗi kiểm tra username khả dụng: {e}")
        return False
    finally:
        conn.close()


def authenticate_user(username: str, plain_password: str) -> Optional[Dict[str, Any]]:
    """Kiểm tra thông tin đăng nhập, check hạn dùng và bốc danh sách quyền hạn.

    Nếu đúng và còn hạn, trả về dict thông tin (id, username, role, allowed_systems).
    Nếu sai hoặc hết hạn, trả về None.
    """
    if not os.path.exists(DB_PATH):
        print(f"❌ Không tìm thấy file DB tại: {DB_PATH}")
        return None

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    auth_cursor = conn.cursor()

    try:
        # Bốc đầy đủ các cột phục vụ kiểm tra thời hạn
        auth_cursor.execute(
            "SELECT id, username, password_hash, role, expired_at FROM sys_users WHERE username = ?;",
            (username,),
        )
        user_row = auth_cursor.fetchone()

        if user_row and verify_password(plain_password, user_row["password_hash"]):
            # ⏳ KIỂM TRA THỜI HẠN TÀI KHOẢN (Nếu expired_at khác NULL và nhỏ hơn thời gian hiện tại)
            expired_at = user_row["expired_at"]
            if expired_at is not None and int(time.time()) > int(expired_at):
                print(f"⚠️ Tài khoản `{username}` đã hết hạn truy cập hệ thống!")
                return None

            # 🔑 BỐC DANH SÁCH ĐỊA BÀN ĐƯỢC PHÂN QUYỀN
            user_id = user_row["id"]
            allowed_systems = get_user_permissions(auth_cursor, user_id)

            return {
                "id": user_id,
                "username": user_row["username"],
                "role": user_row["role"],
                "allowed_systems": allowed_systems,
            }

    except sqlite3.Error as e:
        print(f"❌ Lỗi xảy ra trong quá trình xác thực tài khoản: {e}")
    finally:
        conn.close()

    return None

def get_all_game_systems() -> List[str]:
    """Tự động quét danh sách tất cả các bảng dữ liệu game hiện có trong DB.

    Loại trừ các bảng thuộc hệ thống quản trị (sys_ và wf_).
    """
    if not os.path.exists(DB_PATH):
        return []

    conn = sqlite3.connect(DB_PATH)
    systems_cursor = conn.cursor()

    try:
        # Quét tất cả các bảng game thực tế, bỏ qua bảng hệ thống quản trị và bảng mặc định của SQLite
        systems_cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table'
              AND name NOT LIKE 'sqlite_%'
              AND name NOT LIKE 'sys_%'
              AND name NOT LIKE 'wf_%';
        """)
        return [row[0] for row in systems_cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"❌ Lỗi quét danh sách hệ thống game: {e}")
        return []
    finally:
        conn.close()
