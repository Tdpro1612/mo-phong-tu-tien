import os
import sqlite3

import frontmatter
import pandas as pd

from src.common.string_utils import clean_column_name, remove_accents_and_spaces

# ==============================================================================
# CONFIG CỜ HIỆU (FLAGS)
# ==============================================================================
RESET_DB = True  # Đổi thành False nếu muốn GHI TIẾP (Append) + CHECK TRÙNG LẶP
# ==============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "raw")
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
DB_PATH = os.path.join(BASE_DIR, "game_tu_tien.db")

UNIQUE_KEYS = {
    "he_thong_canh_gioi": "ten_goi",
    "he_thong_linh_can": "ten_linh_can",
    "he_thong_chi_so_nhan_vat": "ten_chi_so",
    "he_thong_nhiem_vu": "ten_nhiem_vu",
}


def get_expected_columns(table_name):
    if not os.path.exists(TEMPLATE_DIR):
        return None
    for file_name in os.listdir(TEMPLATE_DIR):
        if file_name.endswith(".md"):
            file_path = os.path.join(TEMPLATE_DIR, file_name)
            with open(file_path, "r", encoding="utf-8") as f:
                post = frontmatter.load(f)
            if post.get("id_he_thong") == table_name:
                columns_config = post.get("cac_cot_du_lieu", [])
                return [
                    clean_column_name(list(col_dict.keys())[0])
                    for col_dict in columns_config
                ]
    return None


def import_all_csv():
    if not os.path.exists(RAW_DIR):
        print(f"❌ Không tìm thấy thư mục: {RAW_DIR}")
        return

    print(
        f"📂 Cơ chế nạp: {'⚠️ XÓA SẠCH GHI LẠI (RESET)' if RESET_DB else '🔄 GHI TIẾP + CHECK TRÙNG (APPEND)'}"
    )
    print(f"📂 Đang quét dữ liệu thô tại: {RAW_DIR}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    count = 0

    for file_name in os.listdir(RAW_DIR):
        if file_name.endswith(".csv"):
            csv_path = os.path.join(RAW_DIR, file_name)
            name_without_ext = os.path.splitext(file_name)[0]
            table_name = remove_accents_and_spaces(name_without_ext)
            print(f"\n🔍 Phát hiện file CSV: '{file_name}' → Bảng đích: [{table_name}]")

            expected_columns = get_expected_columns(table_name)
            if not expected_columns:
                print(f"⚠️ Bỏ qua [{file_name}]: Không tìm thấy template .md tương ứng.")
                continue

            try:
                print(
                    f"\n🔄 --- Đang xử lý bảng [{table_name}] từ file '{file_name}' ---"
                )
                df_new = pd.read_csv(csv_path)
                df_new.columns = [clean_column_name(col) for col in df_new.columns]

                # Kiểm tra thừa thiếu cột
                extra_cols = [
                    c
                    for c in df_new.columns
                    if c not in expected_columns and c != "stt"
                ]
                missing_cols = [
                    c
                    for c in expected_columns
                    if c not in df_new.columns and c != "stt"
                ]

                if extra_cols:
                    print(f"⚠️ WARNING: Cột thừa sẽ bị loại bỏ: {extra_cols}")
                if missing_cols:
                    print(f"💡 INFO: Cột thiếu tự động bù None: {missing_cols}")

                for col in missing_cols:
                    df_new[col] = None
                df_new = df_new[
                    [col for col in expected_columns if col in df_new.columns]
                ]

                # LỰA CHỌN PHƯƠNG ÁN DỰA TRÊN FLAG RESET_DB
                if RESET_DB:
                    # Phương án 1: Trảm sạch bảng cũ trước khi ghi dữ liệu mới
                    print(
                        f"💥 Đang xóa sạch toàn bộ dữ liệu cũ của bảng [{table_name}]..."
                    )
                    cursor.execute(f"DELETE FROM {table_name};")
                    df_final = df_new
                else:
                    # Phương án 2: Ghi tiếp và kiểm tra trùng lặp
                    key = UNIQUE_KEYS.get(table_name)
                    table_exists = pd.read_sql_query(
                        f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';",
                        conn,
                    )

                    if not table_exists.empty and key:
                        df_old = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                        if not df_old.empty:
                            print(
                                f"📊 DB đang có sẵn {len(df_old)} dòng. So khớp chống trùng qua [{key}]..."
                            )
                            if "stt" in df_old.columns:
                                df_old = df_old.drop(columns=["stt"])
                            if "stt" in df_new.columns:
                                df_new = df_new.drop(columns=["stt"])

                            df_old[key] = df_old[key].astype(str).str.strip()
                            df_new[key] = df_new[key].astype(str).str.strip()

                            df_old = df_old[~df_old[key].isin(df_new[key])]
                            df_final = pd.concat([df_old, df_new], ignore_index=True)
                        else:
                            df_final = df_new
                    else:
                        df_final = df_new

                # TỰ ĐỘNG ĐÁNH LẠI SỐ STT LIÊN TỤC
                if "stt" in df_final.columns:
                    df_final = df_final.drop(columns=["stt"])
                df_final = df_final.reset_index(drop=True)
                df_final.insert(0, "stt", df_final.index + 1)

                cols_order = ["stt"] + [col for col in expected_columns if col != "stt"]
                df_final = df_final[cols_order]

                # Lưu vào SQLite
                df_final.to_sql(table_name, conn, if_exists="replace", index=False)
                print(
                    f"🎉 ĐỒNG BỘ HOÀN TẤT: Bảng [{table_name}] hiện có tổng cộng {len(df_final)} dòng."
                )
                count += 1

            except Exception as e:
                print(f"❌ Thất bại khi xử lý file '{file_name}': {e}")

    conn.commit()
    conn.close()
    print(f"\n🏁 Hoàn thành! Đã xử lý an toàn {count} hệ thống dữ liệu.")


if __name__ == "__main__":
    import_all_csv()
