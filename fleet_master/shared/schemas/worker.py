from datetime import datetime
from typing import Dict, Any, Optional

from pydantic import BaseModel

from shared.models.worker import WorkerStatus


# 共享的基本工作节点属性
class WorkerBase(BaseModel):
    name: str
    description: Optional[str] = None
    endpoint: str
    capabilities: Dict[str, Any] = {}
    subdomain: str


# 创建工作节点请求
class WorkerCreate(WorkerBase):
    pass


# 更新工作节点请求
class WorkerUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    endpoint: Optional[str] = None
    status: Optional[WorkerStatus] = None
    capabilities: Optional[Dict[str, Any]] = None


# 工作节点心跳请求
class WorkerHeartbeat(BaseModel):
    status: WorkerStatus
    last_heartbeat: Optional[datetime] = None


# 工作节点响应
class WorkerResponse(WorkerBase):
    id: int
    status: WorkerStatus
    last_heartbeat: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
