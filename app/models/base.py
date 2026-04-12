"""
数据库模型基类
"""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from app.core.database import Base


class BaseModel(Base):
    """所有模型的基类"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    created_at = Column(DateTime, default=datetime.now, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment="更新时间")
