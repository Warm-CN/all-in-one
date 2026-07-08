"""
共建意见模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, LargeBinary, Boolean
from app.models.base import BaseModel


class Suggestion(BaseModel):
    """建设意见"""
    __tablename__ = "suggestions"

    title = Column(String(200), nullable=False, comment="标题")
    description = Column(Text, nullable=False, comment="描述")
    category = Column(String(20), nullable=False, default="other", comment="分类: layout/feature/bug/other")
    status = Column(String(20), nullable=False, default="received", comment="状态: received/pending_fix/fixing/wont_fix/done")
    page_url = Column(String(500), nullable=True, comment="关联页面URL")
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="提出者")
    is_anonymous = Column(Integer, nullable=False, default=0, comment="是否匿名: 0=实名, 1=匿名")
    done_at = Column(DateTime, nullable=True, comment="完成时间")
    done_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="修改人")


class Screenshot(BaseModel):
    """截图"""
    __tablename__ = "screenshots"

    suggestion_id = Column(Integer, ForeignKey("suggestions.id", ondelete="CASCADE"), nullable=False, index=True, comment="关联意见")
    image_data = Column(LargeBinary, nullable=False, comment="JPEG压缩数据")
    width = Column(Integer, nullable=False, comment="原图宽度")
    height = Column(Integer, nullable=False, comment="原图高度")


class Annotation(BaseModel):
    """批注"""
    __tablename__ = "annotations"

    screenshot_id = Column(Integer, ForeignKey("screenshots.id", ondelete="CASCADE"), nullable=False, index=True, comment="关联截图")
    type = Column(String(20), nullable=False, comment="类型: rect/freehand/text")
    coords = Column(JSON, nullable=False, comment="坐标")
    text = Column(String(500), nullable=False, comment="文字批注内容")
    color = Column(String(20), nullable=False, default="#EF4444", comment="颜色")


class StatusChange(BaseModel):
    """状态变更记录"""
    __tablename__ = "status_changes"

    suggestion_id = Column(Integer, ForeignKey("suggestions.id", ondelete="CASCADE"), nullable=False, index=True, comment="关联意见")
    from_status = Column(String(20), nullable=True, comment="原状态")
    to_status = Column(String(20), nullable=False, comment="新状态")
    reason = Column(Text, nullable=True, comment="说明/不予修改原因")
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="操作人")


class Reply(BaseModel):
    """讨论回复"""
    __tablename__ = "replies"

    suggestion_id = Column(Integer, ForeignKey("suggestions.id", ondelete="CASCADE"), nullable=False, index=True, comment="关联意见")
    parent_id = Column(Integer, ForeignKey("replies.id", ondelete="CASCADE"), nullable=True, comment="父回复")
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="作者")
    content = Column(Text, nullable=False, comment="内容")
    is_anonymous = Column(Integer, nullable=False, default=0, comment="是否匿名: 0=实名, 1=匿名")
    endorse_count = Column(Integer, nullable=False, default=0, comment="复议数")


class Endorsement(BaseModel):
    """复议记录"""
    __tablename__ = "endorsements"

    reply_id = Column(Integer, ForeignKey("replies.id", ondelete="CASCADE"), nullable=False, index=True, comment="关联回复")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="复议用户")
