from sqlalchemy import Column, Integer, String, Date, Time
from app.models.base import BaseModel


class Schedule(BaseModel):
    """日程模型"""
    __tablename__ = "schedules"

    title = Column(String(200), nullable=False, comment="日程标题")
    schedule_date = Column(Date, nullable=False, index=True, comment="日程日期")
    start_time = Column(Time, nullable=False, comment="开始时间")
    end_time = Column(Time, nullable=False, comment="结束时间")
    location = Column(String(200), nullable=True, comment="地点")
    color = Column(String(20), nullable=False, default="#3B82F6", comment="颜色标记")
