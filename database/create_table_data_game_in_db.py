import os
import sqlite3

import frontmatter

# LẤY ĐƯỜNG DẪN TUYỆT ĐỐI CỦA THƯ MỤC 'database' NƠI FILE SCRIPT NÀY ĐANG ĐỨNG
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Các thành phần đều nằm nội bộ bên trong thư mục 'database'
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
DB_PATH = os.path.join(BASE_DIR, "game_tu_tien.db")


def parse_template_to_sql(file_path):
    """Đọc file .md, bóc tách front matter để tạo câu lệnh SQL CREATE TABLE tự động."""
    with open(file_path, "r", encoding="utf-8") as f:
        post = frontmatter.load(f)

    # 1. Lấy tên bảng từ id_he_thong
    table_name = post.get("id_he_thong")
    if not table_name:
        return None

    # 2. Bóc tách danh sách các cột
    columns_config = post.get("cac_cot_du_lieu")
    if not columns_config or not isinstance(columns_config, list):
        print(
            f"⚠️ Bỏ qua {os.path.basename(file_path)}: 'cac_cot_du_lieu' không hợp lệ."
        )
        return None

    # 3. Tiến hành build chuỗi câu lệnh SQL
    sql_columns = []
    for col_dict in columns_config:
        for col_name, col_type in col_dict.items():
            col_name_clean = col_name.strip()

            # Thiết lập khóa chính cho cột STT
            if col_name_clean.lower() == "stt":
                sql_columns.append(f"{col_name_clean} INTEGER PRIMARY KEY")
            else:
                sql_columns.append(f"{col_name_clean} {col_type}")

    columns_sql_str = ", \n  ".join(sql_columns)

    create_table_query = f"""
  CREATE TABLE IF NOT EXISTS {table_name} (
    {columns_sql_str}
  );
  """
    return table_name, create_table_query


def khoi_tao_database():
    if not os.path.exists(TEMPLATE_DIR):
        print(f"❌ Không tìm thấy thư mục template tại: {TEMPLATE_DIR}")
        return

    print(f"🔮 Đang đọc các file hệ thống từ: {TEMPLATE_DIR}")
    print("✨ Bắt đầu bóc tách Front Matter để khởi tạo cấu trúc bảng...")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    count = 0

    # Quét trực tiếp các file .md nằm trong database/templates/
    for file_name in os.listdir(TEMPLATE_DIR):
        if file_name.endswith(".md"):
            file_path = os.path.join(TEMPLATE_DIR, file_name)

            try:
                result = parse_template_to_sql(file_path)
                if result:
                    table_name, query = result
                    cursor.execute(query)
                    print(f"✅ Đã lập đỉnh thành công bảng: [{table_name}]")
                    count += 1
            except Exception as e:
                print(f"❌ Lỗi khi xử lý file {file_name}: {e}")

    conn.commit()
    conn.close()

    print(f"\n🎉 Đại công cáo thành! Đã khởi tạo xong {count} bảng tại: {DB_PATH}")


if __name__ == "__main__":
    khoi_tao_database()
