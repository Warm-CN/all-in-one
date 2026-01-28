"""
FastAPI 应用主入口
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.database import engine, Base
from app.schemas.response import error_response

# 导入路由
from app.api.v1 import auth, signups, room_bookings, admin, users, admin_bookings, schedules, admin_schedules

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="基于 FastAPI 的社团统一管理系统 - 支持 RBAC 权限控制",
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    # 创建所有数据库表
    Base.metadata.create_all(bind=engine)
    print(f"✅ {settings.APP_NAME} v{settings.APP_VERSION} 启动成功！")
    print(f"📚 API 文档: http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    print(f"👋 {settings.APP_NAME} 已关闭")


# ==================== 全局异常处理 ====================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理，统一返回格式"""
    return JSONResponse(
        status_code=500,
        content=error_response(500, f"服务器内部错误: {str(exc)}")
    )


# ==================== 路由注册 ====================

# 认证路由
app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["🔐 认证"]
)

# 报名系统路由（场景 A：公开接口）
app.include_router(
    signups.router,
    prefix="/api/v1/signups",
    tags=["📝 报名系统（公开）"]
)

# 会议室日常预约路由（简化版 - 无需审批）
app.include_router(
    room_bookings.router,
    tags=["📅 会议室预约（日常）"]
)

# 管理员用户管理路由
app.include_router(
    admin.router,
    tags=["👨‍💼 管理员-用户管理"]
)

# 管理员会议室管理路由
app.include_router(
    admin_bookings.router,
    prefix="/api/v1/admin/bookings",
    tags=["📅 管理员-会议室管理"]
)

# 通讯录/用户查询路由
app.include_router(
    users.router,
    prefix="/api/v1/users",
    tags=["👥 通讯录"]
)

# 日程查询路由（所有用户）
app.include_router(
    schedules.router,
    tags=["📅 日程查询"]
)

# 管理员日程管理路由
app.include_router(
    admin_schedules.router,
    tags=["📅 管理员-日程管理"]
)


# ==================== 基础路由 ====================


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": f"欢迎使用{settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "features": [
            "✅ JWT 身份认证",
            "✅ RBAC 权限控制",
            "✅ 用户注册与登录",
            "✅ 会议室预约系统",
            "✅ 灵活报名系统"
        ]
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "version": settings.APP_VERSION}
