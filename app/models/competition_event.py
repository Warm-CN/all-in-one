"""比赛活动模型"""

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class CompetitionEvent(BaseModel):
    __tablename__ = "competition_events"

    cup_type = Column(String(20), nullable=False, index=True, comment="赛事类型: wireless/telecom")
    name = Column(String(120), nullable=False, comment="比赛名称")
    module_key = Column(String(80), nullable=False, unique=True, index=True, comment="报名模块标识")

    signup_start_at = Column(DateTime, nullable=True, comment="报名开始时间")
    signup_end_at = Column(DateTime, nullable=True, comment="报名截止时间")
    topic_open_at = Column(DateTime, nullable=True, comment="选题开放时间")
    topic_end_at = Column(DateTime, nullable=True, comment="选题截止时间")
    cycle_start_at = Column(DateTime, nullable=True, comment="比赛周期开始时间")
    cycle_end_at = Column(DateTime, nullable=True, comment="比赛周期结束时间")

    planned_topic_count = Column(Integer, nullable=False, default=1, comment="计划题目数量")
    portal_title = Column(String(120), nullable=True, comment="报名页展示标题")
    is_current = Column(Integer, nullable=False, default=0, comment="是否正在比赛：1是0否")

    topics = relationship(
        "CompetitionEventTopic",
        back_populates="event",
        cascade="all, delete-orphan",
        order_by="CompetitionEventTopic.id.asc()",
    )
