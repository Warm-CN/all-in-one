"""
认证相关的 Schema 定义
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class LoginRequest(BaseModel):
    """登录请求"""
    student_id: str = Field(..., description="学号", example="admin")
    password: str = Field(..., description="密码", example="123456")


class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")


class UserInfo(BaseModel):
    """用户信息"""
    id: int
    real_name: str
    student_id: str
    phone: str
    email: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    birthday: Optional[date] = None
    role: str
    status: str
    avatar: Optional[str] = None
    
    class Config:
        from_attributes = True


class RegisterRequest(BaseModel):
    """注册请求"""
    real_name: str = Field(..., min_length=2, max_length=50, description="真实姓名")
    student_id: str = Field(..., min_length=5, max_length=20, description="学号")
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$", description="手机号")
    email: Optional[str] = Field(None, description="邮箱")
    department: Optional[str] = Field(None, description="部门")
    
    
class PasswordResetRequest(BaseModel):
    """重置密码请求（管理员用）"""
    user_id: int = Field(..., description="用户ID")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")


class PasswordChangeRequest(BaseModel):
    """修改密码请求（用户自己）"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")
