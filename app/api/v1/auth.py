"""
认证相关路由
包含登录、注册、修改密码等功能
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.dependencies import get_current_active_user, require_admin
from app.core.config import settings
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    UserInfo,
    RegisterRequest,
    PasswordChangeRequest,
    PasswordResetRequest
)
from app.schemas.response import success_response, error_response

router = APIRouter()


@router.post("/login", response_model=dict, summary="用户登录")
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    用户登录接口
    
    - **student_id**: 学号（例如：admin）
    - **password**: 密码（例如：123456）
    
    返回 JWT Token，Payload 包含：
    - sub: 用户ID
    - role: 用户角色
    """
    # 查询用户
    user = db.query(User).filter(User.student_id == login_data.student_id).first()
    
    if not user:
        return error_response(401, "学号或密码错误")
    
    # 验证密码
    if not verify_password(login_data.password, user.password_hash):
        return error_response(401, "学号或密码错误")
    
    # 检查用户状态
    if user.status == 'pending':
        return error_response(403, "账号待审核，请联系管理员")
    elif user.status in ['rejected', 'disabled']:
        return error_response(403, "账号已停用，请联系管理员")
    
    # 生成 JWT Token
    token_data = {
        "sub": str(user.id),  # 用户ID
        "role": user.role,  # 用户角色
        "student_id": user.student_id  # 学号（可选，方便调试）
    }
    access_token = create_access_token(data=token_data)
    
    # 构造响应数据
    token_response = TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # 转换为秒
    )
    
    return success_response(
        data={
            "token": token_response.dict(),
            "user": UserInfo.from_orm(user).dict()
        },
        msg="登录成功"
    )


@router.post("/register", response_model=dict, summary="用户注册")
async def register(
    register_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    用户注册接口
    
    注册后状态为 PENDING（待审核），需要管理员激活
    """
    # 检查学号是否已存在
    existing_user = db.query(User).filter(User.student_id == register_data.student_id).first()
    if existing_user:
        return error_response(400, "该学号已被注册")
    
    # 检查手机号是否已存在
    existing_phone = db.query(User).filter(User.phone == register_data.phone).first()
    if existing_phone:
        return error_response(400, "该手机号已被注册")
    
    # 检查邮箱是否已存在（如果提供了邮箱）
    if register_data.email:
        existing_email = db.query(User).filter(User.email == register_data.email).first()
        if existing_email:
            return error_response(400, "该邮箱已被注册")
    
    # 创建新用户
    new_user = User(
        full_name=register_data.full_name,
        student_id=register_data.student_id,
        password_hash=get_password_hash(register_data.password),
        phone=register_data.phone,
        email=register_data.email,
        department=register_data.department,
        role='member',  # 默认为成员
        status='pending'  # 待审核
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return success_response(
        data=UserInfo.from_orm(new_user).dict(),
        msg="注册成功，请等待管理员审核"
    )


@router.get("/me", response_model=dict, summary="获取当前用户信息")
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当前登录用户的详细信息
    
    需要提供有效的 JWT Token
    """
    return success_response(
        data=UserInfo.from_orm(current_user).dict(),
        msg="获取成功"
    )


@router.put("/password", response_model=dict, summary="修改密码")
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    用户修改自己的密码
    
    需要提供旧密码和新密码
    """
    # 验证旧密码
    if not verify_password(password_data.old_password, current_user.password_hash):
        return error_response(400, "旧密码错误")
    
    # 更新密码
    current_user.password_hash = get_password_hash(password_data.new_password)
    db.commit()
    
    return success_response(msg="密码修改成功，请重新登录")


@router.post("/reset-password", response_model=dict, summary="重置他人密码（仅管理员）")
async def reset_user_password(
    reset_data: PasswordResetRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    管理员重置他人密码
    
    场景 C：仅限 Admin 权限
    """
    # 查询目标用户
    target_user = db.query(User).filter(User.id == reset_data.user_id).first()
    if not target_user:
        return error_response(404, "用户不存在")
    
    # 不允许重置自己的密码（应该用修改密码接口）
    if target_user.id == current_user.id:
        return error_response(400, "请使用修改密码接口")
    
    # 重置密码
    target_user.password_hash = get_password_hash(reset_data.new_password)
    db.commit()
    
    return success_response(
        msg=f"已重置用户 {target_user.full_name}({target_user.student_id}) 的密码"
    )


@router.post("/approve/{user_id}", response_model=dict, summary="审核通过用户（仅管理员）")
async def approve_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    管理员审核通过用户注册
    
    将用户状态从 PENDING 改为 ACTIVE，并升级为 MEMBER
    """
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        return error_response(404, "用户不存在")
    
    if target_user.status != UserStatus.PENDING:
        return error_response(400, f"用户当前状态为 {target_user.status.value}，无需审核")
    
    # 激活用户并设置为 Member
    target_user.status = UserStatus.ACTIVE
    target_user.role = UserRole.MEMBER
    db.commit()
    
    return success_response(
        data=UserInfo.from_orm(target_user).dict(),
        msg=f"已激活用户 {target_user.full_name}"
    )
