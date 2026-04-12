"""
Schema 包初始化
"""
from app.schemas.response import ResponseModel, success_response, error_response
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    UserInfo,
    RegisterRequest,
    PasswordResetRequest,
    PasswordChangeRequest
)
from app.schemas.schedule import ScheduleCreate, ScheduleResponse

__all__ = [
    "ResponseModel",
    "success_response",
    "error_response",
    "LoginRequest",
    "TokenResponse",
    "UserInfo",
    "RegisterRequest",
    "PasswordResetRequest",
    "PasswordChangeRequest",
    "ScheduleCreate",
    "ScheduleResponse",
]
