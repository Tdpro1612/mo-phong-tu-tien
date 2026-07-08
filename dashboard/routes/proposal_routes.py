import sqlite3
import json
import time
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

from dashboard.auth import DB_PATH

proposal_router = APIRouter()

class ProposeChangePayload(BaseModel):
    user_id: int
    system_id: str      
    action: str         
    primary_key_val: str 
    final_data: str     

@proposal_router.post("/propose-change")
async def propose_change(payload: ProposeChangePayload):
    route_conn = sqlite3.connect(DB_PATH)
    route_cursor = route_conn.cursor()
    try:
        target_row_id = int(payload.primary_key_val) if payload.primary_key_val else None

        route_cursor.execute(
            """
            SELECT id FROM sys_pending_changes 
            WHERE user_id = ? AND system_id = ? AND row_id = ? AND status = ?;
            """,
            (payload.user_id, payload.system_id, target_row_id, payload.action)
        )
        existing = route_cursor.fetchone()

        if existing:
            route_cursor.execute(
                """
                UPDATE sys_pending_changes 
                SET final_data = ?, created_at = strftime('%s', 'now')
                WHERE id = ?;
                """,
                (payload.final_data, existing[0])
            )
            msg = f"Đã cập nhật đè dữ liệu mới vào đề xuất {payload.action} cũ đang chờ duyệt!"
        else:
            route_cursor.execute(
                """
                INSERT INTO sys_pending_changes (system_id, row_id, user_id, final_data, status, history_log)
                VALUES (?, ?, ?, ?, ?, '{}');
                """,
                (payload.system_id, target_row_id, payload.user_id, payload.final_data, payload.action)
            )
            msg = f"Đã đưa đề xuất {payload.action} vào Thiên Cơ Lục bản tạm chờ duyệt!"
            
        route_conn.commit()
        return {"status": "success", "message": msg}
    except sqlite3.Error as e:
        route_conn.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi trận pháp ghi bản tạm: {e}") from e
    finally:
        route_conn.close()

@proposal_router.get("/review/list")
async def get_review_list(role: str, user_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        if role in ['root', 'admin', 'manager']:
            cursor.execute("SELECT id, system_id, history_log, final_data FROM sys_pending_changes WHERE status = 'REVIEWED';")
        elif role == 'reviewer':
            cursor.execute("SELECT system_id FROM sys_permissions WHERE user_id = ?;", (user_id,))
            allowed = [r[0] for r in cursor.fetchall()]
            if not allowed: return {"rows": []}
            placeholders = ",".join("?" for _ in allowed)
            cursor.execute(
                f"SELECT id, system_id, history_log, final_data FROM sys_pending_changes WHERE system_id IN ({placeholders}) AND status IN ('NEW', 'EDIT', 'DELETE');",
                allowed
            )
        else:
            return {"rows": []}

        rows = cursor.fetchall()
        result = []
        for r in rows:
            history = json.loads(r["history_log"])
            old_snapshot = history[0]["snapshot"] if history else {}
            final_snapshot = json.loads(r["final_data"])

            result.append({
                "change_id": r["id"],
                "system_id": r["system_id"],
                "old_data": old_snapshot,
                "final_data": final_snapshot
            })
        return {"rows": result}
    finally:
        conn.close()

@proposal_router.get("/review/detail/{change_id}")
async def get_review_detail(change_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT history_log FROM sys_pending_changes WHERE id = ?;", (change_id,))
        row = cursor.fetchone()
        if not row: raise HTTPException(status_code=404, detail="Không tìm thấy lịch sử thay đổi.")
        return {"history": json.loads(row[0])}
    finally:
        conn.close()

@proposal_router.post("/review/action")
async def handle_review_action(data: dict):
    change_id = data.get("change_id")
    action = data.get("action") 
    operator_role = data.get("role")
    operator_name = data.get("username", "Unknown")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        if action == "REJECT":
            cursor.execute("UPDATE sys_pending_changes SET status = 'REJECT' WHERE id = ?;", (change_id,))
        elif action == "ACCEPT":
            target_status = "ACCEPTED" if operator_role in ['root', 'admin', 'manager'] else "REVIEWED"
            cursor.execute("UPDATE sys_pending_changes SET status = ? WHERE id = ?;", (target_status, change_id))
        elif action == "ROLLBACK":
            selected_version = data.get("selected_version")
            cursor.execute("SELECT history_log FROM sys_pending_changes WHERE id = ?;", (change_id,))
            row = cursor.fetchone()
            if row:
                history = json.loads(row[0])
                target_snapshot = next((v["snapshot"] for v in history if v["version"] == selected_version), None)
                if target_snapshot:
                    new_final = json.dumps(target_snapshot, ensure_ascii=False)
                    new_version_num = len(history) + 1
                    history.append({
                        "version": new_version_num,
                        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                        "account_id": data.get("user_id"),
                        "username": operator_name,
                        "action": f"ROLLBACK_TO_V{selected_version}",
                        "snapshot": target_snapshot
                    })
                    cursor.execute(
                        "UPDATE sys_pending_changes SET final_data = ?, history_log = ? WHERE id = ?;",
                        (new_final, json.dumps(history, ensure_ascii=False), change_id)
                    )
        conn.commit()
        return {"status": "success"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e)) from e
    finally:
        conn.close()

@proposal_router.post("/review/push-main")
async def push_accepted_to_main_db(data: dict):
    operator_name = data.get("username", "Unknown")
    system_id = data.get("system_id")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, row_id, final_data, history_log FROM sys_pending_changes WHERE system_id = ? AND status = 'ACCEPTED';",
            (system_id,)
        )
        pending_items = cursor.fetchall()
        if not pending_items:
            return {"status": "success", "message": "Không có dữ liệu nào ở trạng thái ACCEPTED để đẩy."}

        for item in pending_items:
            change_id, row_id, final_data, history_log = item
            final_snapshot = json.loads(final_data)
            history = json.loads(history_log)
            action_type = history[0]["action"]

            if action_type == "NEW":
                columns = ", ".join(final_snapshot.keys())
                placeholders = ", ".join("?" for _ in final_snapshot)
                cursor.execute(f"INSERT INTO {system_id} ({columns}) VALUES ({placeholders});", list(final_snapshot.values()))
            elif action_type == "EDIT":
                set_clause = ", ".join(f"{k} = ?" for k in final_snapshot.keys())
                params = list(final_snapshot.values()) + [row_id]
                cursor.execute(f"UPDATE {system_id} SET {set_clause} WHERE id = ?;", params)
            elif action_type == "DELETE":
                cursor.execute(f"DELETE FROM {system_id} WHERE id = ?;", (row_id,))

            cursor.execute("UPDATE sys_pending_changes SET status = 'DONE' WHERE id = ?;", (change_id,))

        cursor.execute(
            "INSERT INTO sys_audit_logs (username, action, details) VALUES (?, 'PUSH_TO_DB', ?);",
            (operator_name, f"Đã đẩy hàng loạt {len(pending_items)} bản ghi vào bảng `{system_id}`")
        )
        conn.commit()
        return {"status": "success", "message": f"Kích hoạt thành công! Đã đồng bộ {len(pending_items)} dòng vào DB gốc."}
    except sqlite3.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Thất bại trong Bulk Write: {e}") from e
    finally:
        conn.close()

@proposal_router.post("/api/save-permissions")
async def save_permissions_api(data: dict, request: Request):
    user_id = data.get("user_id")
    new_role = data.get("role")
    systems = data.get("systems", [])
    current_operator_role = request.query_params.get("role", "viewer")

    if current_operator_role == 'manager' and new_role in ['manager', 'admin', 'root']:
        raise HTTPException(status_code=403, detail="Manager không được phép phong cấp lên Manager hoặc cao hơn!")
    if current_operator_role == 'admin' and new_role in ['admin', 'root']:
        raise HTTPException(status_code=403, detail="Admin không được phép phong cấp lên Admin hoặc cao hơn!")

    if not user_id or not new_role:
        raise HTTPException(status_code=400, detail="Thiếu thông tin ID hoặc Chức vụ.")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE sys_users SET role = ? WHERE id = ?;", (new_role, user_id))
        cursor.execute("DELETE FROM sys_permissions WHERE user_id = ?;", (user_id,))
        for sys_id in systems:
            cursor.execute("INSERT INTO sys_permissions (user_id, system_id) VALUES (?, ?);", (user_id, sys_id))
        conn.commit()
        return {"status": "success", "message": "Cập nhật sắc phong chức vụ thành công!"}
    except sqlite3.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi DB: {e}") from e
    finally:
        conn.close()
