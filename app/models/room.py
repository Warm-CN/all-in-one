"""
会议室相关模型
"""
from sqlalchemy import Column, String, Integer, Boolean, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Room(BaseModel):
    """会议室表"""
    __tablename__ = "rooms"
    
    name = Column(String(100), unique=True, nullable=False, comment="会议室名称")
    location = Column(String(200), nullable=False, comment="位置")
    capacity = Column(Integer, nullable=False, comment="容纳人数")
    equipment = Column(Text, nullable=True, comment="设备描述")
    is_available = Column(Boolean, default=True, nullable=False, comment="是否可用")
    description = Column(Text, nullable=True, comment="会议室描述")
    image_url = Column(String(255), nullable=True, comment="会议室图片")
    
    def __repr__(self):
        return f"<Room {self.name} at {self.location}>"
