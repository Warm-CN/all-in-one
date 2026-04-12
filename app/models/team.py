"""
竞赛队伍模型
"""
import enum

from sqlalchemy import Boolean, Column, DateTime, String, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


def enum_values(enum_cls):
    return [item.value for item in enum_cls]


class TeamStatus(str, enum.Enum):
    """队伍状态枚举"""
    SUBMITTED = "submitted"
    REVIEWING = "reviewing"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class Team(BaseModel):
    """竞赛队伍主表"""
    __tablename__ = "teams"

    team_name = Column(String(100), nullable=False, comment="队伍名称")
    competition_track = Column(String(100), nullable=True, comment="赛道/组别")
    module_key = Column(String(80), nullable=True, index=True, comment="所属比赛模块")

    captain_name = Column(String(50), nullable=False, comment="队长姓名")
    captain_student_id = Column(String(20), nullable=False, index=True, comment="队长学号")
    captain_phone = Column(String(20), nullable=False, comment="队长手机号")
    captain_email = Column(String(100), nullable=True, comment="队长邮箱")
    captain_college = Column(String(100), nullable=True, comment="队长学院")
    captain_major_class = Column(String(100), nullable=True, comment="队长专业班级")

    topic_id = Column(ForeignKey("topic_options.id", ondelete="SET NULL"), nullable=True, comment="选题ID")
    status = Column(
        SQLEnum(TeamStatus, values_callable=enum_values, name="teamstatus"),
        default=TeamStatus.SUBMITTED,
        nullable=False,
        comment="队伍状态"
    )
    notes = Column(Text, nullable=True, comment="队伍备注")
    delete_requested = Column(Boolean, nullable=False, default=False, comment="是否已提交删除申请")
    delete_requested_at = Column(DateTime, nullable=True, comment="删除申请时间")
    delete_reason = Column(Text, nullable=True, comment="删除申请理由")

    topic = relationship("TopicOption", back_populates="teams")
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    inspection_assignment = relationship(
        "InspectionAssignment",
        back_populates="team",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Team {self.id} captain={self.captain_student_id}>"
