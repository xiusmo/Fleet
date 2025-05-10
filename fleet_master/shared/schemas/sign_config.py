from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime


class SignConfigBase(BaseModel):
    name: Optional[str] = Field("未设置名称", description="配置名称")
    is_default: Optional[bool] = Field(False, description="是否为默认配置")
    
    course_id: Optional[str] = Field(None, description="课程ID")
    class_id: Optional[str] = Field(None, description="班级ID")
    
    location_text: Optional[str] = Field(None, description="位置文本")
    longitude: Optional[float] = Field(None, description="经度")
    latitude: Optional[float] = Field(None, description="纬度")
    # accuracy: Optional[float] = Field(None, description="精度")
    
    use_random_position: Optional[bool] = Field(False, description="是否使用随机位置")
    position_offset: Optional[float] = Field(None, description="位置偏移量(米)")
    
    photo_path: Optional[str] = Field(None, description="照片路径")
    use_random_photo: Optional[bool] = Field(False, description="是否使用随机照片")
    
    custom_headers: Optional[Dict[str, str]] = Field(None, description="自定义请求头")
    custom_data: Optional[Dict[str, Any]] = Field(None, description="自定义请求数据")
    
    trigger_type: Optional[str] = Field("manual", description="触发类型: manual-手动, auto-自动, threshold-阈值")
    threshold_count: Optional[int] = Field(None, description="触发阈值(人数)")
    threshold_percent: Optional[float] = Field(None, description="触发阈值(百分比)")
    threshold_time: Optional[int] = Field(1200, description="触发阈值超时时间(秒)")
    poll_interval: Optional[int] = Field(10, description="触发阈值轮询间隔(秒)")
    
    sign_delay: Optional[int] = Field(None, description="签到延迟(秒)")
    random_delay: Optional[int] = Field(None, description="随机延迟范围(秒)")
    
    monitor_interval: Optional[int] = Field(None, description="监控间隔(秒)")
    
    notify_on_detect: Optional[bool] = Field(False, description="检测到签到任务时通知")
    notify_on_sign: Optional[bool] = Field(False, description="签到成功时通知")
    
    ios_bark_key: Optional[str] = Field(None, description="iOS Bark Key")
    android_ntfy_key: Optional[str] = Field(None, description="Android Bark Key")


class SignConfigResponse(BaseModel):
    name: str
    is_default: bool
    class_id: Optional[str] = None
    uuid: str = None
    
    class Config:
        from_attributes = True


class SignConfigCreate(SignConfigBase):
    pass


class SignConfigUpdate(SignConfigBase):
    uuid: str



class SignConfigInDBBase(SignConfigBase):
    id: int
    user_id: int
    uuid: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SignConfigQueryParams(BaseModel):
    """签到配置查询参数"""
    course_id: Optional[str] = None
    class_id: Optional[str] = None
    is_default: Optional[bool] = None 