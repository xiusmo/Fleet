from datetime import timedelta, datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.security import verify_password, get_password_hash, create_access_token
from shared.models.user import User
from shared.schemas.user import UserCreate, UserUpdate
from shared.core.config import settings


async def authenticate_user(
    db: AsyncSession, username: str, password: str
) -> Optional[User]:
    """
    验证用户凭据
    """
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    
    if not user or not verify_password(password, user.hashed_password):
        return None
    
    return user


async def get_user_by_uid(db: AsyncSession, uid: str) -> Optional[User]:
    """
    根据uid获取用户
    """
    result = await db.execute(select(User).where(User.username == uid))
    return result.scalars().first()


async def update_cookies_by_uid(db: AsyncSession, uid: str, cookies: dict):
    """
    根据uid更新cookies
    """
    result = await db.execute(select(User).where(User.username == uid))
    user = result.scalars().first()
    user.cx_uf = cookies.get("uf")
    user.cx_d = cookies.get("_d")
    user.cx_vc3 = cookies.get("vc3")
    user.cx_uid = cookies.get("_uid")
    user.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(user)
    return user

async def update_im_cookies_by_uid(db: AsyncSession, uid: str, user_update: UserUpdate):
    """
    根据uid更新im的账号密码
    """
    result = await db.execute(select(User).where(User.username == uid))
    user = result.scalars().first()
    user.im_username = user_update.im_username
    user.im_password = user_update.im_password
    user.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(user)
    return user

async def update_person_info_by_uid(db: AsyncSession, uid: str, user_update: UserUpdate):
    """
    根据uid更新用户信息
    """
    result = await db.execute(select(User).where(User.username == uid))
    user = result.scalars().first()
    user.person_name = user_update.person_name
    user.school_name = user_update.school_name
    user.fid = user_update.fid
    user.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(user)
    return user

async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """
    创建新用户
    """
    # 检查用户名是否已存在
    result = await db.execute(select(User).where(User.username == user_in.username))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在",
        )
    
    # 创建新用户
    user = User(
        username=user_in.username,
        tel=user_in.tel,
        hashed_password=get_password_hash(user_in.password),
        is_active=user_in.is_active,
        is_admin=user_in.is_admin,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def generate_token(user: User) -> str:
    """
    为用户生成JWT访问令牌
    """
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )


