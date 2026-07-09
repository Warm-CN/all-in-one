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
from app.models.topic_option import TopicOption
from app.models.team import Team, TeamStatus
from app.models.team_member import TeamMember
from app.models.team_channel_config import TeamChannelConfig
from app.models.inspection_assignment import InspectionAssignment
from app.models.competition_event import CompetitionEvent
from app.models.competition_event_topic import CompetitionEventTopic
from app.models.suggestion import Suggestion, Screenshot, Annotation, StatusChange, Reply, Endorsement

__all__ = [
    "BaseModel",
    "User",
    "Room",
    "RoomBooking",
    "SignupConfig",
    "Application",
    "ApplicationStatus",
    "Schedule",
    "TopicOption",
    "Team",
    "TeamStatus",
    "TeamMember",
    "TeamChannelConfig",
    "InspectionAssignment",
    "CompetitionEvent",
    "CompetitionEventTopic",
    "Suggestion",
    "Screenshot",
    "Annotation",
    "StatusChange",
    "Reply",
    "Endorsement",
]
