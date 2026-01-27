"""
会议室预约 Schema
"""
from pydantic import BaseModel, Field, validator
from datetime import date, time
from typing import Optional


class BookingCreate(BaseModel):
    """创建预约请求"""
    booking_date: date = Field(..., description="预约日期")
    start_time: time = Field(..., description="开始时间")
    end_time: time = Field(..., description="结束时间")
    num_people: int = Field(..., ge=1, le=50, description="人数")
    remarks: Optional[str] = Field(None, max_length=500, description="备注")
    
    @validator('end_time')
    def validate_time_range(cls, v, values):
        """验证结束时间必须晚于开始时间"""
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('结束时间必须晚于开始时间')
        return v


class BookingResponse(BaseModel):
    """预约响应"""
    id: int
    user_id: int
    booking_date: date
    start_time: time
    end_time: time
    num_people: int
    remarks: Optional[str]
    user_name: Optional[str] = None
    user_dept: Optional[str] = None
    
    class Config:
        from_attributes = True
