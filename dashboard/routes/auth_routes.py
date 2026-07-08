import os
import time
import sqlite3
import hashlib
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from dashboard.auth import (
    authenticate_user,
    DB_PATH,
    check_username_available
)

auth_router = APIRouter()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "ui"))

@auth_router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@auth_router.post("/login")
async def handle_login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = authenticate_user(username, password)
    if not user:
        error_msg = "Tên đăng nhập hoặc mật khẩu không chính xác!"
        if os.path.exists(DB_PATH):
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT expired_at FROM sys_users WHERE username = ?;", (username,))
            row = cursor.fetchone()
            conn.close()
            if row and row[0] is not None and int(time.time()) > int(row[0]):
                error_msg = "Tài khoản của bạn đã hết hạn truy cập hệ thống. Vui lòng liên hệ Admin!"
        return templates.TemplateResponse(request=request, name="login.html", context={"error": error_msg})
    return RedirectResponse(url=f"/dashboard?role={user['role']}&user_id={user['id']}", status_code=303)

@auth_router.get("/logout")
async def handle_logout():
    return RedirectResponse(url="/dashboard/login", status_code=303)

@auth_router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")

@auth_router.post("/register")
async def handle_register(request: Request, username: str = Form(...), password: str = Form(...)):
    if not check_username_available(username):
        return templates.TemplateResponse(
            request=request, name="register.html",
            context={"error": f"User `{username}` đã tồn tại trên hệ thống!"}
        )

    if len(password) < 6:
        return templates.TemplateResponse(
            request=request, name="register.html",
            context={"error": "Mật khẩu phải dài từ 6 ký tự trở lên!"}
        )

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
        expired_at = int(time.time()) + (30 * 86400)

        cursor.execute(
            "INSERT INTO sys_users (username, password_hash, role, expired_at) VALUES (?, ?, 'commentor', ?);",
            (username, password_hash, expired_at)
        )
        conn.commit()
        return templates.TemplateResponse(
            request=request, name="register.html",
            context={"success": "Đăng ký thành công."}
        )
    except sqlite3.Error as e:
        return templates.TemplateResponse(request=request, name="register.html", context={"error": f"Lỗi: {e}"})
    finally:
        conn.close()
