# webui/routes.py
import os
import sqlite3

import frontmatter
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

webui_router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "database", "game_tu_tien.db")
TEMPLATE_DIR = os.path.join(BASE_DIR, "..", "database", "templates")

# Cấu hình Templates trỏ vào thư mục webui/ (chính là BASE_DIR)
templates = Jinja2Templates(directory=BASE_DIR)


# ==============================================================================
# HÀM BỔ TRỢ: Đọc thông tin cấu hình từ file Markdown Frontmatter
# ==============================================================================
def _load_system_template(system_id: str) -> tuple:
    """Đọc file template dạng markdown và lấy ra nội dung cấu hình UI."""
    intro_content = ""
    cac_cot_hien_thi_ui = []
    mapping_ngon_ngu_ui = {}

    if not os.path.exists(TEMPLATE_DIR):
        return intro_content, cac_cot_hien_thi_ui, mapping_ngon_ngu_ui

    for file_name in os.listdir(TEMPLATE_DIR):
        if not file_name.endswith(".md"):
            continue

        file_path = os.path.join(TEMPLATE_DIR, file_name)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                post = frontmatter.load(f)

            if post.get("id_he_thong") == system_id:
                intro_content = post.content
                cac_cot_hien_thi_ui = post.get("cac_cot_hien_thi_ui", [])
                mapping_ngon_ngu_ui = post.get("mapping_ngon_ngu_ui", {})
                break
        except (OSError, ValueError, KeyError):
            # Bắt đích danh các lỗi liên quan đến Đọc/Ghi file hoặc Khai báo sai cấu trúc TOML/YAML
            pass

    return intro_content, cac_cot_hien_thi_ui, mapping_ngon_ngu_ui


# ==============================================================================
# ROUTE 1: Render trang chủ giao diện web tĩnh khi vào http://127.0.0.1:8000/
# ==============================================================================
@webui_router.get("/", response_class=HTMLResponse)
async def index_page(request: Request):
    return templates.TemplateResponse(request=request, name="home.html")


# ==============================================================================
# ROUTE 2: API trả về danh sách các bảng (Bắt đầu bằng /api để Frontend dễ gọi)
# ==============================================================================
@webui_router.get("/api/systems")
async def get_systems():
    if not os.path.exists(DB_PATH):
        return JSONResponse(
            status_code=404, content={"message": "Không tìm thấy file DB"}
        )

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
    )
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()

    return {"tables": tables}


# ==============================================================================
# ROUTE 3: API bốc dữ liệu gộp hệ thống
# ==============================================================================
@webui_router.get("/api/system/{system_id}")
async def get_system_data(system_id: str):
    # Trích xuất bớt biến bằng cách gọi hàm bổ trợ
    intro_content, cac_cot_hien_thi_ui, mapping_ngon_ngu_ui = (
        _load_system_template(system_id)
    )

    headers = []
    rows = []

    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute(f"SELECT * FROM {system_id}")
            db_rows = [dict(row) for row in cursor.fetchall()]

            if db_rows:
                if not cac_cot_hien_thi_ui:
                    cac_cot_hien_thi_ui = list(db_rows[0].keys())

                headers = cac_cot_hien_thi_ui

                for row in db_rows:
                    filtered_row = {
                        col: row[col]
                        for col in cac_cot_hien_thi_ui
                        if col in row
                    }
                    rows.append(filtered_row)

        except sqlite3.Error as e:
            # Thay đổi từ Exception chung chung sang lỗi đặc thù của SQLite
            print(f"Lỗi truy vấn DB: {e}")
        finally:
            conn.close()

    return {
        "id_he_thong": system_id,
        "huong_dan_markdown": intro_content,
        "cac_cot_hien_thi_ui": headers,
        "mapping_ngon_ngu_ui": mapping_ngon_ngu_ui,
        "rows": rows,
    }
