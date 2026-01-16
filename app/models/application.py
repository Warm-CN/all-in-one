"""
报名数据模型
"""
from sqlalchemy import Column, Integer, ForeignKey, Enum as SQLEnum, JSON, Text
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel


class ApplicationStatus(str, enum.Enum):
    """报名状态枚举"""
    SUBMITTED = "submitted"  # 已提交
    REVIEWING = "reviewing"  # 审核中
    ACCEPTED = "accepted"    # 已通过
    REJECTED = "rejected"    # 已拒绝
    CANCELLED = "cancelled"  # 已取消


class Application(BaseModel):
    """报名数据表"""
    __tablename__ = "applications"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="报名用户ID")
    signup_config_id = Column(Integer, ForeignKey("signup_configs.id", ondelete="CASCADE"), nullable=False, comment="报名配置ID")
    
    # 灵活表单数据 (JSON 格式)
    # 示例: {"姓名": "张三", "专业": "计算机科学", "自我介绍": "..."}
    form_data = Column(JSON, nullable=False, comment="表单数据")
    
    status = Column(SQLEnum(ApplicationStatus), default=ApplicationStatus.SUBMITTED, nullable=False, comment="报名状态")
    review_notes = Column(Text, nullable=True, comment="审核备注")
    
    # 关系
    user = relationship("User", back_populates="applications")
    signup_config = relationship("SignupConfig", back_populates="applications")
    
    def __repr__(self):
        return f"<Application {self.id} by User {self.user_id} for Config {self.signup_config_id}>"
