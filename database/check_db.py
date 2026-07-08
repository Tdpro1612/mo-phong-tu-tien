# database/check_db.py
"""Script kiểm tra toàn bộ cấu trúc bảng và cột hiện có trong database."""

import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.normpath(os.path.join(BASE_DIR, "db", "game_tu_tien.db"))


def check_database_schema() -> None:
    """Quét và in ra danh sách bảng kèm cấu trúc cột chi tiết."""
    print("====== 📊 KIỂM TRA CẤU TRÚC CƠ SỞ DỮ LIỆU ======")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Không tìm thấy file database tại: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 1. Lấy danh sách tất cả các bảng (loại trừ các bảng hệ thống của SQLite)
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%';
        """)
        tables = [row[0] for row in cursor.fetchall()]

        if not tables:
            print("[!] Database đang trống rỗng, chưa có bảng nào.")
            return

        print(f"[🔥] Tìm thấy tổng cộng: {len(tables)} bảng.\n")

        # 2. Quét chi tiết từng bảng để lấy danh sách cột
        for table_name in tables:
            print(f"📘 BẢNG: `{table_name}`")
            print("-" * 50)
            
            # Lấy thông tin cột của bảng hiện tại
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            # Định dạng hiển thị: ID | Tên Cột | Kiểu Dữ Liệu | Không Null? | Giá Trị Mặc Định
            for col in columns:
                col_id = col[0]
                col_name = col[1]
                col_type = col[2] or "TEXT/BLOB"
                not_null = "NOT NULL" if col[3] == 1 else "NULL"
                default_val = f"DEFAULT: {col[4]}" if col[4] is not None else ""
                is_pk = "🔑 PK" if col[5] == 1 else ""

                print(f"  ↳ [{col_id}] {col_name:<18} | {col_type:<8} | {not_null:<8} | {default_val:<20} {is_pk}")
            print("\n")

    except sqlite3.Error as e:
        print(f"❌ Lỗi khi đọc schema: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    check_database_schema()