"""
竞赛队员模型
"""
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class TeamMember(BaseModel):
    """队员表（不含队长）"""
    __tablename__ = "team_members"

    team_id = Column(ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True, comment="队伍ID")
    name = Column(String(50), nullable=False, comment="队员姓名")
    student_id = Column(String(20), nullable=False, index=True, comment="队员学号")
    phone = Column(String(20), nullable=False, comment="队员手机号")
    email = Column(String(100), nullable=True, comment="队员邮箱")
    college = Column(String(100), nullable=True, comment="队员学院")
    major_class = Column(String(100), nullable=True, comment="队员专业班级")

    team = relationship("Team", back_populates="members")

    def __repr__(self):
        return f"<TeamMember {self.student_id} team={self.team_id}>"
