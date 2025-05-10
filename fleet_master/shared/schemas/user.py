from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# 共享属性
class UserBase(BaseModel):
    username: str
    tel: str
    is_active: Optional[bool] = True
    is_admin: Optional[bool] = False
    im_username: Optional[str] = None
    im_password: Optional[str] = None
    person_name: Optional[str] = None
    school_name: Optional[str] = None
    fid: Optional[str] = None 


# 创建新用户时的请求
class UserCreate(UserBase):
    password: str


# 更新用户信息时的请求
class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    tel: Optional[str] = None
    cx_d: Optional[str] = None
    cx_uf: Optional[str] = None
    cx_vc3: Optional[str] = None
    cx_uid: Optional[str] = None
    im_username: Optional[str] = None
    im_password: Optional[str] = None
    person_name: Optional[str] = None
    school_name: Optional[str] = None
    fid: Optional[str] = None
    
    @field_validator("tel", mode="before")
    def validate_tel(cls, v):
        if not isinstance(v, str):
            v = str(v)
        return v
    
    @field_validator("username", mode="before")
    def validate_username(cls, v):
        if not isinstance(v, str):
            v = str(v)
        return v
    
    @field_validator("im_username", mode="before")
    def validate_im_username(cls, v):
        if not isinstance(v, str):
            v = str(v)
        return v
    
    @field_validator("im_password", mode="before")
    def validate_im_password(cls, v):
        if not isinstance(v, str):
            v = str(v)
        return v
    
    @field_validator("fid", mode="before")
    def validate_fid(cls, v):
        if not isinstance(v, str):
            v = str(v)
        return v


# API响应中的用户信息
class UserResponse(BaseModel):
    created_at: datetime
    updated_at: Optional[datetime] = None
    person_name: Optional[str] = None
    class Config:
        from_attributes = True

class UserResponseForAdmin(UserResponse):
    id: Optional[int] = None
    tel: Optional[str] = None
    is_active: Optional[bool] = None
    school_name: Optional[str] = None

# 用于登录的凭据
class UserLogin(BaseModel):
    username: str
    password: str


# 令牌响应
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# 令牌载荷
class TokenPayload(BaseModel):
    sub: Optional[int] = None
    

class UserDetail(UserResponse):
    id: Optional[int] = None
    username: Optional[str] = None
    im_username: Optional[str] = None
    im_password: Optional[str] = None
    tel: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    cx_d: Optional[str] = None
    cx_uf: Optional[str] = None
    cx_vc3: Optional[str] = None
    cx_uid: Optional[str] = None
    fid: Optional[str] = None
    hashed_password: Optional[str] = None
    school_name: Optional[str] = None
    person_name: Optional[str] = None
    worker_name: Optional[str] = None
    is_admin: Optional[bool] = None
    is_active: Optional[bool] = None
    monitor_status: Optional[bool] = None
    
    
    
