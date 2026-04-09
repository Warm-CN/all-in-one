"""
报名数据模型
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SQLEnum, JSON, Text
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel


def enum_values(enum_cls):
    return [item.value for item in enum_cls]


class ApplicationStatus(str, enum.Enum):
    """报名状态枚举"""
    SUBMITTED = "submitted"  # 已提交
    REVIEWING = "reviewing"  # 审核中
    ACCEPTED = "accepted"    # 已通过
    REJECTED = "rejected"    # 已拒绝
    CANCELLED = "cancelled"  # 已取消


class InterviewStage(str, enum.Enum):
    """面试阶段枚举"""
    FIRST_ROUND = "first_round"    # 第一轮面试（可安排两个志愿）
    SECOND_ROUND = "second_round"  # 第二轮面试（只保留一个志愿）
    ACCEPTED = "accepted"          # 录用
    REJECTED = "rejected"          # 淘汰


class Application(BaseModel):
    """报名数据表"""
    __tablename__ = "applications"
    
    # 将 user_id 设为可空，内外人员分离。当人员成为正式成员时再关联
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="报名用户ID")
    signup_config_id = Column(Integer, ForeignKey("signup_configs.id", ondelete="CASCADE"), nullable=False, comment="报名配置ID")
    
    # 招新独有字段：独立于人员表，避免污染内部人员库
    student_id = Column(String(20), nullable=False, index=True, comment="学号")
    name = Column(String(50), nullable=False, comment="姓名")
    phone = Column(String(20), nullable=False, comment="手机号")
    
    # 灵活表单数据 (JSON 格式)
    # 示例: {"专业": "计算机", "自我介绍": "..."}
    form_data = Column(JSON, nullable=False, comment="详细表单数据")
    
    status = Column(SQLEnum(ApplicationStatus), default=ApplicationStatus.SUBMITTED, nullable=False, comment="报名状态")
    current_stage = Column(
        SQLEnum(InterviewStage, values_callable=enum_values, name="interviewstage"),
        default=InterviewStage.FIRST_ROUND,
        nullable=False,
        comment="当前面试阶段"
    )
    review_notes = Column(Text, nullable=True, comment="审核备注")
    
    # 旧版面试信息（兼容）
    interview_time = Column(String(50), nullable=True, comment="面试时间安排")
    interview_location = Column(String(100), nullable=True, comment="面试地点安排")

    # 一面可安排两个志愿的时间和地点
    first_choice_interview_time = Column(String(50), nullable=True, comment="第一志愿面试时间")
    first_choice_interview_location = Column(String(100), nullable=True, comment="第一志愿面试地点")
    second_choice_interview_time = Column(String(50), nullable=True, comment="第二志愿面试时间")
    second_choice_interview_location = Column(String(100), nullable=True, comment="第二志愿面试地点")

    # 二面只保留一个志愿
    second_round_department = Column(String(50), nullable=True, comment="第二轮面试部门")
    second_round_interview_time = Column(String(50), nullable=True, comment="第二轮面试时间")
    second_round_interview_location = Column(String(100), nullable=True, comment="第二轮面试地点")
    
    # 关系
    user = relationship("User", backref="applications")
    signup_config = relationship("SignupConfig", back_populates="applications")
    
    def __repr__(self):
        return f"<Application {self.id} by User {self.user_id} for Config {self.signup_config_id}>"
