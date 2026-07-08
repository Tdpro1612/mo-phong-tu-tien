import re
from typing import Dict, Any, List


def parse_file_md_schema(file_path: str) -> Dict[str, Any]:
    """Hàm util cao cấp phân tích cú pháp cấu hình Game Data từ file Markdown.

    Xử lý cấu trúc phân tầng phức tạp (id_he_thong, cac_cot_du_lieu,
    cac_cot_hien_thi_ui, mapping_ngon_ngu_ui) và hốt trọn tài liệu hướng dẫn tĩnh.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Hốt trọn vùng Front Matter nằm giữa cặp dấu --- ở đầu file
    front_matter_match = re.search(r"^---\s*(?:\r?\n)(.*?)(?:\r?\n)---\s*(?:\r?\n|$)", content, re.DOTALL)
    
    if not front_matter_match:
        raise ValueError(f"❌ Lỗi: Không tìm thấy Front Matter trong file {file_path}")

    front_matter_text = front_matter_match.group(1)
    
    # 🎯 BỔ SUNG: Cắt lấy toàn bộ nội dung tài liệu Markdown nằm phía sau dấu --- kết thúc
    end_of_front_matter = front_matter_match.end()
    markdown_intro = content[end_of_front_matter:].strip()
    
    # 2. Chuẩn bị các thùng chứa dữ liệu đầu ra
    result = {
        "id_he_thong": "",
        "ten_he_thong": "",
        "ten_danh_muc_chinh": "",
        "cac_cot_du_lieu": [],          # Định dạng list dict [{"col": "type"}] phục vụ DB
        "cac_cot_hien_thi_ui": [],      # Danh sách các cột được phép lên sàn Web
        "mapping_ngon_ngu_ui": {},       # Từ điển dịch nhãn tiếng Việt cho UI
        "intro": markdown_intro # 🎯 LƯU TRỮ VÀO ĐÂY ĐỂ ĐẨY LÊN FRONTEND
    }

    # 3. Phân tích trạng thái đọc bằng Regex dòng
    lines = front_matter_text.split("\n")
    current_section = None

    for line in lines:
        # Làm sạch comment inline trên các dòng cấu hình tổng quát
        line_clean = line.strip()
        if not line_clean or line_clean.startswith("#"):
            continue

        # Bốc tách các thuộc tính phẳng ở tầng gốc (Root keys)
        if current_section is None or not line.startswith("  "):
            if "id_he_thong:" in line_clean:
                result["id_he_thong"] = line_clean.split(":", 1)[1].strip().strip('"\'')
                current_section = None; continue
            elif "ten_he_thong:" in line_clean:
                result["ten_he_thong"] = line_clean.split(":", 1)[1].strip().strip('"\'')
                current_section = None; continue
            elif "ten_danh_muc_chinh:" in line_clean:
                result["ten_danh_muc_chinh"] = line_clean.split(":", 1)[1].strip().strip('"\'')
                current_section = None; continue
            
            # Phát hiện điểm bắt đầu của các vùng dữ liệu mảng/đối tượng
            if line_clean.startswith("cac_cot_du_lieu:"):
                current_section = "db_cols"; continue
            elif line_clean.startswith("cac_cot_hien_thi_ui:"):
                current_section = "ui_cols"; continue
            elif line_clean.startswith("mapping_ngon_ngu_ui:"):
                current_section = "ui_mapping"; continue

        # 4. Đọc dữ liệu chi tiết của từng vùng (Section) dựa vào thụt lề đầu dòng
        if current_section == "db_cols" and line_clean.startswith("-"):
            col_raw = line_clean[1:].strip()
            if "#" in col_raw:
                col_raw = col_raw.split("#", 1)[0].strip()
            if ":" in col_raw:
                k, v = col_raw.split(":", 1)
                result["cac_cot_du_lieu"].append({k.strip(): v.strip().strip('"\'')})

        elif current_section == "ui_cols" and line_clean.startswith("-"):
            col_name = line_clean[1:].strip()
            result["cac_cot_hien_thi_ui"].append(col_name)

        elif current_section == "ui_mapping" and ":" in line_clean:
            k, v = line_clean.split(":", 1)
            result["mapping_ngon_ngu_ui"][k.strip()] = v.strip().strip('"\'')

    return result
