"""
用户模型
"""
from sqlalchemy import Column, String, Enum as SQLEnum, Date
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel


class UserRole(str, enum.Enum):
    """用户角色枚举"""
    VISITOR = "visitor"      # 访客
    MEMBER = "member"        # 成员
    ADMIN = "admin"          # 管理员


class UserStatus(str, enum.Enum):
    """用户状态枚举"""
    PENDING = "pending"      # 待审核
    ACTIVE = "active"        # 已激活
    INACTIVE = "inactive"    # 已停用


class User(BaseModel):
    """用户表"""
    __tablename__ = "users"
    
    real_name = Column(String(50), nullable=False, index=True, comment="真实姓名")
    password_hash = Column(String(255), nullable=False, comment="加密密码")
    student_id = Column(String(20), unique=True, nullable=False, index=True, comment="学号")
    phone = Column(String(11), unique=True, nullable=False, comment="手机号")
    email = Column(String(100), unique=True, nullable=True, comment="邮箱")
    department = Column(String(100), nullable=True, comment="部门")
    position = Column(String(100), nullable=True, comment="职位")
    birthday = Column(Date, nullable=True, comment="生日")
    role = Column(SQLEnum(UserRole), default=UserRole.VISITOR, nullable=False, comment="角色")
    status = Column(SQLEnum(UserStatus), default=UserStatus.PENDING, nullable=False, comment="状态")
    avatar = Column(String(255), nullable=True, comment="头像URL")
    
    # 关系
    bookings = relationship("Booking", back_populates="user", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.student_id} ({self.real_name})>"
