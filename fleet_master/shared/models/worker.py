from enum import Enum
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from datetime import datetime, timezone
import sqlalchemy as sa
from sqlmodel import Field, Relationship, Column, JSON, SQLModel

if TYPE_CHECKING:
    from shared.models.user import User

class WorkerStatus(str, Enum):
    """工作节点状态枚举"""
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    ERROR = "error"


class Worker(SQLModel, table=True):
    """工作节点模型"""
    __tablename__ = "workers"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: Optional[str] = None
    endpoint: str
    status: WorkerStatus = Field(default=WorkerStatus.OFFLINE)
    last_heartbeat: Optional[datetime] = Field(default=None, sa_column=sa.Column(sa.TIMESTAMP(timezone=True)))
    capabilities: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    
    subdomain: str = Field(unique=True, default=None)
    
    
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=sa.Column(sa.TIMESTAMP(timezone=True), nullable=False)
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=sa.Column(sa.TIMESTAMP(timezone=True))
    )
    
    # 关系
    users: List["User"] = Relationship(back_populates="worker")
