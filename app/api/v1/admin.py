"""
管理员用户管理接口
提供待审核用户列表、审核通过、审核拒绝等功能
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.auth import UserInfo
from app.schemas.response import success_response, error_response

router = APIRouter(prefix="/api/admin", tags=["管理员-用户管理"])


@router.get("/users/pending", response_model=dict, summary="获取待审核用户列表")
async def get_pending_users(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    获取所有待审核的用户列表
    
    权限：仅管理员
    返回：所有 status == 'pending' 的用户
    """
    pending_users = db.query(User).filter(
        User.status == 'pending'
    ).order_by(User.created_at.desc()).all()
    
    users_data = [UserInfo.from_orm(user).dict() for user in pending_users]
    
    return success_response(
        data=users_data,
        msg=f"共 {len(users_data)} 个待审核用户"
    )


@router.post("/users/approve/{user_id}", response_model=dict, summary="审核通过用户")
async def approve_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    审核通过指定用户
    
    权限：仅管理员
    操作：将 status 改为 'active'，role 改为 'member'
    """
    target_user = db.query(User).filter(User.id == user_id).first()
    
    if not target_user:
        return error_response(404, "用户不存在")
    
    if target_user.status != 'pending':
        return error_response(400, f"用户当前状态为 {target_user.status}，无法审核")
    
    # 激活用户
    target_user.status = 'active'
    target_user.role = 'member'
    db.commit()
    db.refresh(target_user)
    
    return success_response(
        data=UserInfo.from_orm(target_user).dict(),
        msg=f"已通过 {target_user.full_name} 的注册申请"
    )


@router.post("/users/reject/{user_id}", response_model=dict, summary="拒绝用户注册")
async def reject_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    拒绝指定用户的注册申请
    
    权限：仅管理员
    操作：将 status 改为 'inactive'
    """
    target_user = db.query(User).filter(User.id == user_id).first()
    
    if not target_user:
        return error_response(404, "用户不存在")
    
    if target_user.status != 'pending':
        return error_response(400, f"用户当前状态为 {target_user.status}，无法拒绝")
    
    # 拒绝用户
    target_user.status = 'rejected'
    db.commit()
    db.refresh(target_user)
    
    return success_response(
        data=UserInfo.from_orm(target_user).dict(),
        msg=f"已拒绝 {target_user.full_name} 的注册申请"
    )


@router.get("/users", response_model=dict, summary="获取用户列表（支持搜索和筛选）")
async def get_all_users(
    status: str = None,
    keyword: str = None,
    department: str = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    获取用户列表，支持按状态、关键词、部门筛选
    
    权限：仅管理员
    参数：
    - status: pending/active/inactive
    - keyword: 按姓名或学号搜索
    - department: 部门筛选
    """
    query = db.query(User)
    
    if status:
        # 直接使用字符串比较
        if status not in ['pending', 'active', 'rejected', 'disabled']:
            return error_response(400, f"无效的状态值: {status}")
        query = query.filter(User.status == status)
    
    if keyword:
        query = query.filter(
            (User.full_name.contains(keyword)) | (User.student_id.contains(keyword))
        )
    
    if department:
        query = query.filter(User.department == department)
    
    users = query.order_by(User.created_at.desc()).all()
    users_data = [UserInfo.from_orm(user).dict() for user in users]
    
    return success_response(
        data=users_data,
        msg=f"共 {len(users_data)} 个用户"
    )


@router.post("/users/approve", response_model=dict, summary="批量审核通过用户")
async def batch_approve_users(
    user_ids: List[int],
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    批量审核通过多个用户
    
    权限：仅管理员
    参数：user_ids - 用户ID列表
    """
    if not user_ids:
        return error_response(400, "用户ID列表不能为空")
    
    approved_users = []
    failed_users = []
    
    for user_id in user_ids:
        target_user = db.query(User).filter(User.id == user_id).first()
        
        if not target_user:
            failed_users.append({"id": user_id, "reason": "用户不存在"})
            continue
        
        if target_user.status != 'pending':
            failed_users.append({"id": user_id, "reason": f"状态为 {target_user.status}"})
            continue
        
        # 激活用户
        target_user.status = 'active'
        target_user.role = 'member'
        approved_users.append(target_user.full_name)
    
    db.commit()
    
    return success_response(
        data={
            "approved_count": len(approved_users),
            "approved_users": approved_users,
            "failed_count": len(failed_users),
            "failed_users": failed_users
        },
        msg=f"成功通过 {len(approved_users)} 个用户"
    )


@router.post("/users/reset-password", response_model=dict, summary="重置用户密码")
async def reset_user_password(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    重置指定用户的密码为初始密码（123456）
    
    权限：仅管理员
    """
    target_user = db.query(User).filter(User.id == user_id).first()
    
    if not target_user:
        return error_response(404, "用户不存在")
    
    # 不允许重置自己的密码
    if target_user.id == current_user.id:
        return error_response(400, "不能重置自己的密码，请使用修改密码功能")
    
    # 生成随机八位强密码
    import secrets
    import string
    alphabet = string.ascii_letters + string.digits
    new_password = ''.join(secrets.choice(alphabet) for i in range(8))
    
    target_user.password_hash = get_password_hash(new_password)
    db.commit()
    
    return success_response(
        data={"new_password": new_password},
        msg=f"已重置 {target_user.full_name} 的密码，请务必记录新密码：{new_password}"
    )


@router.post("/users/promote", response_model=dict, summary="提升用户为管理员")
async def promote_to_admin(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    将指定用户的角色提升为管理员
    
    权限：仅管理员
    """
    target_user = db.query(User).filter(User.id == user_id).first()
    
    if not target_user:
        return error_response(404, "用户不存在")
    
    if target_user.role == 'admin':
        return error_response(400, "该用户已经是管理员")
    
    if target_user.status != 'active':
        return error_response(400, "只能提升已激活的用户为管理员")
    
    # 提升为管理员
    target_user.role = 'admin'
    db.commit()
    db.refresh(target_user)
    
    return success_response(
        data=UserInfo.from_orm(target_user).dict(),
        msg=f"已将 {target_user.full_name} 提升为管理员"
    )


@router.delete("/users/{user_id}", response_model=dict, summary="移出成员（删除用户）")
async def remove_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    将用户移出社团（软删除：设为 inactive）
    
    权限：仅管理员
    """
    target_user = db.query(User).filter(User.id == user_id).first()
    
    if not target_user:
        return error_response(404, "用户不存在")
    
    # 不能删除自己
    if target_user.id == current_user.id:
        return error_response(400, "不能移出自己")
    
    # 软删除：设为 disabled
    target_user.status = 'disabled'
    db.commit()
    
    return success_response(
        msg=f"已将 {target_user.full_name} 移出社团"
    )
