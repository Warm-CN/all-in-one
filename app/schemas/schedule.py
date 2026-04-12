"""
日程相关的 Pydantic Schema
用于请求验证和响应序列化
"""
from pydantic import BaseModel, Field
from datetime import date, time
from typing import Optional


class ScheduleCreate(BaseModel):
    """创建日程请求"""
    title: str = Field(..., min_length=1, max_length=200, description="日程标题")
    schedule_date: date = Field(..., description="日程日期")
    start_time: time = Field(..., description="开始时间")
    end_time: time = Field(..., description="结束时间")
    location: Optional[str] = Field(None, max_length=200, description="地点")
    color: str = Field(default="#3B82F6", max_length=20, description="颜色标记")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "技术分享会",
                "schedule_date": "2026-02-01",
                "start_time": "14:00",
                "end_time": "16:00",
                "location": "北三会议室",
                "color": "#3B82F6"
            }
        }


class ScheduleResponse(BaseModel):
    """日程记录响应"""
    id: int
    title: str
    schedule_date: date
    start_time: time
    end_time: time
    location: Optional[str]
    color: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
