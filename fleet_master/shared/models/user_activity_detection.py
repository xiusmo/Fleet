import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING

from sqlalchemy.sql import func
from sqlmodel import Field, Relationship, Column, Integer, String, ForeignKey, DateTime, Boolean, BigInteger, SQLModel
import sqlalchemy as sa
if TYPE_CHECKING:
    from shared.models.sign_activity import SignActivity
    from shared.models.user import User

class UserActivityDetection(SQLModel, table=True):
    """用户活动检测记录，记录哪个用户检测到了哪个活动"""
    __tablename__ = 'user_activity_detections'
    
    id: int = Field(sa_column=Column(Integer, primary_key=True, index=True))
    uuid: str = Field(sa_column=Column(String(100), default=lambda: str(uuid.uuid4()), nullable=False, unique=True))
    user_id: int = Field(sa_column=Column(Integer, ForeignKey("users.id"), index=True, nullable=False))
    activity_id: str = Field(sa_column=Column(String(50), ForeignKey("sign_activities.activity_id"), index=True, nullable=False))
    course_name: Optional[str] = Field(sa_column=Column(String(100), nullable=True))
    teacher_name: Optional[str] = Field(sa_column=Column(String(100), nullable=True))
    uuid_expires_at: Optional[datetime] = Field(sa_column=Column(DateTime(timezone=True), nullable=True))  # 手签过期时间
    
    detected_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    status: str = Field(sa_column=Column(String(20), default="pending"))  # pending: 待处理, processing: 处理中, polling: 轮询中, success: 成功, failed: 失败, waiting: 等待手动确认中, enc: 等待扫描二维码
    message: Optional[str] = Field(sa_column=Column(String(255), nullable=True))

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=sa.Column(sa.TIMESTAMP(timezone=True), nullable=False)
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=sa.Column(sa.TIMESTAMP(timezone=True))
    )

    # 关系定义
    user: "User" = Relationship(back_populates="detected_activities")
    activity: "SignActivity" = Relationship(back_populates="detected_by_users")
    
    def __repr__(self):
        return f"<UserActivityDetection(id={self.id}, user_id={self.user_id}, activity_id={self.activity_id})>" 
    
    @classmethod
    def from_activity(cls, activity: "SignActivity", user: "User") -> "UserActivityDetection":
        return cls(user_id=user.id, activity_id=activity.activity_id, course_name=activity.course_name, teacher_name=activity.teacher_name, status="pending")
    
    