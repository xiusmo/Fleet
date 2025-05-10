from datetime import datetime, timezone
from typing import List, Optional, Tuple, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from shared.models.worker import Worker, WorkerStatus
from shared.schemas.worker import WorkerCreate, WorkerUpdate, WorkerHeartbeat


async def create_worker(db: AsyncSession, worker_in: WorkerCreate) -> Worker:
    """创建新工作节点"""
    # 检查工作节点名称是否已存在
    result = await db.execute(select(Worker).where(Worker.name == worker_in.name))
    existing_worker = result.scalars().first()
    if existing_worker:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="工作节点名称已存在",
        )
    
    # 创建新工作节点
    worker = Worker(
        name=worker_in.name,
        description=worker_in.description,
        endpoint=worker_in.endpoint,
        capabilities=worker_in.capabilities,
        status=WorkerStatus.ONLINE,
        last_heartbeat=datetime.now(timezone.utc),
        subdomain=worker_in.subdomain,
    )
    
    db.add(worker)
    await db.commit()
    await db.refresh(worker)
    
    return worker


async def get_worker(db: AsyncSession, worker_id: int) -> Optional[Worker]:
    """获取工作节点详情"""
    result = await db.execute(select(Worker).where(Worker.id == worker_id))
    return result.scalars().first()


async def get_workers(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Worker]:
    """获取所有工作节点"""
    result = await db.execute(
        select(Worker).order_by(desc(Worker.created_at)).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def update_worker(
    db: AsyncSession, worker_id: int, worker_in: WorkerUpdate
) -> Optional[Worker]:
    """更新工作节点信息"""
    worker = await get_worker(db, worker_id)
    if not worker:
        return None
    
    # 更新工作节点属性
    update_data = worker_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(worker, field, value)
    
    await db.commit()
    await db.refresh(worker)
    return worker


async def delete_worker(db: AsyncSession, worker_id: int) -> bool:
    """删除工作节点"""
    worker = await get_worker(db, worker_id)
    if not worker:
        return False
    
    await db.delete(worker)
    await db.commit()
    return True


async def update_worker_heartbeat(
    db: AsyncSession, worker_id: int, heartbeat_in: WorkerHeartbeat
) -> Optional[Worker]:
    """更新工作节点心跳信息"""
    worker = await get_worker(db, worker_id)
    if not worker:
        return None
    
    worker.status = heartbeat_in.status
    worker.last_heartbeat = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(worker)
    return worker


async def verify_worker_availability(
    db: AsyncSession, worker_id: int
) -> Tuple[bool, Optional[str]]:
    """
    验证工作节点的可用性
    
    Args:
        db: 数据库会话
        worker_id: 工作节点ID
        
    Returns:
        Tuple[bool, Optional[str]]: (是否可用, 不可用原因)
    """
    worker = await get_worker(db, worker_id)
    if not worker:
        return False, "工作节点不存在"
    
    # 如果工作节点状态为离线，直接返回不可用
    if worker.status == WorkerStatus.OFFLINE:
        return False, "工作节点离线"
    
    # 检查工作节点是否已经繁忙
    if worker.status == WorkerStatus.BUSY:
        return False, "工作节点繁忙"
    
    # 验证工作节点的健康状态
    try:
        from shared.utils.http import AsyncHttpClient
        
        # 创建HTTP客户端
        client = AsyncHttpClient(
            base_url=worker.endpoint,
            timeout=5.0,  # 较短的超时时间
            max_retries=1  # 只尝试一次
        )
        
        # 发送健康检查请求
        async with client:
            try:
                # 使用HEAD请求检查健康端点
                response = await client.head(
                    "/health",
                    ignore_retries=True,
                    raise_for_status=False
                )
                
                # 检查响应状态
                if response.status_code != 200:
                    # 更新工作节点状态为离线
                    worker.status = WorkerStatus.OFFLINE
                    await db.commit()
                    await db.refresh(worker)
                    return False, f"健康检查失败，状态码: {response.status_code}"
                
                # 工作节点可用
                return True, None
            
            except Exception as e:
                # 更新工作节点状态为离线
                worker.status = WorkerStatus.OFFLINE
                await db.commit()
                await db.refresh(worker)
                return False, f"健康检查请求失败: {str(e)}"
    
    except ImportError:
        # 如果HTTP客户端未导入，假设工作节点可用
        return True, None


async def find_available_worker(
    db: AsyncSession,
    capabilities: Optional[Dict[str, Any]] = None
) -> Optional[Worker]:
    """
    查找可用的工作节点
    
    Args:
        db: 数据库会话
        capabilities: 所需的工作节点能力
        
    Returns:
        Optional[Worker]: 可用的工作节点，如果没有则返回None
    """
    # 获取所有在线的工作节点
    result = await db.execute(
        select(Worker).where(Worker.status == WorkerStatus.ONLINE)
    )
    online_workers = result.scalars().all()
    
    # 如果没有在线工作节点，直接返回None
    if not online_workers:
        return None
    
    # 如果指定了所需能力，筛选具有这些能力的工作节点
    if capabilities:
        filtered_workers = []
        for worker in online_workers:
            # 检查工作节点是否具有所有所需能力
            has_capabilities = True
            for key, value in capabilities.items():
                if key not in worker.capabilities or worker.capabilities[key] != value:
                    has_capabilities = False
                    break
            
            if has_capabilities:
                filtered_workers.append(worker)
        
        # 如果没有符合条件的工作节点，返回None
        if not filtered_workers:
            return None
        
        # 使用符合条件的工作节点列表
        workers_to_check = filtered_workers
    else:
        # 使用所有在线工作节点
        workers_to_check = online_workers
    
    # 检查每个工作节点的可用性
    # TODO: 检查每个工作节点的可用性，以及worker的选择逻辑
    for worker in workers_to_check:
        # available, _ = await verify_worker_availability(db, worker.id)
        # if available:
        return worker
    
    # 没有找到可用的工作节点
    return None
