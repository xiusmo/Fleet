from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Optional
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
    activity_id: Optional[int] = None
    course_id: Optional[int] = None
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
    activity_id: Optional[int] = None
    message: Optional[str] = None
    uuid: Optional[str] = None
    detected_at: Optional[datetime] = None
    activity: Optional[Activity] = None
    course_name: Optional[str] = None