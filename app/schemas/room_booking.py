"""
会议室预约相关的 Pydantic Schema
用于请求验证和响应序列化
"""
from pydantic import BaseModel, Field
from datetime import date, time
from typing import Optional


class BookingCreate(BaseModel):
    """创建预约请求"""
    booking_date: date = Field(..., description="预约日期")
    start_time: time = Field(..., description="开始时间")
    end_time: time = Field(..., description="结束时间")
    num_people: int = Field(..., ge=1, description="参与人数（至少1人）")
    remarks: Optional[str] = Field(None, max_length=500, description="备注说明")

    class Config:
        json_schema_extra = {
            "example": {
                "booking_date": "2026-01-28",
                "start_time": "14:00",
                "end_time": "16:00",
                "num_people": 8,
                "remarks": "技术分享会"
            }
        }


class BookingResponse(BaseModel):
    """预约记录响应"""
    id: int
    user_id: int
    booking_date: date
    start_time: time
    end_time: time
    num_people: int
    remarks: Optional[str]
    user_name: Optional[str] = None
    user_dept: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True
