"""
共建意见 Pydantic Schema
"""
from typing import Optional, List
from pydantic import BaseModel


class AnnotationCreate(BaseModel):
    type: str
    coords: dict
    text: str
    color: str = "#EF4444"


class ScreenshotCreate(BaseModel):
    image_data: str
    width: int
    height: int
    annotations: List[AnnotationCreate] = []


class SuggestionCreate(BaseModel):
    title: str
    description: str
    category: str = "other"
    page_url: str = ""
    screenshots: List[ScreenshotCreate] = []


class ReplyCreate(BaseModel):
    content: str
    parent_id: Optional[int] = None


class StatusUpdate(BaseModel):
    status: str
    reason: Optional[str] = None
