import uuid
from typing import Dict, List, Optional, TYPE_CHECKING
from datetime import datetime, timezone

from sqlalchemy.sql import func
from sqlmodel import Field, Relationship, Column, String, Integer, Boolean, Float, ForeignKey, DateTime, JSON, SQLModel
from pydantic import field_validator
import sqlalchemy as sa
if TYPE_CHECKING:
    from shared.models.user import User

class SignConfig(SQLModel, table=True):
    """用户签到配置模型，存储用户的签到参数和策略"""
    __tablename__ = 'sign_configs'
    
    id: int = Field(sa_column=Column(Integer, primary_key=True, index=True))
    uuid: str = Field(sa_column=Column(String(100), default=lambda: str(uuid.uuid4()), nullable=False, unique=True))
    user_id: int = Field(sa_column=Column(Integer, ForeignKey('users.id')))
    name: str = Field(sa_column=Column(String(100), default="你没有设置名称"))  # 配置名称
    is_default: bool = Field(sa_column=Column(Boolean, default=False))  # 是否为默认配置
    
    # 策略关联
    course_id: Optional[str] = Field(sa_column=Column(String(50), nullable=True, index=True))  # 课程ID，可为空表示通用配置
    class_id: Optional[str] = Field(sa_column=Column(String(50), nullable=True))  # 班级ID，可为空表示应用于所有班级
    
    # 位置签到
    location_text: Optional[str] = Field(sa_column=Column(String(255), nullable=True))  # 位置文本
    longitude: Optional[float] = Field(sa_column=Column(Float, nullable=True))  # 经度
    latitude: Optional[float] = Field(sa_column=Column(Float, nullable=True))  # 纬度
    # accuracy: float = Field(sa_column=Column(Float, default=5.0))  # 精度，默认5米
    use_random_position: bool = Field(sa_column=Column(Boolean, default=False))  # 位置偏移
    position_offset: float = Field(sa_column=Column(Float, default=0.0001))  # 偏移量 m
    
    # 照片签到
    photo_path: Optional[str] = Field(sa_column=Column(String(255), nullable=True))  # 照片路径
    use_random_photo: bool = Field(sa_column=Column(Boolean, default=False))  # 是否使用随机照片(从照片库中随机选择)
    
    # 高级设置
    custom_headers: Optional[Dict] = Field(sa_column=Column(JSON, nullable=True))  # 自定义请求头
    custom_data: Optional[Dict] = Field(sa_column=Column(JSON, nullable=True))  # 自定义请求数据
    
    # 签到触发策略
    trigger_type: str = Field(sa_column=Column(String(20), default="manual"))  # immediate: 立即签到, threshold: 达到阈值后签到, manual: 手动签到
    threshold_count: int = Field(sa_column=Column(Integer, default=1))  # 触发签到的人数阈值
    threshold_percent: float = Field(sa_column=Column(Float, default=0.0))  # 触发签到的人数百分比阈值
    threshold_time: int = Field(sa_column=Column(Integer, default=1200))  # 签到超时时间(秒)
    poll_interval: int = Field(sa_column=Column(Integer, default=10))  # 轮询间隔(秒)
    
    # 签到行为控制
    sign_delay: int = Field(sa_column=Column(Integer, default=0))  # 签到延迟时间(秒)
    random_delay: int = Field(sa_column=Column(Integer, default=0))  # 随机延迟范围(秒)
    
    # 监控间隔
    monitor_interval: int = Field(sa_column=Column(Integer, default=30))  # 监控间隔(秒)
    
    # 通知设置
    notify_on_detect: bool = Field(sa_column=Column(Boolean, default=True))  # 检测到签到时通知
    notify_on_sign: bool = Field(sa_column=Column(Boolean, default=True))  # 签到完成时通知
    
    ios_bark_key: Optional[str] = Field(sa_column=Column(String(255), nullable=True))  # iOS Bark Key
    android_ntfy_key: Optional[str] = Field(sa_column=Column(String(255), nullable=True))  # Android Bark Key
    
    # 关联关系
    user: Optional["User"] = Relationship(back_populates="sign_configs")
    
    # 时间戳字段（只保留一组）
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=sa.Column(sa.TIMESTAMP(timezone=True), nullable=False)
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=sa.Column(sa.TIMESTAMP(timezone=True))
    )
    
    def __repr__(self):
        return f"<SignConfig(id={self.id}, user_id={self.user_id}, name={self.name}, is_default={self.is_default})>"
     
    @field_validator('threshold_time')
    def validate_threshold_time(cls, v):
        if v < 120:
            v = 120
        if v > 3600:
            v = 3600
        return v
    
    @field_validator('poll_interval')
    def validate_poll_interval(cls, v):
        if v < 3:
            v = 3
        if v > 60:
            v = 60
        return v
