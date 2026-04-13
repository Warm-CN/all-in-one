"""
队伍验收安排模型
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class InspectionAssignment(BaseModel):
    """验收安排表"""
    __tablename__ = "inspection_assignments"

    team_id = Column(ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, unique=True, index=True, comment="队伍ID")
    # 一验安排
    first_inspection_time = Column(DateTime, nullable=True, comment="第一次验收时间")
    first_inspection_location = Column(String(100), nullable=True, comment="第一次验收地点")
    first_inspector = Column(String(100), nullable=True, comment="第一次验收负责人")
    first_notes = Column(Text, nullable=True, comment="第一次验收备注")

    # 二验安排
    second_inspection_time = Column(DateTime, nullable=True, comment="第二次验收时间")
    second_inspection_location = Column(String(100), nullable=True, comment="第二次验收地点")
    second_inspector = Column(String(100), nullable=True, comment="第二次验收负责人")
    second_notes = Column(Text, nullable=True, comment="第二次验收备注")

    # 兼容旧字段（后续可迁移下线）
    inspection_time = Column(DateTime, nullable=True, comment="验收时间")
    inspection_location = Column(String(100), nullable=True, comment="验收地点")
    inspector = Column(String(100), nullable=True, comment="验收负责人")
    notes = Column(Text, nullable=True, comment="验收备注")
    assigned_by = Column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="安排人")

    team = relationship("Team", back_populates="inspection_assignment")

    def __repr__(self):
        return f"<InspectionAssignment team={self.team_id}>"
