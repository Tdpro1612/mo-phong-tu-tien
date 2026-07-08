# dashboard/routes.py
from fastapi import APIRouter

# Import các Router con từ các file vừa tách biệt
from dashboard.routes.auth_routes import auth_router
from dashboard.routes.view_routes import view_router
from dashboard.routes.table_routes import table_api_router
from dashboard.routes.proposal_routes import proposal_router

dashboard_router = APIRouter()

# 1. Nhóm điều hướng Giao diện chính (Màn hình Jinja2)
dashboard_router.include_router(view_router)

# 2. Nhóm Auth (Login/Logout/Register)
dashboard_router.include_router(auth_router)

# 3. Nhóm API quản lý dữ liệu bảng (Prefix đồng bộ để JS fetch chuẩn xác)
dashboard_router.include_router(table_api_router, prefix="/api/table-data")

# 4. Nhóm API xử lý biến động và sảnh chờ thẩm định
dashboard_router.include_router(proposal_router, prefix="/api")