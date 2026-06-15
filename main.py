# main.py
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from webui.routes import webui_router

app = FastAPI(title="Thiên Cơ Lục - Data Engine")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. Kích hoạt cụm router của WebUI (Không để prefix="/api" ở đây nữa, để router tự quyết định)
app.include_router(webui_router)

# 2. Mount thư mục webui để trình duyệt có thể tải các file style.css, app.js
# Khi gọi trong HTML: src="/webui/app.js" hoặc href="/webui/style.css"
app.mount(
    "/webui",
    StaticFiles(directory=os.path.join(BASE_DIR, "webui")),
    name="webui_assets",
)
