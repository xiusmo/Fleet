from datetime import datetime, timezone
from enum import Enum
from typing import Optional
import uuid
import sqlalchemy as sa
from sqlmodel import Field, SQLModel

class AnnouncementStatus(str, Enum):
    draft = "draft"
    published = "published"
    scheduled = "scheduled"
    archived = "archived"
    advertisement = "advertisement"



class Announcement(SQLModel, table=True):
    __tablename__ = "announcements"

    id: int = Field(default=None, primary_key=True)
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True, index=True)
    title: str = Field(nullable=False, index=True)
    summary: Optional[str] = Field(nullable=True)
    content: str = Field(nullable=False)
    
    status: AnnouncementStatus = Field(default=AnnouncementStatus.draft, nullable=False)
    is_pinned: bool = Field(default=False, nullable=False)
    publish_date: Optional[datetime] = Field(default=None, nullable=True)
    cover_image: Optional[str] = Field(default=None, nullable=True)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=sa.Column(sa.TIMESTAMP(timezone=True), nullable=False)
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=sa.Column(sa.TIMESTAMP(timezone=True))
    )
