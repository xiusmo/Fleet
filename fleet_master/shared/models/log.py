from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, Any

import sqlalchemy as sa
from sqlmodel import Field, Column, JSON, SQLModel


class LogLevel(str, Enum):
    """日志级别枚举"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogCategory(str, Enum):
    """日志类别枚举"""
    SYSTEM = "system"
    TASK = "task"
    WORKER = "worker"
    USER = "user"
    API = "api"
    SECURITY = "security"
    PUSH = "push"
    SCHEDULER = "scheduler"
    OTHER = "other"
    


class Log(SQLModel, table=True):
    """日志模型"""
    __tablename__ = "logs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    level: LogLevel = Field(default=LogLevel.INFO)
    category: LogCategory = Field(default=LogCategory.OTHER)
    message: str
    details: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    source: Optional[str] = None  # 来源，如模块名、函数名
    
    # 可选关联ID
    user_id: Optional[int] = Field(default=None, index=True)
    task_id: Optional[int] = Field(default=None, index=True)
    worker_id: Optional[int] = Field(default=None, index=True) 
    
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=sa.Column(sa.TIMESTAMP(timezone=True), nullable=False)
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=sa.Column(sa.TIMESTAMP(timezone=True))
    )