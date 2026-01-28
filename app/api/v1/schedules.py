"""
日程查询路由（普通用户只读）
提供日程的查询功能，所有登录用户均可访问
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date, datetime
from typing import Optional, List

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.schedule import Schedule
from app.models.user import User
from app.schemas.schedule import ScheduleResponse
from app.schemas.response import success_response, error_response

router = APIRouter(prefix="/api/v1/schedules", tags=["日程查询"])


@router.get("", response_model=dict, summary="获取日程列表")
async def get_schedules(
    date: Optional[date] = Query(None, description="查询指定日期的日程"),
    start_date: Optional[date] = Query(None, description="查询日期范围-起始日期"),
    end_date: Optional[date] = Query(None, description="查询日期范围-结束日期"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取日程列表，支持三种查询模式：
    1. 指定日期：传入 date 参数
    2. 日期范围：传入 start_date 和 end_date 参数
    3. 不传参数：返回空列表
    
    参数:
    - date: 查询指定日期 (格式: YYYY-MM-DD)
    - start_date: 起始日期 (格式: YYYY-MM-DD)
    - end_date: 结束日期 (格式: YYYY-MM-DD)
    """
    query = db.query(Schedule)
    
    # 按查询模式过滤
    if date:
        # 单日查询
        query = query.filter(Schedule.schedule_date == date)
    elif start_date and end_date:
        # 日期范围查询
        query = query.filter(
            and_(
                Schedule.schedule_date >= start_date,
                Schedule.schedule_date <= end_date
            )
        )
    elif start_date:
        # 只有起始日期
        query = query.filter(Schedule.schedule_date >= start_date)
    elif end_date:
        # 只有结束日期
        query = query.filter(Schedule.schedule_date <= end_date)
    else:
        # 不传参数返回空列表
        return success_response(data=[], msg="请指定查询条件")
    
    # 按日期和时间排序
    schedules = query.order_by(
        Schedule.schedule_date,
        Schedule.start_time
    ).all()
    
    # 构建返回数据
    data = []
    for schedule in schedules:
        data.append({
            "id": schedule.id,
            "title": schedule.title,
            "schedule_date": schedule.schedule_date.isoformat(),
            "start_time": schedule.start_time.strftime("%H:%M"),
            "end_time": schedule.end_time.strftime("%H:%M"),
            "location": schedule.location,
            "color": schedule.color,
            "created_at": schedule.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": schedule.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        })
    
    return success_response(data=data, msg="查询成功")
