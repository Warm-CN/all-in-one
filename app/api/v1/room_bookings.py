"""
会议室预约路由（简化版 - 无需审批）
提供日常会议室预约的增删查功能，包含时间冲突检测
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date, time, datetime, timedelta
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.room_booking import RoomBooking
from app.models.user import User
from app.schemas.room_booking import BookingCreate, BookingResponse
from app.schemas.response import success_response, error_response

router = APIRouter(prefix="/api/bookings", tags=["会议室预约"])


def check_time_overlap(
    db: Session,
    booking_date: date,
    start_time: time,
    end_time: time,
    exclude_id: int = None
) -> bool:
    """
    检查时间段是否与已有预约重叠
    
    Args:
        db: 数据库会话
        booking_date: 预约日期
        start_time: 开始时间
        end_time: 结束时间
        exclude_id: 排除的预约ID（用于更新时忽略自己）
    
    Returns:
        bool: True 表示有冲突，False 表示无冲突
    """
    query = db.query(RoomBooking).filter(
        RoomBooking.booking_date == booking_date
    )
    
    # 排除指定ID
    if exclude_id:
        query = query.filter(RoomBooking.id != exclude_id)
    
    # 获取当天所有预约
    bookings = query.all()
    
    # 检查时间重叠：两个时间段重叠的条件是
    # start_time < existing.end_time AND end_time > existing.start_time
    for existing in bookings:
        if start_time < existing.end_time and end_time > existing.start_time:
            return True
    
    return False


@router.get("", response_model=dict, summary="获取指定日期的预约列表")
async def get_bookings(
    date: date,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取指定日期的所有预约记录，按时间先后排序
    
    参数:
    - date: 查询日期 (格式: YYYY-MM-DD)
    """
    bookings = db.query(RoomBooking).filter(
        RoomBooking.booking_date == date
    ).order_by(
        RoomBooking.start_time
    ).all()
    
    # 构建返回数据，包含用户信息
    data = []
    for booking in bookings:
        data.append({
            "id": booking.id,
            "user_id": booking.user_id,
            "booking_date": booking.booking_date.isoformat(),
            "start_time": booking.start_time.strftime("%H:%M"),
            "end_time": booking.end_time.strftime("%H:%M"),
            "num_people": booking.num_people,
            "remarks": booking.remarks,
            "user_name": booking.user.full_name if booking.user else None,
            "user_dept": booking.user.department if booking.user else None,
            "created_at": booking.created_at.isoformat()
        })
    
    return success_response(data=data, msg="获取成功")


@router.post("", response_model=dict, summary="提交会议室预约")
async def create_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    提交会议室预约
    
    核心校验：
    - 检查预约日期不能是过去
    - 检查时间段是否与已有预约重叠
    - 自动关联当前登录用户
    """
    # 检查日期是否是过去
    if booking_data.booking_date < date.today():
        return error_response(400, "不能预约过去的日期")
    
    # 检查时间冲突
    has_conflict = check_time_overlap(
        db=db,
        booking_date=booking_data.booking_date,
        start_time=booking_data.start_time,
        end_time=booking_data.end_time
    )
    
    if has_conflict:
        return error_response(400, "该时段已被占用，请选择其他时间")
    
    # 创建预约记录
    booking = RoomBooking(
        user_id=current_user.id,  # 自动关联当前用户
        booking_date=booking_data.booking_date,
        start_time=booking_data.start_time,
        end_time=booking_data.end_time,
        num_people=booking_data.num_people,
        remarks=booking_data.remarks
    )
    
    db.add(booking)
    db.commit()
    db.refresh(booking)
    
    return success_response(
        data={
            "id": booking.id,
            "booking_date": booking.booking_date.isoformat(),
            "start_time": booking.start_time.strftime("%H:%M"),
            "end_time": booking.end_time.strftime("%H:%M")
        },
        msg="预约成功"
    )


@router.delete("/{id}", response_model=dict, summary="取消预约")
async def delete_booking(
    id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    取消会议室预约
    
    权限控制：
    - 普通用户只能删除自己的预约
    - 管理员可以删除任何预约
    """
    booking = db.query(RoomBooking).filter(RoomBooking.id == id).first()
    
    if not booking:
        return error_response(404, "预约不存在")
    
    # 权限检查：普通用户只能删除自己的预约
    if booking.user_id != current_user.id and current_user.role != "admin":
        return error_response(403, "无权删除此预约")
    
    db.delete(booking)
    db.commit()
    
    return success_response(msg="预约已取消")


@router.get("/my", response_model=dict, summary="获取我的预约列表")
async def get_my_bookings(
    upcoming: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的所有预约记录
    - upcoming: 是否仅获取未来（含今天）的预约
    """
    query = db.query(RoomBooking).filter(
        RoomBooking.user_id == current_user.id
    )

    if upcoming:
        query = query.filter(RoomBooking.booking_date >= date.today())
        # 未来预约按时间正序排列（最近的在前面）
        query = query.order_by(
            RoomBooking.booking_date.asc(),
            RoomBooking.start_time.asc()
        )
    else:
        # 历史预约按时间倒序排列
        query = query.order_by(
            RoomBooking.booking_date.desc(),
            RoomBooking.start_time.desc()
        )

    bookings = query.all()
    
    data = []
    for booking in bookings:
        data.append({
            "id": booking.id,
            "booking_date": booking.booking_date.isoformat(),
            "start_time": booking.start_time.strftime("%H:%M"),
            "end_time": booking.end_time.strftime("%H:%M"),
            "num_people": booking.num_people,
            "remarks": booking.remarks,
            "created_at": booking.created_at.isoformat()
        })
    
    return success_response(data=data, msg="获取成功")
