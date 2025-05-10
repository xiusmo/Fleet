from typing import Any, List, Optional
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from shared.schemas.sign_config import SignConfigCreate, SignConfigResponse, SignConfigBase, SignConfigUpdate
from app.api import deps
from shared.models.user import User
from app.services.sign_config import clear_default_for_user, create_sign_config, get_multi_by_user, get_by_uuid, update_sign_config
router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=SignConfigResponse)
async def create_sign_configs(
    *,
    config_in: SignConfigCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """创建签到配置"""
    if config_in.is_default:
        await clear_default_for_user(db=db, user_id=current_user.id)
    
    return await create_sign_config(
        db=db,
        sign_config=config_in,
        user_id=current_user.id
    )


@router.get("/", response_model=List[SignConfigResponse])
async def get_sign_configs(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """获取当前用户的所有签到配置"""
    return await get_multi_by_user(db=db, user_id=current_user.id)


@router.get("/{config_uuid}", response_model=SignConfigBase)
async def get_sign_config(
    *,
    db: AsyncSession = Depends(deps.get_db),
    config_uuid: str,
    current_user: User = Depends(deps.get_current_user)
):
    """获取指定ID的签到配置"""
    config = await get_by_uuid(db=db, uuid=config_uuid)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="签到配置不存在"
        )
    if config.user_id != current_user.id:
        logger.warning(f"用户{current_user.id}无权访问配置{config_uuid}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="无权访问此配置"
        )
    return config


@router.put("/{config_uuid}", response_model=SignConfigResponse)
async def update_sign_configs(
    *,
    db: AsyncSession = Depends(deps.get_db),
    config_uuid: str,
    config_in: SignConfigUpdate,
    current_user: User = Depends(deps.get_current_user)
):
    """更新签到配置"""
    # 如果设置为默认配置，先将其他配置的默认状态取消
    if config_in.is_default:
        await clear_default_for_user(db=db, user_id=current_user.id, exclude_uuid=config_uuid)
    
    return await update_sign_config(
        db=db,
        sign_config=config_in,
        user_id=current_user.id
    )


@router.delete("/{config_uuid}", response_model=SignConfigResponse)
async def delete_sign_config(
    *,
    db: AsyncSession = Depends(deps.get_db),
    config_uuid: str,
    current_user: User = Depends(deps.get_current_user)
):
    """删除签到配置"""
    config = await get_by_uuid(db=db, uuid=config_uuid)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="签到配置不存在"
        )
    if config.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此配置"
        )
    await db.delete(config)
    await db.commit()
    return config
