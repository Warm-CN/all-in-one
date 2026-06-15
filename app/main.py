"""
FastAPI 应用主入口
"""
from datetime import datetime, timedelta
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.schemas.response import error_response
from app.models.signup import SignupConfig

# 速率限制器（基于客户端 IP）
limiter = Limiter(key_func=get_remote_address)

# 导入路由
from app.api.v1 import auth, signups, room_bookings, admin, users, admin_bookings, schedules, admin_schedules, teams, competitions

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="基于 FastAPI 的社团统一管理系统 - 支持 RBAC 权限控制",
)

# 配置速率限制
app.state.limiter = limiter

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

upload_dir = Path("uploads")
upload_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    # 创建所有数据库表
    Base.metadata.create_all(bind=engine)
    ensure_default_signup_config()
    print(f"✅ {settings.APP_NAME} v{settings.APP_VERSION} 启动成功！")
    print(f"📚 API 文档: http://localhost:8000/docs")


def ensure_default_signup_config():
    """开发环境下自动生成一个招新活动，避免前端无活动可演示。"""
    if not settings.DEBUG:
        return

    db = SessionLocal()
    try:
        now = datetime.now()
        active_exists = db.query(SignupConfig).filter(
            SignupConfig.is_active == True,
            SignupConfig.start_time <= now,
            SignupConfig.end_time >= now,
            SignupConfig.category.in_(["recruitment", "招新"])
        ).first()

        if active_exists:
            return

        config = SignupConfig(
            title="2026 春季协会招新",
            description="欢迎报名协会，提交后可在公开页面查询进度与面试安排。",
            start_time=now - timedelta(days=1),
            end_time=now + timedelta(days=20),
            max_participants=None,
            is_active=True,
            category="recruitment",
            form_fields=[
                {"name": "姓名", "type": "text", "required": True},
                {"name": "手机号", "type": "text", "required": True},
                {"name": "邮箱", "type": "text", "required": True},
                {"name": "学院", "type": "text", "required": True},
                {"name": "专业班级", "type": "text", "required": True},
                {"name": "第一志愿", "type": "select", "required": True},
                {"name": "第二志愿", "type": "select", "required": False},
                {"name": "服从调剂", "type": "radio", "required": True},
                {"name": "自我介绍", "type": "textarea", "required": False}
            ]
        )
        db.add(config)
        db.commit()
        print("✅ 已自动创建默认招新活动（DEBUG模式）")
    except Exception as exc:
        db.rollback()
        print(f"⚠️ 默认招新活动创建失败: {exc}")
    finally:
        db.close()


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    print(f"👋 {settings.APP_NAME} 已关闭")


# ==================== 全局异常处理 ====================

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """速率限制超出处理"""
    return JSONResponse(
        status_code=429,
        content=error_response(429, "请求过于频繁，请稍后再试")
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理，统一返回格式（不泄露内部信息）"""
    if settings.DEBUG:
        import traceback
        traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content=error_response(500, "服务器内部错误，请联系管理员")
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

# 竞赛队伍模块路由
app.include_router(
    teams.router,
    prefix="/api/v1",
    tags=["🏆 竞赛队伍"]
)

# 比赛历史与配置路由
app.include_router(
    competitions.router,
    prefix="/api/v1",
    tags=["🏁 比赛历史与配置"]
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
