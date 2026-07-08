import sqlite3

# ----------------------------------------------------------------------
# 1. TẠO BẢNG HỆ THỐNG 
# ----------------------------------------------------------------------
def create_a_table(cursor: sqlite3.Cursor, table_name: str, dict_columns: list) -> bool:
    """Hàm chuẩn mực tạo một bảng trống dựa trên tham số đầu vào."""
    valid_prefixes = ("data_", "he_thong_", "sys_")
    if not table_name.startswith(valid_prefixes):
        print(f"❌ Lỗi: Tên bảng '{table_name}' không hợp lệ! Phải bắt đầu bằng: {valid_prefixes}")
        return False

    if not dict_columns or len(dict_columns) < 3:
        print(f"❌ Lỗi: Bảng '{table_name}' không đủ dữ liệu cấu trúc! (Yêu cầu >= 3 cột).")
        return False
    
    is_existed = check_table_exists(cursor, table_name)
    
    if is_existed:
        print(f"ℹ️ Bảng [{table_name}] đã tồn tại trong Hệ thống. Không cần tạo lại.")
        return True
    sql_columns = []
    for index, col_dict in enumerate(dict_columns):
        for col_name, col_type in col_dict.items():
            col_name_clean = col_name.strip()
            col_type_clean = col_type.strip()

            if index == 0:
                sql_columns.append(f"{col_name_clean} INTEGER PRIMARY KEY AUTOINCREMENT")
            else:
                sql_columns.append(f"{col_name_clean} {col_type_clean}")

    columns_sql_str = ",\n    ".join(sql_columns)
    create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} (\n    {columns_sql_str}\n);"

    cursor.execute(create_table_query)
    print(f"✅ Tạo thành công cấu trúc bảng biểu trống: [{table_name}]")
    return True

# ----------------------------------------------------------------------
# 2. KIỂM TRA TỒN TẠI BẢNG 
# ----------------------------------------------------------------------
def check_table_exists(cursor: sqlite3.Cursor, table_name: str) -> bool:
    """Kiểm tra xem một bảng đã tồn tại trong Database hay chưa."""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
    return cursor.fetchone() is not None

# ----------------------------------------------------------------------
# 3. XÓA BẢNG 
# ----------------------------------------------------------------------
def delete_table(cursor: sqlite3.Cursor, table_name) -> bool:
    """Xóa bảng khỏi hệ thống (Hỗ trợ cả chuỗi hoặc list chuỗi)."""
    if isinstance(table_name, str):
        tables_to_delete = [table_name]
    elif isinstance(table_name, list):
        tables_to_delete = table_name
    else:
        print("❌ Lỗi: Tham số table_name phải là chuỗi hoặc danh sách chuỗi!")
        return False

    success = True
    for table in tables_to_delete:
        if not check_table_exists(cursor, table):
            print(f"⚠️ Bảng '{table}' không tồn tại để xóa.")
            success = False
            continue
            
        cursor.execute(f"DROP TABLE IF EXISTS {table};")
        print(f"🔥 Đã xóa hoàn toàn bảng: [{table}]")
    return success

# ----------------------------------------------------------------------
# 4. THÊM 1 DÒNG VÀO BẢNG HỆ THỐNG 
# ----------------------------------------------------------------------
def add_one_row(cursor: sqlite3.Cursor, table_name: str, row_data: dict) -> bool:
    """Thêm mới 1 dòng vào bảng an toàn chống SQL Injection."""
    if not check_table_exists(cursor, table_name):
        print(f"❌ Lỗi: Bảng '{table_name}' chưa được khởi tạo.")
        return False

    columns = ", ".join(row_data.keys())
    placeholders = ", ".join(["?"] * len(row_data))
    values = tuple(row_data.values())

    query = f"INSERT OR REPLACE INTO {table_name} ({columns}) VALUES ({placeholders});"
    cursor.execute(query, values)
    return True

# ----------------------------------------------------------------------
# 5. THÊM NHIỀU DÒNG VÀO BẢNG HỆ THỐNG 
# ----------------------------------------------------------------------
def add_many_rows(cursor: sqlite3.Cursor, table_name: str, rows_list: list) -> bool:
    """Thêm nhiều dòng cùng lúc - Ép nghiêm ngặt theo cấu trúc cột chuẩn xịn dưới DB."""
    if not rows_list:
        return False

    if not check_table_exists(cursor, table_name):
        print(f"❌ Lỗi: Bảng '{table_name}' chưa được khởi tạo.")
        return False

    # 1. BỐC CẤU TRÚC CỘT CHUẨN TỪ DATABASE LÊN
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns_info = cursor.fetchall()
    
    # columns_info có dạng: [(id, name, type, notnull, dflt_value, pk), ...]
    # Chúng ta bỏ cột đầu tiên (index 0 - Cột ID PRIMARY KEY AUTOINCREMENT)
    db_standard_keys = [col[1] for col in columns_info[1:]] 
    
    # 2. RÁP KHUÔN CÂU LỆNH SQL CHUẨN ĐẾN TỪNG XĂNG-TI-MÉT
    columns_sql = ", ".join(db_standard_keys)
    placeholders = ", ".join(["?"] * len(db_standard_keys))
    query = f"INSERT OR REPLACE INTO {table_name} ({columns_sql}) VALUES ({placeholders});"
    
    # 3. ÉP DỮ LIỆU CỦA TỪNG DICT THEO ĐÚNG KHUÔN MẪU CỦA DB
    values_to_insert = []
    for row in rows_list:
        # Cứ soi theo danh sách cột của DB, có thì bốc, không có thì tự nạp None (NULL)
        row_tuple = tuple(row.get(key) for key in db_standard_keys)
        values_to_insert.append(row_tuple)

    # 4. CHẠY TRANSACTION BẢO VỆ TOÀN VẸN DỮ LIỆU
    connection = cursor.connection
    with connection:
        cursor.executemany(query, values_to_insert)
        
    print(f"🌱 Đã nạp thành công {len(rows_list)} dòng vào bảng [{table_name}] theo cấu trúc DB chuẩn.")
    return True

# ----------------------------------------------------------------------
# 6. HÀM HỖ TRỢ LẤY CỘT NAME TRONG BẢNG HỆ THỐNG 
# ----------------------------------------------------------------------
def _get_key_column_name(cursor: sqlite3.Cursor, table_name: str) -> str:
    """Hàm bổ trợ: Trích xuất chính xác tên của Cột số 2 (Business Key)."""
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns_info = cursor.fetchall()
    if len(columns_info) < 2:
        raise ValueError(f"❌ Lỗi: Bảng '{table_name}' không đủ số cột tiêu chuẩn.")
    return columns_info[1][1]

# ----------------------------------------------------------------------
# 7. HÀM XÓA 1 DÒNG TRONG BẢNG HỆ THỐNG 
# ----------------------------------------------------------------------
def delete_one_row(cursor: sqlite3.Cursor, table_name: str, key_value, key_column_name: str = None) -> bool:
    """Xóa 1 dòng dựa vào giá trị của Cột số 2. Cho phép truyền trước key_column_name để tối ưu."""
    if not check_table_exists(cursor, table_name):
        return False

    if key_column_name is None:
        try:
            key_column_name = _get_key_column_name(cursor, table_name)
        except ValueError as e:
            print(e)
            return False

    query = f"DELETE FROM {table_name} WHERE {key_column_name} = ?;"
    cursor.execute(query, (key_value,))
    
    if cursor.rowcount > 0:
        return True
    else:
        print(f"⚠️ Không tìm thấy dòng nào có {key_column_name} = '{key_value}' để xóa.")
        return False

# ----------------------------------------------------------------------
# 8. HÀM XÓA NHIỀU DÒNG TRONG BẢNG HỆ THỐNG 
# ----------------------------------------------------------------------
def delete_many_rows(cursor: sqlite3.Cursor, table_name: str, key_values_list: list) -> bool:
    """Xóa nhiều dòng đồng thời sử dụng toán tử IN."""
    if not key_values_list:
        return False

    if not check_table_exists(cursor, table_name):
        return False

    try:
        key_column_name = _get_key_column_name(cursor, table_name)
    except ValueError:
        return False

    placeholders = ", ".join(["?"] * len(key_values_list))
    query = f"DELETE FROM {table_name} WHERE {key_column_name} IN ({placeholders});"
    
    connection = cursor.connection
    with connection:
        cursor.execute(query, tuple(key_values_list))
    
    print(f"🗑️ Đã quét và xóa thành công {cursor.rowcount} dòng khỏi bảng [{table_name}].")
    return True

# ----------------------------------------------------------------------
# 9. HÀM UPDATE 1 DÒNG TRONG BẢNG HỆ THỐNG 
# ----------------------------------------------------------------------
def update_one_row(cursor: sqlite3.Cursor, table_name: str, key_old_value, update_data: dict, key_column_name: str = None) -> bool:
    """Cập nhật dữ liệu của 1 dòng dựa vào giá trị CŨ của Cột số 2."""
    if not check_table_exists(cursor, table_name):
        return False

    if key_column_name is None:
        try:
            key_column_name = _get_key_column_name(cursor, table_name)
        except ValueError as e:
            print(e)
            return False

    if not update_data:
        print("⚠️ Không có trường dữ liệu nào cần cập nhật.")
        return False

    set_clauses = ", ".join([f"{col} = ?" for col in update_data.keys()])
    values = tuple(update_data.values()) + (key_old_value,)

    query = f"UPDATE {table_name} SET {set_clauses} WHERE {key_column_name} = ?;"
    cursor.execute(query, values)
    
    if cursor.rowcount > 0:
        return True
    else:
        print(f"⚠️ Thất bại: Không tìm thấy dòng có {key_column_name} = '{key_old_value}' để cập nhật.")
        return False

# ----------------------------------------------------------------------
# 10. HÀM UPDATE NHIỀU DÒNG TRONG BẢNG HỆ THỐNG 
# ----------------------------------------------------------------------
def update_many_rows(cursor: sqlite3.Cursor, table_name: str, update_list: list) -> bool:
    """Cập nhật nhiều dòng linh hoạt (Hỗ trợ thiếu trường dữ liệu)
    
    Đồng thời an toàn tuyệt đối bằng Transaction (Nếu đứt giữa chừng sẽ hủy hết để chạy lại từ đầu).
    """
    if not update_list:
        return False

    if not check_table_exists(cursor, table_name):
        return False

    try:
        # Lấy tên cột số 2 đúng 1 lần duy nhất để tối ưu tốc độ I/O cho SQLite
        key_column_name = _get_key_column_name(cursor, table_name)
    except ValueError:
        return False

    count = 0
    connection = cursor.connection
    
    # BẮT ĐẦU KÉT SẮT TRANSACTION AN TOÀN
    try:
        with connection: # Đứt ở đây là SQLite tự hủy hết, database không bị lỗi nửa vời
            for item in update_list:
                k_old = item.get("key_old")
                data_new = item.get("data") # Cục data này thiếu trường thoải mái!
                
                if k_old is None or not data_new:
                    continue
                    
                # Gọi hàm đơn lẻ (Hàm này sinh câu lệnh SQL động chỉ SET những trường có trong data_new)
                if update_one_row(cursor, table_name, k_old, data_new, key_column_name):
                    count += 1
                    
        print(f"🔄 Chốt sổ (COMMIT)! Đã cập nhật thành công {count}/{len(update_list)} dòng vào bảng [{table_name}].")
        return True

    except Exception as e:
        # Nếu có bất kỳ lỗi gì làm đứt luồng (sập nguồn, lỗi code...), toàn bộ quá trình trên sẽ bị hủy (ROLLBACK)
        print(f"🔥 Hệ thống bị đứt giữa chừng! Đã kích hoạt Rollback hủy toàn bộ dữ liệu lỗi. Chi tiết: {e}")
        return False

# ==============================================================================
# 11: LẤY HẾT TÊN TẤT CẢ CÁC BẢNG ĐANG CÓ TRONG DB
# ==============================================================================
def get_all_table_names(db_path: str) -> list[str]:
    """
    Quét hệ thống SQLite dựa trên đường dẫn DB_PATH truyền vào 
    và trả về danh sách tên của tất cả các bảng (tables).
    """
    query = """
        SELECT name 
        FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%';
    """
    # Khởi tạo kết nối nội bộ bằng block 'with' để tự động đóng DB khi xong
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            return [row[0] for row in rows]
            
    except Exception as e:
        print(f"❌ Lỗi khi lấy danh sách tên bảng từ {db_path}: {e}")
        return []


# ==============================================================================
# 12: LẤY TOÀN BỘ DỮ LIỆU CỦA MỘT BẢNG NHẤT ĐỊNH (DẠNG LIST DICT)
# ==============================================================================
def get_all_rows_from_table(db_path: str, table_name: str) -> list[dict]:
    """
    Lấy toàn bộ các dòng dữ liệu của một bảng chỉ định dựa trên db_path.
    Kết quả trả về tự động mapping tên cột thành dạng List[Dict].
    """
    try:
        with sqlite3.connect(db_path) as conn:
            # 💡 Bật row_factory để SQLite tự động mapping tên cột vào giá trị
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(f"SELECT * FROM {table_name};")
            rows = cursor.fetchall()
            
            # Chỉ cần ép kiểu từng row thành dict là xong, cực kỳ tối ưu
            return [dict(row) for row in rows]
            
    except Exception as e:
        print(f"❌ Lỗi khi lấy dữ liệu từ bảng [{table_name}] tại {db_path}: {e}")
        return []