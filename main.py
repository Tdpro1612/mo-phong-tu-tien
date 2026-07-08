# main.py
import os
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi.security import APIKeyHeader
from webui.routes import webui_router
from dashboard.main_router import dashboard_router
from database.database_routes import database_routes
from fastapi.responses import FileResponse


app = FastAPI(title="Thiên Cơ Lục")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE_PATH = os.path.join(BASE_DIR, "webui", "home.html")

# Nạp các biến môi trường từ file .env vào hệ thống
load_dotenv()
header_scheme = APIKeyHeader(name="X-Dashboard-Token", auto_error=False)
# Lấy mã khóa bí mật từ .env ra, nếu không có thì dùng 1 chuỗi mặc định để tránh lỗi sập nguồn
DASHBOARD_TOKEN = os.getenv("DASHBOARD_SECRET_TOKEN", "default_fallback_token_2026")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------------------
# 🛡️ MÔN VỆ BẢO VỆ: KIỂM TRA QUYỀN DASHBOARD (CHỈ CHẶN LỆNH GHI/XÓA)
# ------------------------------------------------------------------------------
async def dashboard_security_gate(
    request: Request,
    token: str = Depends(header_scheme) # 👈 FastAPI sẽ tự bốc từ ổ khóa Docs hoặc Header vào đây
):
    if request.method in ["POST", "PUT", "DELETE"]:
        # DASHBOARD_TOKEN lấy từ .env của bạn
        if not token or token != DASHBOARD_TOKEN:
            raise HTTPException(
                status_code=401, 
                detail="Cảnh báo: Đạo hữu không có thẩm quyền can thiệp vào Thiên Cơ Lục!"
            )

# ------------------------------------------------------------------------------
# 1. ĐĂNG KÝ ROUTERS (ĐIỀU HƯỚNG HỆ THỐNG ĐÃ PHÂN CẤP)
# ------------------------------------------------------------------------------
# Cụm Router của WebUI (Thoải mái hoàn toàn)
app.include_router(webui_router)

# Cụm Router của Dashboard (Dành cho quản trị viên)
app.include_router(dashboard_router, prefix="/dashboard")

# Cụm Router của Database (Siết bảo mật tự động bằng Môn Vệ dựa theo Method)
app.include_router(
    database_routes,
    prefix="/db",
    dependencies=[Depends(dashboard_security_gate)] # 👈 Áp giáp bảo vệ ở đây!
)

# ------------------------------------------------------------------------------
# 2. MOUNT TÀI NGUYÊN TĨNH (STATIC FILES)
# ------------------------------------------------------------------------------
app.mount("/webui", StaticFiles(directory=os.path.join(BASE_DIR, "webui")), name="webui_assets")
app.mount("/dashboard/ui", StaticFiles(directory=os.path.join(BASE_DIR, "dashboard", "ui")), name="dashboard_ui_assets")



@app.get("/")
async def serve_home():
    if os.path.exists(HTML_FILE_PATH):
        return FileResponse(HTML_FILE_PATH)
    return {"status": "error", "message": "Không tìm thấy file home.html"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
