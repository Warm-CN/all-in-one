"""比赛题目模型"""

from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class CompetitionEventTopic(BaseModel):
    __tablename__ = "competition_event_topics"

    event_id = Column(ForeignKey("competition_events.id", ondelete="CASCADE"), nullable=False, index=True, comment="所属比赛")
    title = Column(String(200), nullable=False, comment="选题名称")
    description = Column(Text, nullable=True, comment="题目简介")
    document_name = Column(String(255), nullable=True, comment="题目文档名称")
    document_path = Column(String(255), nullable=True, comment="题目文档路径")
    topic_option_id = Column(ForeignKey("topic_options.id", ondelete="SET NULL"), nullable=True, index=True, comment="映射的选题ID")

    event = relationship("CompetitionEvent", back_populates="topics")
