"""
会议室预约模型
"""
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel


class BookingStatus(str, enum.Enum):
    """预约状态枚举"""
    PENDING = "pending"      # 待审核
    APPROVED = "approved"    # 已批准
    REJECTED = "rejected"    # 已拒绝
    CANCELLED = "cancelled"  # 已取消
    COMPLETED = "completed"  # 已完成


class Booking(BaseModel):
    """会议室预约表"""
    __tablename__ = "bookings"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="预约用户ID")
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False, comment="会议室ID")
    start_time = Column(DateTime, nullable=False, comment="开始时间")
    end_time = Column(DateTime, nullable=False, comment="结束时间")
    purpose = Column(String(200), nullable=False, comment="预约目的")
    status = Column(SQLEnum(BookingStatus), default=BookingStatus.PENDING, nullable=False, comment="预约状态")
    participant_count = Column(Integer, nullable=True, comment="参与人数")
    notes = Column(Text, nullable=True, comment="备注")
    reject_reason = Column(Text, nullable=True, comment="拒绝原因")
    
    # 关系
    user = relationship("User", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")
    
    def __repr__(self):
        return f"<Booking {self.id} by User {self.user_id} for Room {self.room_id}>"
