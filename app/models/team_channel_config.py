"""
竞赛队伍模块通道配置模型
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey

from app.models.base import BaseModel


class TeamChannelConfig(BaseModel):
    """报名与选题通道配置"""
    __tablename__ = "team_channel_configs"

    module_key = Column(String(50), nullable=False, unique=True, index=True, comment="模块标识，如 wireless_cup_2026")
    signup_open = Column(Boolean, default=True, nullable=False, comment="报名通道是否开启")
    topic_open = Column(Boolean, default=False, nullable=False, comment="选题通道是否开启")
    info_update_open = Column(Boolean, default=True, nullable=False, comment="队伍信息修改通道是否开启")
    signup_close_at = Column(DateTime, nullable=True, comment="报名截止时间")
    topic_close_at = Column(DateTime, nullable=True, comment="选题截止时间")
    info_update_close_at = Column(DateTime, nullable=True, comment="队伍信息修改截止时间")
    updated_by = Column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="最近更新人")

    def __repr__(self):
        return f"<TeamChannelConfig {self.module_key}>"
