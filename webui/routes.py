# webui/routes.py
import os

from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

from database.database_manager import get_all_table_names
from database.database_utils import parse_file_md_schema

webui_router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "database", "db", "game_tu_tien.db")
DATA_TEMPLATE_DIR = os.path.join(BASE_DIR, "..", "database", "data_templates")

# Cấu hình Templates trỏ vào thư mục webui/ (chính là BASE_DIR)
templates = Jinja2Templates(directory=BASE_DIR)


# ==============================================================================
# HÀM BỔ TRỢ: Đọc thông tin cấu hình từ file Markdown Frontmatter
# ==============================================================================
@webui_router.get("/api/webui-schemas")
async def get_webui_schemas():
    """API quét danh sách bảng game và bốc sạch cấu hình Mapping/UI từ file .md tương ứng."""
    # 1. Lấy tất cả các bảng và lọc tiền tố he_thong_
    all_tables_names = get_all_table_names(DB_PATH)
    table_name_list = [t for t in all_tables_names if t.startswith("he_thong_")]
    
    schemas_response = {}
    
    # 2. Duyệt từng bảng để parse file .md tương ứng
    for table_name in table_name_list:
        md_file_path = os.path.join(DATA_TEMPLATE_DIR, f"{table_name}.md")
        
        if os.path.exists(md_file_path):
            # Tận dụng hàm "xịn" của bạn để bốc tách id_he_thong, cac_cot_hien_thi_ui, mapping_ngon_ngu_ui...
            schema_data = parse_file_md_schema(md_file_path)
            schemas_response[table_name] = schema_data
        else:
            # Nếu không có file template, trả về rỗng để Frontend tự fallback về DB gốc
            schemas_response[table_name] = {}
            
    return schemas_response
