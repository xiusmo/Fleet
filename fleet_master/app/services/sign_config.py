from datetime import datetime, timezone
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from sqlalchemy.future import select
from shared.models.sign_config import SignConfig
from shared.schemas.sign_config import SignConfigCreate, SignConfigUpdate
from shared.models.user import User

async def clear_default_for_user(db: AsyncSession, user_id: int, exclude_uuid: Optional[str] = None):
    """清除用户的默认签到配置"""
    # 方法1：使用查询先获取配置项，然后逐个更新
    query = select(SignConfig).where(SignConfig.user_id == user_id, SignConfig.is_default == True)
    if exclude_uuid:
        query = query.where(SignConfig.uuid != exclude_uuid)
    
    result = await db.execute(query)
    configs = result.scalars().all()
    
    for config in configs:
        config.is_default = False
    
    # 提交更新
    if configs:
        await db.commit()
    
    return len(configs)


async def update_sign_config(
    db: AsyncSession, sign_config: SignConfigUpdate, user_id: int
):
    """更新签到配置"""
    existing = await db.execute(
        select(SignConfig).where(SignConfig.uuid == sign_config.uuid)
    )
    existing = existing.scalars().first()
    if existing:
        if existing.user_id != user_id:
            raise HTTPException(status_code=400, detail="签到配置不属于当前用户")

        # 更新已有对象字段
        for key, value in sign_config.model_dump().items():
            setattr(existing, key, value)
        existing.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(existing)
        return existing
    else:
        raise HTTPException(status_code=404, detail="签到配置不存在")
    

async def create_sign_config(
    db: AsyncSession, sign_config: SignConfigCreate, user_id: int
):
    """创建签到配置"""
    sign_config_db = SignConfig(**sign_config.model_dump())
    sign_config_db.user_id = user_id
    db.add(sign_config_db)
    await db.commit()
    await db.refresh(sign_config_db)
    return sign_config_db


async def get_multi_by_user(db: AsyncSession, user_id: int):
    """获取用户的所有签到配置"""
    result = await db.execute(
        select(SignConfig).where(SignConfig.user_id == user_id)
    )
    return result.scalars().all()


async def get_by_uuid(db: AsyncSession, uuid: str):
    """获取指定ID的签到配置"""
    result = await db.execute(
        select(SignConfig)
        .where(SignConfig.uuid == uuid)
        .limit(1)
    )
    return result.scalars().first()



async def get_config_for_sign(db: AsyncSession, user: User, class_id: Optional[str] = None) -> SignConfig:
    if class_id:
        result = await db.execute(
            select(SignConfig)
            .where(SignConfig.user_id == user.id, SignConfig.class_id == class_id)
            .limit(1)
        )
        config = result.scalars().first()
        if config:
            return config
    
    result = await db.execute(
        select(SignConfig)
        .where(SignConfig.user_id == user.id, SignConfig.is_default == True)
        .limit(1)
    )
    config = result.scalars().first()
    if config:
        return config
    
    return SignConfig(trigger_type="manual", use_random_photo=True)
    
    
    