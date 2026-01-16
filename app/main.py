"""
FastAPI 应用主入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="基于 FastAPI 的社团统一管理系统",
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


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    print(f"👋 {settings.APP_NAME} 已关闭")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": f"欢迎使用{settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


# TODO: 引入路由
# from app.api.v1 import auth, users, rooms, bookings, signups
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
# app.include_router(users.router, prefix="/api/v1/users", tags=["用户"])
# app.include_router(rooms.router, prefix="/api/v1/rooms", tags=["会议室"])
# app.include_router(bookings.router, prefix="/api/v1/bookings", tags=["预约"])
# app.include_router(signups.router, prefix="/api/v1/signups", tags=["报名"])
