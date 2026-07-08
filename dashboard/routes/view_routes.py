import os
import sqlite3
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from dashboard.auth import (
    DB_PATH,
    get_all_game_systems,
    get_user_permissions
)

view_router = APIRouter()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "ui"))

@view_router.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request, role: str = "viewer"):
    valid_roles = ['root', 'admin', 'manager', 'reviewer', 'staff', 'commentor', 'viewer']
    user_role = role if role in valid_roles else "viewer"

    if user_role in ['root', 'admin', 'manager', 'commentor']:
        allowed_systems = get_all_game_systems()
    elif user_role in ['reviewer', 'staff']:
        allowed_systems = []
        if os.path.exists(DB_PATH):
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            user_id = request.query_params.get("user_id")
            if user_id:
                allowed_systems = get_user_permissions(cursor, user_id)
            conn.close()
    else:
        allowed_systems = []

    return templates.TemplateResponse(
        request=request, name="index.html",
        context={"user_role": user_role, "allowed_systems": allowed_systems, "is_permission_view": False, "is_review_view": False}
    )

@view_router.get("/permissions", response_class=HTMLResponse)
async def permissions_page(request: Request, role: str = "viewer"):
    if role not in ['root', 'admin', 'manager']:
        return HTMLResponse(content="<h1>🛑 Bản lĩnh chưa đủ để truy cập mật cảnh phân quyền!</h1>", status_code=403)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if role == 'root':
        cursor.execute("SELECT id, username, role FROM sys_users WHERE role != 'root';")
    elif role == 'admin':
        cursor.execute("SELECT id, username, role FROM sys_users WHERE role NOT IN ('root', 'admin');")
    elif role == 'manager':
        cursor.execute("SELECT id, username, role FROM sys_users WHERE role NOT IN ('root', 'admin', 'manager');")

    raw_users = cursor.fetchall()
    users_with_perms = []
    for u in raw_users:
        user_id = u["id"]
        cursor.execute("SELECT system_id FROM sys_permissions WHERE user_id = ?;", (user_id,))
        allowed_systems = [row[0] for row in cursor.fetchall()]

        users_with_perms.append({
            "id": user_id,
            "username": u["username"],
            "role": u["role"],
            "allowed_systems": allowed_systems
        })
    conn.close()

    return templates.TemplateResponse(
        request=request, name="index.html",
        context={
            "user_role": role,
            "is_permission_view": True,
            "is_review_view": False,
            "users": users_with_perms,
            "all_systems": get_all_game_systems()
        }
    )

@view_router.get("/review", response_class=HTMLResponse)
async def review_page(request: Request, role: str = "viewer"):
    if role not in ['root', 'admin', 'manager', 'reviewer']:
        return HTMLResponse(content="<h1>🛑 Bản lĩnh chưa đủ để vào sảnh phê duyệt!</h1>", status_code=403)
    return templates.TemplateResponse(
        request=request, name="index.html",
        context={"user_role": role, "allowed_systems": [], "is_permission_view": False, "is_review_view": True}
    )
