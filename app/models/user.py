"""
用户模型
"""
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class User(BaseModel):
    """用户表"""
    __tablename__ = "users"
    
    # 核心字段
    student_id = Column(String(20), unique=True, nullable=False, index=True, comment="学号（用于登录）")
    password_hash = Column(String(255), nullable=False, comment="加密密码")
    
    # 档案与联系信息
    full_name = Column(String(50), nullable=False, comment="真实姓名")
    phone = Column(String(20), nullable=True, comment="手机号")
    email = Column(String(100), nullable=True, comment="电子邮箱")
    department = Column(String(50), nullable=True, comment="所属部门")
    position = Column(String(50), nullable=True, comment="职位")
    
    # 权限与状态控制
    role = Column(String(20), default='member', nullable=False, comment="角色：admin 或 member")
    status = Column(String(20), default='pending', nullable=False, comment="状态：pending/active/rejected/disabled")
    
    # 关系 (由 RoomBooking 反向引用，无需显式定义)
    
    def __repr__(self):
        return f"<User {self.student_id} ({self.full_name})>"

