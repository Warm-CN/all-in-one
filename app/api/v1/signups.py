"""
报名系统路由
场景 A：公开接口 - 提交报名表单（无需登录）
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.models.signup import SignupConfig
from app.models.application import Application, ApplicationStatus
from app.models.user import User
from app.schemas.response import success_response, error_response

router = APIRouter()


@router.get("/configs", response_model=dict, summary="获取活跃的报名配置列表")
async def get_active_signup_configs(
    category: str = None,
    db: Session = Depends(get_db)
):
    """
    场景 A（公开）：获取当前可报名的活动列表
    
    无需登录即可访问
    """
    query = db.query(SignupConfig).filter(SignupConfig.is_active == True)
    
    # 按分类筛选
    if category:
        query = query.filter(SignupConfig.category == category)
    
    # 只显示报名时间内的活动
    now = datetime.now()
    query = query.filter(
        SignupConfig.start_time <= now,
        SignupConfig.end_time >= now
    )
    
    configs = query.all()
    
    return success_response(
        data=[{
            "id": c.id,
            "title": c.title,
            "description": c.description,
            "category": c.category,
            "start_time": c.start_time.isoformat(),
            "end_time": c.end_time.isoformat(),
            "max_participants": c.max_participants,
            "form_fields": c.form_fields
        } for c in configs],
        msg="获取成功"
    )


@router.post("/apply", response_model=dict, summary="提交报名表单")
async def submit_application(
    signup_config_id: int,
    student_id: str,
    form_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    场景 A（公开）：提交报名表单
    
    **无需登录** - 游客也可以报名
    
    - signup_config_id: 报名配置ID
    - student_id: 学号
    - form_data: 表单数据（JSON格式）
    
    示例：
    ```json
    {
        "signup_config_id": 1,
        "student_id": "2021001",
        "form_data": {
            "姓名": "张三",
            "专业": "计算机科学",
            "自我介绍": "我热爱编程..."
        }
    }
    ```
    """
    # 检查报名配置是否存在
    config = db.query(SignupConfig).filter(SignupConfig.id == signup_config_id).first()
    if not config:
        return error_response(404, "报名活动不存在")
    
    if not config.is_active:
        return error_response(400, "该活动已关闭报名")
    
    # 检查报名时间
    now = datetime.now()
    if now < config.start_time:
        return error_response(400, "报名尚未开始")
    if now > config.end_time:
        return error_response(400, "报名已结束")
    
    # 查找或创建用户（如果学号存在则关联，否则游客身份）
    user = db.query(User).filter(User.student_id == student_id).first()
    user_id = user.id if user else None
    
    # 检查是否已报名
    if user_id:
        existing = db.query(Application).filter(
            Application.user_id == user_id,
            Application.signup_config_id == signup_config_id
        ).first()
        if existing:
            return error_response(400, "您已经报名过该活动了")
    
    # 检查人数限制
    if config.max_participants:
        current_count = db.query(Application).filter(
            Application.signup_config_id == signup_config_id
        ).count()
        if current_count >= config.max_participants:
            return error_response(400, "报名人数已满")
    
    # 创建报名记录
    application = Application(
        user_id=user_id,
        signup_config_id=signup_config_id,
        form_data=form_data,
        status=ApplicationStatus.SUBMITTED
    )
    
    db.add(application)
    db.commit()
    db.refresh(application)
    
    return success_response(
        data={"application_id": application.id},
        msg="报名成功！"
    )


@router.get("/applications", response_model=dict, summary="获取报名列表（仅管理员）")
async def get_applications(
    signup_config_id: int = None,
    status: str = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    场景 C（管理）：查看所有报名记录
    
    **仅限 Admin** - 导出数据
    """
    query = db.query(Application)
    
    if signup_config_id:
        query = query.filter(Application.signup_config_id == signup_config_id)
    
    if status:
        query = query.filter(Application.status == status)
    
    applications = query.all()
    
    return success_response(
        data=[{
            "id": app.id,
            "user_id": app.user_id,
            "signup_config_id": app.signup_config_id,
            "form_data": app.form_data,
            "status": app.status.value,
            "created_at": app.created_at.isoformat()
        } for app in applications],
        msg="获取成功"
    )
