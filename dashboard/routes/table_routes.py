import sqlite3
import json
from fastapi import APIRouter, HTTPException

from dashboard.auth import DB_PATH

table_api_router = APIRouter()

@table_api_router.get("/main")
async def get_main_table_data(table: str):
    """[Call lần 1] - Đọc dữ liệu tĩnh, chính thức từ SQLite gốc (Quyền Read-only)"""
    if table.startswith("sys_"):
        raise HTTPException(status_code=403, detail="Không được phép can thiệp bảng hệ thống!")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute(f"PRAGMA table_info({table});")
        columns = [row[1] for row in cursor.fetchall()]
        if not columns:
            raise HTTPException(status_code=404, detail=f"Bảng hệ thống game `{table}` chưa tồn tại.")

        cursor.execute(f"SELECT * FROM {table};")
        rows = [dict(row) for row in cursor.fetchall()]
        return {"columns": columns, "rows": rows}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Lỗi SQLite: {e}") from e
    finally:
        conn.close()

@table_api_router.get("/temp")
async def get_temp_table_data(table: str, user_id: int):
    """[Call lần 2] - Đọc dữ liệu bản tạm của chính account tạo ra phục vụ bọc khung xanh lá"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT id, final_data FROM sys_pending_changes
            WHERE user_id = ? AND system_id = ? AND status NOT IN ('DONE', 'REJECT');
            """,
            (user_id, table)
        )
        raw_rows = cursor.fetchall()

        parsed_rows = []
        for r in raw_rows:
            row_dict = json.loads(r["final_data"])
            row_dict["_change_id"] = r["id"]
            parsed_rows.append(row_dict)

        return {"rows": parsed_rows}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Lỗi đọc DB tạm: {e}") from e
    finally:
        conn.close()
