from datetime import datetime
from typing import Dict, Any, Optional, List

from pydantic import BaseModel

from shared.models.log import LogLevel, LogCategory


class LogBase(BaseModel):
    """日志基本模型"""
    level: LogLevel
    category: LogCategory
    message: str
    details: Dict[str, Any] = {}
    source: Optional[str] = None
    user_id: Optional[int] = None
    task_id: Optional[int] = None
    worker_id: Optional[int] = None


class LogCreate(LogBase):
    """创建日志请求"""
    pass


class LogResponse(LogBase):
    """日志响应模型"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class LogFilter(BaseModel):
    """日志筛选条件"""
    level: Optional[LogLevel] = None
    category: Optional[LogCategory] = None
    user_id: Optional[int] = None
    task_id: Optional[int] = None
    worker_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search: Optional[str] = None 