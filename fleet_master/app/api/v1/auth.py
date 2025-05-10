import re
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from shared.utils.logger import DBLogger, get_logger
from shared.db.session import get_db
from shared.models.user import User
from shared.schemas.user import UserCreate, UserResponse, Token
from app.services.auth import authenticate_user, create_user, generate_token
from app.services.cx_login import login_by_cx
from shared.utils.http import AsyncHttpClient, get_http_client
from shared.core.config import settings

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    获取当前登录用户信息
    """
    return current_user

class LoginRequestSchema(BaseModel):
    username: str = Field(..., title="手机号", example="13812345678")
    password: str = Field(..., title="密码", min_length=1)
    turnstileToken: str = Field(..., title="Turnstile验证令牌")

    @field_validator('username')
    def validate_phone(cls, v: str):
        # 中国大陆手机号格式校验（11位数字，以 1 开头，第二位为3~9）
        if not re.fullmatch(r"1[3-9]\d{9}", v):
            raise ValueError("请输入有效的手机号")
        return v

async def verify_turnstile(token: str, http: AsyncHttpClient, logger: DBLogger) -> bool:
    """验证Turnstile令牌"""
    try:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data={
            "secret": settings.TURNSTILE_SECRET_KEY,
            "response": token,
        }
        await logger.info(f"验证Turnstile令牌: {data}")
        response = await http.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            headers=headers,
            data=data
            )
        result = response.json()
        return result.get("success", False)
    except Exception as e:
        print(f"Turnstile验证出错: {str(e)}")
        return False

@router.post("/cx_login", response_model=Token)
async def cx_login(
    login_request: LoginRequestSchema,
    db: AsyncSession = Depends(get_db),
    http: AsyncHttpClient = Depends(get_http_client),
    logger: DBLogger = Depends(get_logger)
):
    """
    超星登录
    """
    # 验证Turnstile令牌
    is_valid = await verify_turnstile(login_request.turnstileToken, http, logger)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="人机验证失败，请重试",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = await login_by_cx(db = db, http = http, tel = login_request.username, password = login_request.password)
    return {"access_token": token, "token_type": "bearer"}
    
    
