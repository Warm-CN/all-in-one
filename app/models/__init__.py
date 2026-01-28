"""
模型包初始化
导出所有模型
"""
from app.models.base import BaseModel
from app.models.user import User
from app.models.room import Room
from app.models.room_booking import RoomBooking
from app.models.signup import SignupConfig
from app.models.application import Application, ApplicationStatus
from app.models.schedule import Schedule

__all__ = [
    "BaseModel",
    "User",
    "Room",
    "RoomBooking",
    "SignupConfig",
    "Application",
    "ApplicationStatus",
    "Schedule",
]
