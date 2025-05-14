from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Optional, Any
class SignActivityFromWS(BaseModel):
    activity_id: str = Field(..., description="活动的唯一标识符", alias="aid")
    class_id: str = Field(..., description="班级的唯一标识符", alias="classid")
    course_id: str = Field(..., description="课程的唯一标识符", alias="courseid")
    course_name: str = Field(..., description="课程名称", alias="coursename")
    teacher_name: str = Field(..., description="教师名称", alias="teacherfactor")
    title: str = Field(..., description="事件标题，如 '签到'", alias="title")
    detected_at: datetime = Field(..., description="事件检测的时间戳（ISO 8601 格式）")
    detected_by: str = Field(..., description="检测者的唯一标识符")
    cookies: Optional[Dict[str, str]] = Field(None, description="cookies")
    

class Activity(BaseModel):
    activity_id: Optional[str] = None
    course_id: Optional[str] = None
    class_id: Optional[str] = None
    title: Optional[str] = None
    other_id: Optional[int] = None
    sign_type: Optional[str] = None
    status: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_users: Optional[int] = None
    signed_users: Optional[int] = None
    sign_percent: Optional[float] = None
    need_photo: Optional[bool] = None
    need_location: Optional[bool] = None
    location_range: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    need_code: Optional[bool] = None
    sign_code: Optional[str] = None
    need_captcha: Optional[bool] = None
    captcha_type: Optional[str] = None
    attend_update_at: Optional[datetime] = None
    teacher_name: Optional[str] = None


class UserActivityDetectionResponse(BaseModel):
    status: str  
    activity_id: Optional[str] = None
    message: Optional[str] = None
    uuid: Optional[str] = None
    detected_at: Optional[datetime] = None
    activity: Optional[Activity] = None
    course_name: Optional[str] = None

# 新增 API 响应模型，专门用于处理后端 API 返回的数据
class APIActivityResponse(BaseModel):
    """用于解析后端 API 返回的活动数据"""
    activity_id: str
    name: str = Field(description="活动标题")
    starttime: Optional[str] = Field(None, description="开始时间字符串")
    endtime: Optional[str] = Field(None, description="结束时间字符串")
    createtime: Optional[str] = Field(None, description="创建时间字符串")
    manual: bool = Field(default=False, description="是否手动结束签到")
    need_location: bool = Field(default=False, description="是否需要位置签到")
    late_minute: Optional[int] = Field(None, description="迟到分钟数")
    time_long: int = Field(default=0, description="签到时长")
    need_photo: bool = Field(default=False, description="是否需要拍照")
    other_id: int = Field(description="签到类型ID")
    need_captcha: bool = Field(default=False, description="是否需要验证码", alias="need_captcha")
    need_face: bool = Field(default=False, description="是否需要人脸识别")
    need_sign_out: bool = Field(default=False, description="是否需要签退")
    sign_out_time: Optional[str] = Field(None, description="签退时间字符串")
    sign_out_time_long: Optional[int] = Field(0, description="签退时长")
    sign_code: Optional[str] = Field(None, description="签到码")
    need_code: bool = Field(default=False, description="是否需要签到码")
    latitude: float = Field(default=0.0, description="纬度")
    longitude: float = Field(default=0.0, description="经度")
    address: Optional[str] = Field(None, description="地址")
    location_range: Optional[float] = Field(0.0, description="位置范围")

    @classmethod
    def parse_datetime(cls, value: Optional[str]) -> Optional[datetime]:
        """将 API 返回的时间字符串转换为 datetime 对象"""
        if not value:
            return None
        try:
            # 处理常见的格式问题
            value = value.replace(" ", "").replace("Z", "+00:00")
            return datetime.fromisoformat(value)
        except (ValueError, TypeError):
            return None

    def to_sign_activity(self, course_id: str, class_id: str, course_name: str, teacher_name: str) -> Dict[str, Any]:
        """将 API 响应转换为 SignActivity 模型需要的数据字典"""
        return {
            "activity_id": self.activity_id,
            "title": self.name,  # 字段映射
            "course_id": course_id,
            "class_id": class_id,
            "course_name": course_name,
            "teacher_name": teacher_name,
            "start_time": self.parse_datetime(self.starttime),
            "end_time": self.parse_datetime(self.endtime),
            "manual": self.manual,
            "need_location": self.need_location,
            "time_long": self.time_long,
            "need_photo": self.need_photo,
            "other_id": self.other_id,
            "need_captcha": self.need_captcha,  # 字段映射
            "need_face": self.need_face,
            "need_sign_out": self.need_sign_out,
            "sign_out_time": self.parse_datetime(self.sign_out_time),
            "sign_out_time_long": self.sign_out_time_long,
            "sign_code": self.sign_code,
            "need_code": self.need_code,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "address": self.address,
            "location_range": self.location_range,
        }