from datetime import datetime, timezone
from typing import Any, List, Optional, Dict, TYPE_CHECKING

from sqlalchemy.sql import func
from sqlmodel import Field, Relationship, Column, String, Integer, DateTime, ForeignKey, JSON, Text, Float, BigInteger, Boolean, SQLModel
import sqlalchemy as sa

if TYPE_CHECKING:
    from shared.models.user_activity_detection import UserActivityDetection


class SignActivity(SQLModel, table=True):
    """签到活动模型，用于跟踪签到活动的状态和统计信息"""
    __tablename__ = 'sign_activities'
    
    id: int = Field(sa_column=Column(Integer, primary_key=True, index=True))
    activity_id: str = Field(sa_column=Column(String(50), index=True, unique=True))  # 学习通活动ID
    course_id: str = Field(sa_column=Column(String(50), index=True))  # 课程ID
    course_name: str = Field(sa_column=Column(String(50)))
    class_id: str = Field(sa_column=Column(String(50), index=True))  # 班级ID
    title: str = Field(sa_column=Column(String(100)))  # 活动标题
    other_id: int = Field(sa_column=Column(Integer))  # 签到类型
    sign_type: Optional[str] = Field(sa_column=Column(String(20), nullable=True))  # 签到类型名称
    teacher_name: str = Field(sa_column=Column(String(50)))
    
    # 活动状态
    status: int = Field(sa_column=Column(Integer, default=1))  # 1: 活动中, 2: 已结束
    start_time: datetime = Field(sa_column=Column(DateTime(timezone=True)))  # 活动开始时间
    end_time: datetime = Field(sa_column=Column(DateTime(timezone=True)))  # 活动结束时间
    sign_out_time: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=True))  # 签到结束时间
    time_long: int = Field(sa_column=Column(Integer, default=0))  # 签到时长
    sign_out_time_long: int = Field(sa_column=Column(Integer, default=0))  # 签到结束时长
    manual: bool = Field(sa_column=Column(Boolean, default=False))  # 是否手动结束签到

    
    # 统计信息
    total_users: int = Field(sa_column=Column(Integer, default=0))  # 总用户数
    signed_users: int = Field(sa_column=Column(Integer, default=0))  # 已签到用户数
    sign_percent: float = Field(sa_column=Column(Float, default=0.0))  # 签到百分比
    
    # 签到参数
    need_photo: bool = Field(sa_column=Column(Boolean, default=False))  # 是否需要拍照
    need_location: bool = Field(sa_column=Column(Boolean, default=False))  # 是否需要位置
    location_range: float = Field(sa_column=Column(Float, default=0.0))  # 位置范围（米）
    latitude: float = Field(sa_column=Column(Float, default=0.0))  # 纬度
    longitude: float = Field(sa_column=Column(Float, default=0.0))  # 经度
    address: Optional[str] = Field(sa_column=Column(String(255), nullable=True))  # 地址
    need_code: bool = Field(sa_column=Column(Boolean, default=False))  # 是否需要签到码
    sign_code: Optional[str] = Field(sa_column=Column(String(20), nullable=True))  # 签到码
    need_sign_out: bool = Field(sa_column=Column(Boolean, default=False))  # 是否需要签退
    
    # 验证码相关
    need_captcha: bool = Field(sa_column=Column(Boolean, default=False))  # 是否需要人机验证码
    captcha_type: Optional[str] = Field(sa_column=Column(String(20), nullable=True))  # 验证码类别，例如：image, slider, click等
    need_face: bool = Field(sa_column=Column(Boolean, default=False))  # 是否需要人脸识别
    
    # 签到人数更新时间
    attend_update_at: Optional[datetime] = Field(sa_column=Column(DateTime(timezone=True), nullable=True))  # 签到人数更新时间
    
    # 检测到此活动的所有用户
    detected_by_users: List["UserActivityDetection"] = Relationship(back_populates="activity")
    
    # 时间戳字段（只保留一组）
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=sa.Column(sa.TIMESTAMP(timezone=True), nullable=False)
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=sa.Column(sa.TIMESTAMP(timezone=True))
    )
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any], course_id: str, class_id: str, course_name: str, teacher_name: str) -> "SignActivity":
        def parse_time(key: str) -> datetime:
            value = data.get(key)
            if value:
                return datetime.fromisoformat(value.replace(" ", "").replace("Z", "+00:00"))
            return None

        return cls(
            course_id=course_id,
            course_name=course_name,
            class_id=class_id,
            teacher_name=teacher_name,
            activity_id=data["activity_id"],
            title=data["name"],
            start_time=parse_time("starttime"),
            end_time=parse_time("endtime"),
            createtime=parse_time("createtime"),
            manual=data["manual"],
            need_location=data["need_location"],
            late_minute=data["late_minute"],
            time_long=data["time_long"],
            need_photo=data["need_photo"],
            other_id=data["other_id"],
            need_captcha=data["need_vcode"],
            need_face=data["need_face"],
            need_sign_out=data["need_sign_out"],
            sign_out_time=parse_time("sign_out_time"),
            sign_out_time_long=data["sign_out_time_long"],
            sign_code=data["sign_code"],
            need_code=data["need_code"],
            latitude=data["latitude"],
            longitude=data["longitude"],
            address=data["address"],
            location_range=data["location_range"],
        )
    