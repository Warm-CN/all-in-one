"""
会议室预约路由
场景 B：内部接口 - 预约会议室（需要 Member 或 Admin 权限）
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

from app.core.database import get_db
from app.core.dependencies import require_member, require_admin, get_current_active_user
from app.models.booking import Booking, BookingStatus
from app.models.room import Room
from app.models.user import User
from app.schemas.response import success_response, error_response

router = APIRouter()


class BookingRequest(BaseModel):
    """预约请求"""
    room_id: int = Field(..., description="会议室ID")
    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")
    purpose: str = Field(..., min_length=5, max_length=200, description="预约目的")
    participant_count: Optional[int] = Field(None, description="参与人数")
    notes: Optional[str] = Field(None, description="备注")


@router.post("/create", response_model=dict, summary="预约会议室")
async def create_booking(
    booking_data: BookingRequest,
    current_user: User = Depends(require_member),  # 场景 B：需要 Member 或 Admin
    db: Session = Depends(get_db)
):
    """
    场景 B（内部）：预约会议室
    
    **需要 Member 或 Admin 权限**
    
    只有社团成员才能预约会议室
    """
    # 检查会议室是否存在
    room = db.query(Room).filter(Room.id == booking_data.room_id).first()
    if not room:
        return error_response(404, "会议室不存在")
    
    if not room.is_available:
        return error_response(400, "该会议室当前不可用")
    
    # 验证时间
    if booking_data.start_time >= booking_data.end_time:
        return error_response(400, "结束时间必须晚于开始时间")
    
    if booking_data.start_time < datetime.now():
        return error_response(400, "不能预约过去的时间")
    
    # 检查时间冲突
    conflicting = db.query(Booking).filter(
        Booking.room_id == booking_data.room_id,
        Booking.status.in_([BookingStatus.PENDING, BookingStatus.APPROVED]),
        Booking.start_time < booking_data.end_time,
        Booking.end_time > booking_data.start_time
    ).first()
    
    if conflicting:
        return error_response(400, f"该时间段已被预约（预约ID: {conflicting.id}）")
    
    # 创建预约
    booking = Booking(
        user_id=current_user.id,
        room_id=booking_data.room_id,
        start_time=booking_data.start_time,
        end_time=booking_data.end_time,
        purpose=booking_data.purpose,
        participant_count=booking_data.participant_count,
        notes=booking_data.notes,
        status=BookingStatus.PENDING  # 待审核
    )
    
    db.add(booking)
    db.commit()
    db.refresh(booking)
    
    return success_response(
        data={
            "booking_id": booking.id,
            "status": booking.status.value,
            "room_name": room.name
        },
        msg="预约成功，请等待管理员审批"
    )


@router.get("/my-bookings", response_model=dict, summary="查看我的预约")
async def get_my_bookings(
    status: str = None,
    current_user: User = Depends(require_member),
    db: Session = Depends(get_db)
):
    """
    场景 B（内部）：查看自己的预约记录
    
    **需要 Member 或 Admin 权限**
    """
    query = db.query(Booking).filter(Booking.user_id == current_user.id)
    
    if status:
        query = query.filter(Booking.status == status)
    
    bookings = query.order_by(Booking.start_time.desc()).all()
    
    return success_response(
        data=[{
            "id": b.id,
            "room_id": b.room_id,
            "start_time": b.start_time.isoformat(),
            "end_time": b.end_time.isoformat(),
            "purpose": b.purpose,
            "status": b.status.value,
            "created_at": b.created_at.isoformat()
        } for b in bookings],
        msg="获取成功"
    )


@router.post("/approve/{booking_id}", response_model=dict, summary="审批预约（仅管理员）")
async def approve_booking(
    booking_id: int,
    approve: bool = True,
    reject_reason: str = None,
    current_user: User = Depends(require_admin),  # 场景 C：仅限 Admin
    db: Session = Depends(get_db)
):
    """
    场景 C（管理）：审批会议室预约
    
    **仅限 Admin 权限**
    
    - approve: True 表示批准，False 表示拒绝
    - reject_reason: 拒绝原因（拒绝时必填）
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        return error_response(404, "预约不存在")
    
    if booking.status != BookingStatus.PENDING:
        return error_response(400, f"该预约当前状态为 {booking.status.value}，无法审批")
    
    if approve:
        booking.status = BookingStatus.APPROVED
        msg = "预约已批准"
    else:
        if not reject_reason:
            return error_response(400, "拒绝时必须提供原因")
        booking.status = BookingStatus.REJECTED
        booking.reject_reason = reject_reason
        msg = "预约已拒绝"
    
    db.commit()
    
    return success_response(msg=msg)


@router.get("/all", response_model=dict, summary="查看所有预约（仅管理员）")
async def get_all_bookings(
    status: str = None,
    room_id: int = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    场景 C（管理）：导出所有预约数据
    
    **仅限 Admin 权限**
    """
    query = db.query(Booking)
    
    if status:
        query = query.filter(Booking.status == status)
    if room_id:
        query = query.filter(Booking.room_id == room_id)
    
    bookings = query.order_by(Booking.created_at.desc()).all()
    
    return success_response(
        data=[{
            "id": b.id,
            "user_id": b.user_id,
            "room_id": b.room_id,
            "start_time": b.start_time.isoformat(),
            "end_time": b.end_time.isoformat(),
            "purpose": b.purpose,
            "status": b.status.value,
            "participant_count": b.participant_count,
            "notes": b.notes,
            "reject_reason": b.reject_reason,
            "created_at": b.created_at.isoformat()
        } for b in bookings],
        msg="获取成功"
    )
