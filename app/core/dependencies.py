"""
权限依赖与身份验证
实现 RBAC (基于角色的权限控制)
"""
from typing import List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User, UserRole, UserStatus

# HTTP Bearer Token 认证
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前登录用户（身份验证依赖项）
    
    从请求头的 Authorization 中提取 Token 并验证
    如果 Token 无效或过期，抛出 401 异常
    
    Args:
        credentials: HTTP Bearer 凭证
        db: 数据库会话
        
    Returns:
        User: 当前登录的用户对象
        
    Raises:
        HTTPException: 401 - Token 无效或用户不存在
    """
    # 提取 Token
    token = credentials.credentials
    
    # 解码 Token
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据或 Token 已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 从 Payload 中获取用户 ID
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 格式错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 查询用户
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    获取当前激活的用户
    
    验证用户状态是否为 ACTIVE
    
    Args:
        current_user: 当前登录用户
        
    Returns:
        User: 已激活的用户对象
        
    Raises:
        HTTPException: 403 - 账号未激活或已停用
    """
    if current_user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"账号状态异常：{current_user.status.value}，请联系管理员"
        )
    return current_user


class RoleChecker:
    """
    角色检查器（灵活的 RBAC 权限控制）
    
    使用方式：
        - Depends(RoleChecker(["admin"])) - 仅限 Admin
        - Depends(RoleChecker(["member", "admin"])) - Member 或 Admin 都可以
    """
    
    def __init__(self, allowed_roles: List[str]):
        """
        初始化角色检查器
        
        Args:
            allowed_roles: 允许的角色列表，例如 ["member", "admin"]
        """
        self.allowed_roles = [role.lower() for role in allowed_roles]
    
    def __call__(self, current_user: User = Depends(get_current_active_user)) -> User:
        """
        检查用户角色是否在允许的角色列表中
        
        Args:
            current_user: 当前已激活的用户
            
        Returns:
            User: 通过权限检查的用户对象
            
        Raises:
            HTTPException: 403 - 权限不足
        """
        user_role = current_user.role.value.lower()
        
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足：需要 {' 或 '.join(self.allowed_roles)} 角色"
            )
        
        return current_user


# ==================== 便捷的角色检查器实例 ====================

# 仅限访客（一般不会用到，因为访客权限最低）
require_visitor = RoleChecker(["visitor"])

# 需要 Member 或更高权限（Member 和 Admin 都可以）
require_member = RoleChecker(["member", "admin"])

# 仅限 Admin
require_admin = RoleChecker(["admin"])
