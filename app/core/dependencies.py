"""
权限依赖
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User, UserRole

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前登录用户"""
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据"
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据"
        )
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return user


def require_active_user(current_user: User = Depends(get_current_user)) -> User:
    """要求用户状态为激活"""
    from app.models.user import UserStatus
    if current_user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号未激活或已被停用"
        )
    return current_user


def require_role(required_role: UserRole):
    """要求特定角色（或更高权限）"""
    role_hierarchy = {
        UserRole.VISITOR: 0,
        UserRole.MEMBER: 1,
        UserRole.ADMIN: 2
    }
    
    def role_checker(current_user: User = Depends(require_active_user)) -> User:
        user_level = role_hierarchy.get(current_user.role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要 {required_role.value} 或更高权限"
            )
        return current_user
    
    return role_checker


# 便捷的角色检查器
require_member = require_role(UserRole.MEMBER)
require_admin = require_role(UserRole.ADMIN)
