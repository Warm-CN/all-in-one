"""
报名配置模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class SignupConfig(BaseModel):
    """报名配置表"""
    __tablename__ = "signup_configs"
    
    title = Column(String(200), nullable=False, comment="报名活动标题")
    description = Column(Text, nullable=True, comment="活动描述")
    start_time = Column(DateTime, nullable=False, comment="报名开始时间")
    end_time = Column(DateTime, nullable=False, comment="报名结束时间")
    max_participants = Column(Integer, nullable=True, comment="最大报名人数（null表示不限制）")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否激活")
    current_stage = Column(String(30), nullable=False, default="registration", comment="系统当前阶段")
    
    # 自定义表单字段配置 (JSON 格式)
    # 示例: [{"name": "姓名", "type": "text", "required": true}, {"name": "专业", "type": "text"}]
    form_fields = Column(JSON, nullable=False, comment="表单字段配置")
    
    # 分类标签，用于区分不同活动类型（招新、无线杯、电信杯等）
    category = Column(String(50), nullable=False, index=True, comment="活动分类")
    
    # 关系
    applications = relationship("Application", back_populates="signup_config", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SignupConfig {self.title} ({self.category})>"
