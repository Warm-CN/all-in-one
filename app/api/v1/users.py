from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.auth import UserInfo
from app.schemas.response import success_response

router = APIRouter()

@router.get("/", response_model=dict, summary="获取通讯录")
async def get_contacts(
    keyword: str = None,
    department: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取通讯录列表（仅展示已激活用户）
    
    权限：所有已登录并激活的用户
    """
    query = db.query(User).filter(User.status == 'active')
    
    if keyword:
        query = query.filter(
            (User.full_name.contains(keyword)) | (User.student_id.contains(keyword))
        )
    
    if department:
        query = query.filter(User.department == department)
    
    # 按部门排序，然后按姓名排序
    users = query.order_by(User.department, User.full_name).all()
    users_data = [UserInfo.from_orm(user).dict() for user in users]
    
    return success_response(
        data=users_data,
        msg=f"获取成功"
    )
