from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from shared.models.announcement import AnnouncementStatus


# Pydantic 模型（数据校验和返回模型）
class AnnouncementBase(BaseModel):
    title: str
    summary: Optional[str] = None
    content: str
    status: AnnouncementStatus = AnnouncementStatus.draft
    is_pinned: bool = False
    publish_date: Optional[datetime] = None
    cover_image: Optional[str] = None
    uuid: Optional[str] = None


class AnnouncementCreate(AnnouncementBase):
    pass


class AnnouncementUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    status: Optional[AnnouncementStatus] = None
    is_pinned: Optional[bool] = None
    publish_date: Optional[datetime] = None
    cover_image: Optional[str] = None


class AnnouncementOut(AnnouncementBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True