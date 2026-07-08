import os
import sqlite3
import pandas as pd
# Import hàm bóc tách từ file utils của bạn
from database_utils import parse_file_md_schema
from database_manager import create_a_table, check_table_exists, add_many_rows
from src.common.string_utils import clean_column_name, remove_accents_and_spaces
from datetime import datetime
import json
# LẤY ĐƯỜNG DẪN TUYỆT ĐỐI CỦA THƯ MỤC NƠI FILE SCRIPT NÀY ĐANG ĐỨNG
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_DIR = os.path.normpath(os.path.join(BASE_DIR, "raw_data"))
TEMPLATE_DIR = os.path.join(BASE_DIR, "data_templates")
DB_PATH = os.path.join(BASE_DIR, "db", "game_tu_tien.db")
db_dir = os.path.dirname(DB_PATH)  # Lấy ra đường dẫn của folder 'db'
if not os.path.exists(db_dir):
    os.makedirs(db_dir)

# 1. Định nghĩa các trường định danh chống trùng cho từng bảng (giống file cũ của bạn)
UNIQUE_KEYS = {
    "he_thong_canh_gioi": "ten_goi",
    "he_thong_linh_can": "ten_linh_can",
    "he_thong_chi_so_nhan_vat": "ten_chi_so",
    "he_thong_nhiem_vu": "ten_nhiem_vu",
}


def khoi_tao_database_for_data_game():
    if not os.path.exists(TEMPLATE_DIR):
        print(f"❌ Không tìm thấy thư mục template tại: {TEMPLATE_DIR}")
        return

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

def parse_csv_to_payload_and_table(csv_path: str):
    """
    Đọc file CSV và trả về:
    - table_name (str): Tên bảng (làm sạch từ tên file bằng remove_accents_and_spaces)
    - payload (list[dict]): Danh sách dữ liệu (cột làm sạch bằng clean_column_name, ô trống mang giá trị None)
    """
    # 1. Trích xuất tên file (bỏ đuôi .csv) 
    file_name_without_ext = os.path.splitext(os.path.basename(csv_path))[0]
    
    # 2. Sử dụng remove_accents_and_spaces để chuyển tên file thành tên bảng chuẩn
    table_name = remove_accents_and_spaces(file_name_without_ext)
    
    # 3. Đọc file CSV bằng Pandas
    df = pd.read_csv(csv_path)
    
    # 4. Làm sạch tên toàn bộ các cột trong CSV bằng clean_column_name
    df.columns = [clean_column_name(col) for col in df.columns]
    
    # 5. Ép tất cả các ô trống (NaN/Empty) trong DataFrame thành giá trị None (null)
    df_clean = df.where(pd.notnull(df), None)
    
    # 6. Chuyển đổi DataFrame thành danh sách các dictionary (List[Dict])
    payload = df_clean.to_dict(orient='records')
    # 2. Đoạn xử lý bên trong vòng lặp nạp file CSV của bạn:
    return table_name, payload

def get_all_csv_file_paths(directory_path: str) -> list:
    """Hàm lấy tất cả đường dẫn file (file path) .csv trong thư mục chỉ định."""
    if not os.path.exists(directory_path):
        print(f"❌ Thư mục không tồn tại: {directory_path}")
        return []
        
    csv_paths = []
    for file_name in os.listdir(directory_path):
        if file_name.endswith(".csv"):
            full_path = os.path.join(directory_path, file_name)
            csv_paths.append(full_path)
            
    return csv_paths


def import_all_game_data():
    """Hàm quét toàn bộ file CSV, xử lý parse và truyền dữ liệu trực tiếp vào các table, 
    sau đó lưu vết phiên bản vào bảng quản trị hệ thống sys_version_archive (Có check trùng log)."""
    print("====== 💾 BẮT ĐẦU QUY TRÌNH NẠP DỮ LIỆU VÀO DATABASE ======")
    
    # 1. Lấy danh sách tất cả file path CSV
    csv_files = get_all_csv_file_paths(RAW_DATA_DIR)
    if not csv_files:
        print("⚠️ Không có file CSV nào để xử lý.")
        return

    # Khởi tạo kết nối SQLite chuyên dụng để truyền vào hàm core
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    success_count = 0
    # Cấu trúc lưu vết phục vụ cho B4: List[Dict] chứa thông tin chi tiết từng bảng đã nạp thành công
    imported_history = [] 

    # 2. Lặp qua từng file path để xử lý truyền dữ liệu
    for file_path in csv_files:
        file_name = os.path.basename(file_path)
        try:
            # Bước 2a: Gọi hàm parse để lấy tên bảng và list[dict] dữ liệu thô
            table_name, payload = parse_csv_to_payload_and_table(file_path)
            
            if not payload:
                print(f"⚠️ Bỏ qua file {file_name}: Không có dữ liệu hoặc parse lỗi.")
                continue

            print(f"\n🔍 Đang xử lý file: {file_name} → Bảng đích: [{table_name}]")

            # Bước 2b: Kiểm tra xem bảng mục tiêu đã tồn tại trong DB chưa trước khi tính toán
            if not check_table_exists(cursor, table_name):
                print(f"❌ Lỗi: Bảng [{table_name}] chưa được khởi tạo trong database. Hãy chạy script tạo bảng trước!")
                continue

            # Bước 2c: Kiểm tra dữ liệu trùng lặp (nếu bảng có định nghĩa UNIQUE_KEY)
            unique_key = UNIQUE_KEYS.get(table_name)
            if unique_key:
                try:
                    cursor.execute(f"SELECT {unique_key} FROM {table_name};")
                    existing_rows = cursor.fetchall()
                    existing_keys = set(str(row[0]).strip() for row in existing_rows)
                except Exception:
                    existing_keys = set()
                    
                new_rows_count = 0
                replaced_rows_count = 0
                
                for row in payload:
                    row_key = str(row.get(unique_key, "")).strip()
                    if row_key in existing_keys:
                        print(f"🔄 Dòng đã tồn tại: [{row_key}] -> Sẽ thực hiện REPLACE (ghi đè dữ liệu mới).")
                        replaced_rows_count += 1
                    else:
                        new_rows_count += 1
                        
                print(f"📊 Thống kê sơ bộ bảng [{table_name}]: Thêm mới {new_rows_count} dòng, Ghi đè {replaced_rows_count} dòng đã tồn tại.")

            # 3. Gọi hàm add_many_rows truyền trực tiếp list[dict] vào bảng
            print(f"📦 Đang nạp {len(payload)} dòng dữ liệu vào bảng [{table_name}]...")
            success = add_many_rows(cursor, table_name, payload)
            
            if success:
                print(f"🎉 Đã nạp dữ liệu vào bảng [{table_name}] THÀNH CÔNG!")
                success_count += 1
                
                # Lưu lại thông tin bảng và payload để lát ghi nhận archive
                imported_history.append({
                    "table_name": table_name,
                    "unique_key": unique_key if unique_key else "id",
                    "payload": payload
                })
            else:
                print(f"❌ Hàm core báo nạp dữ liệu bảng [{table_name}] THẤT BẠI.")

        except Exception as e:
            print(f"❌ Gặp lỗi khi xử lý file {file_name}: {e}")

    # ==============================================================================
    # B4: TẠO VERSION ARCHIVE CHO CÁC DỮ LIỆU NÀY VỚI QUYỀN USER ROOT (CÓ CHECK TRÙNG LOG)
    # ==============================================================================
    if imported_history:
        try:
            print("\n==============================================================================")
            print("📜 ĐANG GHI LOG PHIÊN BẢN VÀO BẢNG [sys_version_archive]...")
            
            current_version = "v1.0.0" 
            archive_payloads = []

            # 🛑 BƯỚC CHECK TRÙNG LOG: Lấy các log đã tồn tại của phiên bản hiện tại lên để đối chiếu
            existing_logs = set()
            if check_table_exists(cursor, "sys_version_archive"):
                try:
                    # Gom bộ ba định danh: (số_version, tên_bảng, khóa_nghiệp_vụ) để làm khóa unique cho log
                    cursor.execute("SELECT version, table_name, b_key_value FROM sys_version_archive;")
                    rows = cursor.fetchall()
                    # Tạo set chứa chuỗi ghép "version|table_name|b_key_value" để so khớp cực nhanh
                    existing_logs = set(f"{str(r[0]).strip()}|{str(r[1]).strip()}|{str(r[2]).strip()}" for r in rows)
                except Exception:
                    existing_logs = set()

            # Duyệt qua lịch sử để đóng gói payload archive
            log_skipped_count = 0
            for item in imported_history:
                t_name = item["table_name"]
                u_key = item["unique_key"]
                
                for row in item["payload"]:
                    b_key_val = str(row.get(u_key, "N/A")).strip()
                    
                    # Tạo chuỗi định danh duy nhất cho dòng log sắp ghi
                    log_identifier = f"{current_version}|{t_name}|{b_key_val}"
                    
                    # Nếu bộ log này đã tồn tại trong DB rồi thì bỏ qua không nạp trùng nữa
                    if log_identifier in existing_logs:
                        log_skipped_count += 1
                        continue
                        
                    delta_patch_json = json.dumps([None, row], ensure_ascii=False)
                    
                    archive_row = {
                        "version": current_version,
                        "table_name": t_name,
                        "b_key_value": b_key_val,
                        "action_type": "NEW",
                        "delta_patch": delta_patch_json,
                        "username": "rootdev",
                        "manager_name": "rootdev"
                    }
                    archive_payloads.append(archive_row)

            # Thực hiện nạp nếu có log mới cần ghi nhận
            if archive_payloads:
                if check_table_exists(cursor, "sys_version_archive"):
                    print(f"📦 Đang nạp {len(archive_payloads)} dòng log phiên bản mới vào [sys_version_archive]...")
                    add_many_rows(cursor, "sys_version_archive", archive_payloads)
                    conn.commit()
                    print(f"✨ Ghi log [sys_version_archive] thành công cho phiên bản [{current_version}]!")
                else:
                    print("❌ Lỗi: Bảng [sys_version_archive] chưa được tạo. Không thể ghi nhận log phiên bản.")
            else:
                print(f"⏭️ Toàn bộ {log_skipped_count} dòng log cho phiên bản [{current_version}] đều đã tồn tại trước đó. Bỏ qua ghi trùng!")

        except Exception as e:
            conn.rollback()
            print(f"⚠️ Cảnh báo: Không thể tạo version dữ liệu trong sys_version_archive: {e}")

    # Đóng kết nối sau khi hoàn thành toàn bộ danh sách file
    conn.close()
    print(f"\n🏁 Quy trình kết thúc. Đã xử lý thành công {success_count}/{len(csv_files)} bảng dữ liệu.")
if __name__ == "__main__":
    khoi_tao_database_for_data_game()
    import_all_game_data()
