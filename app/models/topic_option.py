"""
竞赛题目选项模型
"""
from sqlalchemy import Column, String, Text, Boolean, Integer
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class TopicOption(BaseModel):
    """题目选项表"""
    __tablename__ = "topic_options"

    code = Column(String(50), nullable=False, unique=True, index=True, comment="题目编号")
    title = Column(String(200), nullable=False, comment="题目名称")
    module_key = Column(String(80), nullable=True, index=True, comment="所属比赛模块")
    description = Column(Text, nullable=True, comment="题目说明")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否可选")
    max_teams = Column(Integer, nullable=True, comment="最大可选队伍数，空表示不限")

    teams = relationship("Team", back_populates="topic")

    def __repr__(self):
        return f"<TopicOption {self.code} {self.title}>"
