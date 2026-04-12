"""
简化版会议室预约模型
用于日常预约管理（无需审批流程）
"""
from sqlalchemy import Column, Integer, ForeignKey, Date, Time, String, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class RoomBooking(BaseModel):
    """会议室预约表（简化版）"""
    __tablename__ = "room_bookings"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="预约用户ID")
    booking_date = Column(Date, nullable=False, index=True, comment="预约日期")
    start_time = Column(Time, nullable=False, comment="开始时间")
    end_time = Column(Time, nullable=False, comment="结束时间")
    num_people = Column(Integer, nullable=False, comment="人数")
    remarks = Column(Text, nullable=True, comment="备注")
    
    # 关系
    user = relationship("User", backref="room_bookings")
    
    def __repr__(self):
        return f"<RoomBooking {self.id} on {self.booking_date} by User {self.user_id}>"
