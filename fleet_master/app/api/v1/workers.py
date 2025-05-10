from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_admin
from shared.db.session import get_db
from shared.models.user import User
from shared.schemas.worker import WorkerCreate, WorkerUpdate, WorkerResponse, WorkerHeartbeat
from app.services.worker import (
    create_worker, get_worker, get_workers, update_worker,
    delete_worker, update_worker_heartbeat
)

router = APIRouter()


@router.post("", response_model=WorkerResponse)
async def register_worker(
    worker_in: WorkerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    注册新工作节点（管理员）
    """
    return await create_worker(db, worker_in)


@router.get("", response_model=List[WorkerResponse])
async def read_workers(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    获取所有工作节点（管理员）
    """
    return await get_workers(db, skip, limit)


@router.get("/{worker_id}", response_model=WorkerResponse)
async def read_worker(
    worker_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    获取指定工作节点详情（管理员）
    """
    worker = await get_worker(db, worker_id)
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工作节点不存在"
        )
    return worker


@router.put("/{worker_id}", response_model=WorkerResponse)
async def update_worker_info(
    worker_id: int,
    worker_in: WorkerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    更新工作节点信息（管理员）
    """
    worker = await update_worker(db, worker_id, worker_in)
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工作节点不存在"
        )
    return worker


@router.delete("/{worker_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_worker(
    worker_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    删除工作节点（管理员）
    """
    result = await delete_worker(db, worker_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工作节点不存在"
        )


@router.post("/{worker_id}/heartbeat", response_model=WorkerResponse)
async def heartbeat(
    worker_id: int,
    heartbeat_in: WorkerHeartbeat,
    db: AsyncSession = Depends(get_db)
):
    """
    更新工作节点心跳信息（供工作节点调用）
    """
    worker = await update_worker_heartbeat(db, worker_id, heartbeat_in)
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工作节点不存在"
        )
    return worker
