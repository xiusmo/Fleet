from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import datetime, timezone

from shared.models.announcement import Announcement, AnnouncementStatus
from shared.models.user import User
from shared.db.session import get_db
from shared.schemas.announcement import AnnouncementCreate, AnnouncementUpdate, AnnouncementOut
from app.api.deps import get_current_active_admin

router = APIRouter()


@router.post("/", response_model=AnnouncementOut)
async def create_announcement(
    announcement_in: AnnouncementCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin),
):
    """创建公告（管理员）"""
    announcement = Announcement(**announcement_in.model_dump())
    db.add(announcement)
    await db.commit()
    await db.refresh(announcement)
    return announcement


@router.get("/active-list", response_model=List[AnnouncementOut])
async def get_active_announcements(
    db: AsyncSession = Depends(get_db),
):
    """获取已发布的公告（公开接口）"""
    result = await db.execute(
        select(Announcement)
        .where((Announcement.status == AnnouncementStatus.published) | (Announcement.status == AnnouncementStatus.advertisement))
        .order_by(Announcement.publish_date.desc())
        .limit(10)
    )
    return result.scalars().all()


@router.get("/{uuid}", response_model=AnnouncementOut)
async def get_announcement_by_uuid(
    uuid: str,
    db: AsyncSession = Depends(get_db),
):
    """根据uuid获取公告（公开接口）"""
    result = await db.execute(select(Announcement).where(Announcement.uuid == uuid))
    announcement = result.scalars().first()
    if not announcement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="公告未找到")
    return announcement


@router.get("/", response_model=List[AnnouncementOut])
async def get_all_announcements(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin),
):
    """获取所有公告（管理员）"""
    result = await db.execute(select(Announcement).offset(skip).limit(limit))
    return result.scalars().all()


@router.put("/{uuid}", response_model=AnnouncementOut)
async def update_announcement(
    uuid: str,
    announcement_in: AnnouncementUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin),
):
    """更新公告（管理员）"""
    result = await db.execute(select(Announcement).where(Announcement.uuid == uuid))
    announcement = result.scalars().first()
    if not announcement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="公告未找到")
    
    update_data = announcement_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(announcement, key, value)
    
    # 手动更新updated_at为当前的UTC时间
    announcement.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(announcement)
    return announcement


@router.delete("/{uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_announcement(
    uuid: str,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin),
):
    """删除公告（管理员）"""
    result = await db.execute(select(Announcement).where(Announcement.uuid == uuid))
    announcement = result.scalars().first()
    if not announcement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="公告未找到")
    
    await db.delete(announcement)
    await db.commit()
    return None



