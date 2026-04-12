"""
日程管理路由（管理员专用）
提供日程的创建、删除功能，仅管理员可访问
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date, time, datetime
from typing import List

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.models.schedule import Schedule
from app.models.user import User
from app.schemas.schedule import ScheduleCreate, ScheduleResponse
from app.schemas.response import success_response, error_response

router = APIRouter(prefix="/api/v1/admin/schedules", tags=["📅 管理员-日程管理"])


def check_time_overlap(
    db: Session,
    schedule_date: date,
    start_time: time,
    end_time: time,
    exclude_id: int = None
) -> List[dict]:
    """
    检查时间段是否与已有日程重叠
    
    Args:
        db: 数据库会话
        schedule_date: 日程日期
        start_time: 开始时间
        end_time: 结束时间
        exclude_id: 排除的日程ID（用于更新时忽略自己）
    
    Returns:
        List[dict]: 重叠的日程列表
    """
    query = db.query(Schedule).filter(
        Schedule.schedule_date == schedule_date
    )
    
    # 排除指定ID
    if exclude_id:
        query = query.filter(Schedule.id != exclude_id)
    
    # 获取当天所有日程
    schedules = query.all()
    
    # 检查时间重叠
    overlapping = []
    for existing in schedules:
        if start_time < existing.end_time and end_time > existing.start_time:
            overlapping.append({
                "id": existing.id,
                "title": existing.title,
                "time_range": f"{existing.start_time.strftime('%H:%M')}-{existing.end_time.strftime('%H:%M')}"
            })
    
    return overlapping


@router.post("", response_model=dict, summary="创建日程")
async def create_schedule(
    schedule_data: ScheduleCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    创建新的日程，会检测时间冲突但不阻止创建
    
    请求体:
    - title: 日程标题
    - schedule_date: 日程日期
    - start_time: 开始时间
    - end_time: 结束时间
    - location: 地点（可选）
    - color: 颜色标记（默认 #3B82F6）
    """
    # 验证时间范围
    if schedule_data.start_time >= schedule_data.end_time:
        return error_response(code=400, msg="结束时间必须晚于开始时间")
    
    # 检测时间冲突
    overlapping = check_time_overlap(
        db,
        schedule_data.schedule_date,
        schedule_data.start_time,
        schedule_data.end_time
    )
    
    # 创建日程
    new_schedule = Schedule(
        title=schedule_data.title,
        schedule_date=schedule_data.schedule_date,
        start_time=schedule_data.start_time,
        end_time=schedule_data.end_time,
        location=schedule_data.location,
        color=schedule_data.color
    )
    
    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)
    
    # 构建返回数据
    response_data = {
        "id": new_schedule.id,
        "title": new_schedule.title,
        "schedule_date": new_schedule.schedule_date.isoformat(),
        "start_time": new_schedule.start_time.strftime("%H:%M"),
        "end_time": new_schedule.end_time.strftime("%H:%M"),
        "location": new_schedule.location,
        "color": new_schedule.color,
        "created_at": new_schedule.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": new_schedule.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
    }
    
    # 如果有时间冲突，附加警告信息
    if overlapping:
        response_data["warning"] = f"该时间段与 {len(overlapping)} 个已有日程重叠"
        response_data["overlapping_schedules"] = overlapping
    
    return success_response(data=response_data, msg="日程创建成功")


@router.delete("/{schedule_id}", response_model=dict, summary="删除日程")
async def delete_schedule(
    schedule_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    删除指定的日程
    
    参数:
    - schedule_id: 日程ID
    """
    # 查询日程
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    
    if not schedule:
        return error_response(code=404, msg="日程不存在")
    
    # 删除日程
    db.delete(schedule)
    db.commit()
    
    return success_response(data={"id": schedule_id}, msg="日程删除成功")


@router.get("/check-overlap", response_model=dict, summary="检查时间冲突")
async def check_overlap(
    schedule_date: date,
    start_time: time,
    end_time: time,
    exclude_id: int = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    检查指定时间段是否与已有日程冲突
    
    参数:
    - schedule_date: 日程日期
    - start_time: 开始时间
    - end_time: 结束时间
    - exclude_id: 排除的日程ID（可选）
    """
    overlapping = check_time_overlap(
        db,
        schedule_date,
        start_time,
        end_time,
        exclude_id
    )
    
    return success_response(
        data={
            "has_conflict": len(overlapping) > 0,
            "overlapping_schedules": overlapping
        },
        msg="检查完成"
    )
