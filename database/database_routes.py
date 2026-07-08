from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Union
import sqlite3
import os

# Import chuẩn mực đường dẫn DB và toàn bộ 9 hàm core từ file của bạn
from .database_manager import (
    create_a_table,
    check_table_exists,
    delete_table,
    add_one_row,
    add_many_rows,
    delete_one_row,
    delete_many_rows,
    get_all_rows_from_table,
    get_all_table_names,
    update_one_row,
    update_many_rows
)

# Quy hoạch đường dẫn DB động giống các file khác trong folder database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.normpath(os.path.join(BASE_DIR, "db", "game_tu_tien.db"))
database_routes = APIRouter()


# --- BỘ ĐỊNH NGHĨA PAYLOAD CHO TỪNG HÀM CORE (Dựa 1-1 theo tham số của bạn) ---

class CreateTableIn(BaseModel):
    table_name: str
    dict_columns: List[Dict[str, str]]

class DeleteTableIn(BaseModel):
    table_name: Union[str, List[str]]  # Hàm của bạn hỗ trợ cả chuỗi hoặc list chuỗi

class AddOneRowIn(BaseModel):
    table_name: str
    row_data: Dict[str, Any]

class AddManyRowsIn(BaseModel):
    table_name: str
    rows_list: List[Dict[str, Any]]

class DeleteOneRowIn(BaseModel):
    table_name: str
    key_value: Any
    key_column_name: str = None  # Cho phép truyền trước hoặc để None tự bốc cột số 2

class DeleteManyRowsIn(BaseModel):
    table_name: str
    key_values_list: List[Any]

class UpdateOneRowIn(BaseModel):
    table_name: str
    key_old_value: Any
    update_data: Dict[str, Any]
    key_column_name: str = None

class UpdateItem(BaseModel):
    key_old: Any
    data: Dict[str, Any]

class UpdateManyRowsIn(BaseModel):
    table_name: str
    update_list: List[UpdateItem]


# --- BỘ ROUTES API CHUẨN MỰC THỰC THI 1-1 ---

@database_routes.post("/create-table")
def api_create_table(payload: CreateTableIn):
    """Hàm 1: Tạo một bảng trống dựa trên tham số đầu vào."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        success = create_a_table(cursor, payload.table_name, payload.dict_columns)
        if success:
            conn.commit()
            return {"status": "success", "message": f"Xử lý bảng [{payload.table_name}] hoàn tất."}
        raise HTTPException(status_code=400, detail="Tạo bảng thất bại.")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@database_routes.get("/check-table/{table_name}")
def api_check_table_exists(table_name: str):
    """Hàm 2: Kiểm tra xem một bảng đã tồn tại hay chưa."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        exists = check_table_exists(cursor, table_name)
        return {"table_name": table_name, "exists": exists}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@database_routes.delete("/delete-table")
def api_delete_table(payload: DeleteTableIn):
    """Hàm 3: Xóa bảng khỏi hệ thống (Hỗ trợ chuỗi hoặc danh sách chuỗi)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        success = delete_table(cursor, payload.table_name)
        if success:
            conn.commit()
            return {"status": "success", "message": f"Đã thực thi xóa bảng mục tiêu."}
        raise HTTPException(status_code=400, detail="Xóa bảng thất bại hoặc bảng không tồn tại.")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@database_routes.delete("/delete-all-tables")
def api_delete_all_table():
    """Hàm 6: Xóa tất cả bảng khỏi hệ thống (Hỗ trợ danh sách chuỗi)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        list_tables_names = get_all_table_names(DB_PATH)
        if not list_tables_names:
            raise HTTPException(status_code=400, detail="Không có bảng nào để xóa.")
        success = delete_table(cursor, list_tables_names)
        if success:
            conn.commit()
            return {"status": "success", "message": f"Đã thực thi xóa tất cả bảng mục tiêu."}
        raise HTTPException(status_code=400, detail="Xóa bảng thất bại hoặc bảng không tồn tại.")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@database_routes.post("/add-one-row")
def api_add_one_row(payload: AddOneRowIn):
    """Hàm 4: Thêm mới 1 dòng vào bảng an toàn chống SQL Injection."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        success = add_one_row(cursor, payload.table_name, payload.row_data)
        if success:
            conn.commit()
            return {"status": "success", "message": "Thêm 1 dòng thành công."}
        raise HTTPException(status_code=400, detail="Thêm dòng thất bại (Bảng chưa được khởi tạo).")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@database_routes.post("/add-many-rows")
def api_add_many_rows(payload: AddManyRowsIn):
    """Hàm 5: Thêm nhiều dòng cùng lúc - Ép nghiêm ngặt theo cấu trúc cột chuẩn dưới DB."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # Hàm add_many_rows của bạn đã tự quản lý transaction (with connection), 
        # nên ở đây chỉ cần truyền cursor vào chạy.
        success = add_many_rows(cursor, payload.table_name, payload.rows_list)
        if success:
            return {"status": "success", "message": f"Đã nạp {len(payload.rows_list)} dòng thành công."}
        raise HTTPException(status_code=400, detail="Nạp nhiều dòng thất bại.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@database_routes.delete("/delete-one-row")
def api_delete_one_row(payload: DeleteOneRowIn):
    """Hàm 7: Xóa 1 dòng dựa vào giá trị của Cột số 2."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        success = delete_one_row(cursor, payload.table_name, payload.key_value, payload.key_column_name)
        if success:
            conn.commit()
            return {"status": "success", "message": f"Đã xóa thành công dòng có giá trị '{payload.key_value}'."}
        raise HTTPException(status_code=400, detail="Xóa dòng thất bại (Không tìm thấy hoặc lỗi bảng).")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@database_routes.delete("/delete-many-rows")
def api_delete_many_rows(payload: DeleteManyRowsIn):
    """Hàm 8: Xóa nhiều dòng đồng thời sử dụng toán tử IN (Tự quản lý Transaction)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        success = delete_many_rows(cursor, payload.table_name, payload.key_values_list)
        if success:
            return {"status": "success", "message": "Thực thi quét xóa loạt hoàn tất."}
        raise HTTPException(status_code=400, detail="Xóa chuỗi dòng thất bại.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@database_routes.put("/update-one-row")
def api_update_one_row(payload: UpdateOneRowIn):
    """Hàm 9: Cập nhật dữ liệu của 1 dòng dựa vào giá trị CŨ của Cột số 2."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        success = update_one_row(cursor, payload.table_name, payload.key_old_value, payload.update_data, payload.key_column_name)
        if success:
            conn.commit()
            return {"status": "success", "message": "Cập nhật 1 dòng thành công."}
        raise HTTPException(status_code=400, detail="Cập nhật thất bại (Không tìm thấy dòng hoặc dữ liệu rỗng).")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@database_routes.put("/update-many-rows")
def api_update_many_rows(payload: UpdateManyRowsIn):
    """Hàm 10: Cập nhật nhiều dòng linh hoạt (Tự quản lý Transaction an toàn tuyệt đối)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # Chuyển đổi payload từ dạng list Pydantic object sang list dict thô để tương thích với hàm core
        raw_update_list = [item.model_dump() for item in payload.update_list]
        
        success = update_many_rows(cursor, payload.table_name, raw_update_list)
        if success:
            return {"status": "success", "message": "Cập nhật chuỗi dòng hoàn tất."}
        raise HTTPException(status_code=400, detail="Cập nhật chuỗi dòng bị lỗi hoặc kích hoạt Rollback.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# router lấy dữ liệu của bảng
@database_routes.get("/table/{table_name}")
async def get_table_data(table_name: str):
    """API lấy toàn bộ dữ liệu của một bảng chỉ định (Có chốt chặn kiểm tra tồn tại)."""
    
    # 1. Lấy danh sách các bảng thực tế đang có trong DB
    valid_tables = get_all_table_names(DB_PATH)
    
    # 2. Nếu tên bảng truyền vào không nằm trong DB, chặn lại và báo lỗi 404 ngay
    if table_name not in valid_tables:
        raise HTTPException(
            status_code=404, 
            detail=f"Thất bại: Thiên Cơ Lục không tồn tại bảng nào có tên là [{table_name}]."
        )
        
    # 3. Nếu bảng hợp lệ, tiến hành bốc dữ liệu và trả về cho client
    data = get_all_rows_from_table(DB_PATH, table_name)
    return {
        "status": "success",
        "table": table_name, 
        "total_rows": len(data),
        "data": data
    }
