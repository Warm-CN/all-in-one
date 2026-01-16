"""
统一响应格式
"""
from typing import Optional, Any, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    """统一响应模型"""
    code: int = 200
    msg: str = "success"
    data: Optional[T] = None


def success_response(data: Any = None, msg: str = "操作成功") -> dict:
    """成功响应"""
    return {
        "code": 200,
        "msg": msg,
        "data": data
    }


def error_response(code: int, msg: str, data: Any = None) -> dict:
    """错误响应"""
    return {
        "code": code,
        "msg": msg,
        "data": data
    }
