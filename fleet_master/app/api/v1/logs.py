from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.deps import get_current_active_admin
from shared.db.session import get_db
from shared.models.log import Log, LogLevel, LogCategory
from shared.models.user import User
from shared.schemas.log import LogResponse, LogFilter
from shared.utils.logger import get_logger, DBLogger

router = APIRouter()


@router.get("", response_model=List[LogResponse])
async def get_logs(
    level: Optional[LogLevel] = None,
    category: Optional[LogCategory] = None,
    user_id: Optional[int] = None,
    task_id: Optional[int] = None,
    worker_id: Optional[int] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
    logger: DBLogger = Depends(get_logger)
):
    """
    获取日志列表（管理员）
    """
    # 记录查询日志的操作
    await logger.info(
        f"管理员查询日志",
        category=LogCategory.SYSTEM,
        user_id=current_user.id,
        details={
            "filters": {
                "level": level,
                "category": category,
                "user_id": user_id,
                "task_id": task_id,
                "worker_id": worker_id,
                "search": search,
                "skip": skip,
                "limit": limit
            }
        }
    )
    
    # 构建查询
    query = select(Log)
    
    # 添加筛选条件
    if level:
        query = query.where(Log.level == level)
    if category:
        query = query.where(Log.category == category)
    if user_id:
        query = query.where(Log.user_id == user_id)
    if task_id:
        query = query.where(Log.task_id == task_id)
    if worker_id:
        query = query.where(Log.worker_id == worker_id)
    
    # 搜索
    if search:
        query = query.where(
            or_(
                Log.message.contains(search),
                Log.source.contains(search)
            )
        )
    
    # 分页和排序
    query = query.order_by(Log.created_at.desc()).offset(skip).limit(limit)
    
    # 执行查询
    result = await db.execute(query)
    logs = result.scalars().all()
    
    return logs


@router.delete("/{log_id}")
async def delete_log(
    log_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
    logger: DBLogger = Depends(get_logger)
):
    """
    删除日志（管理员）
    """
    # 查找日志
    result = await db.execute(select(Log).where(Log.id == log_id))
    log = result.scalars().first()
    
    if not log:
        await logger.warning(
            f"尝试删除不存在的日志 ID: {log_id}",
            category=LogCategory.SYSTEM,
            user_id=current_user.id
        )
        return {"message": "日志不存在"}
    
    # 删除日志
    await db.delete(log)
    await db.commit()
    
    # 记录删除操作
    await logger.warning(
        f"删除日志 ID: {log_id}",
        category=LogCategory.SYSTEM,
        user_id=current_user.id,
        details={"deleted_log_id": log_id}
    )
    
    return {"message": "日志已删除"}


@router.delete("")
async def clear_logs(
    filter: LogFilter,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
    logger: DBLogger = Depends(get_logger)
):
    """
    清空符合条件的日志（管理员）
    """
    # 构建查询
    query = select(Log)
    
    # 添加筛选条件
    if filter.level:
        query = query.where(Log.level == filter.level)
    if filter.category:
        query = query.where(Log.category == filter.category)
    if filter.user_id:
        query = query.where(Log.user_id == filter.user_id)
    if filter.task_id:
        query = query.where(Log.task_id == filter.task_id)
    if filter.worker_id:
        query = query.where(Log.worker_id == filter.worker_id)
    if filter.start_date:
        query = query.where(Log.created_at >= filter.start_date)
    if filter.end_date:
        query = query.where(Log.created_at <= filter.end_date)
    if filter.search:
        query = query.where(
            or_(
                Log.message.contains(filter.search),
                Log.source.contains(filter.search)
            )
        )
    
    # 执行查询以获取要删除的日志数量
    result = await db.execute(query)
    logs = result.scalars().all()
    count = len(logs)
    
    # 删除日志
    if count > 0:
        for log in logs:
            await db.delete(log)
        await db.commit()
    
    # 记录清空操作
    await logger.warning(
        f"清空 {count} 条日志",
        category=LogCategory.SYSTEM,
        user_id=current_user.id,
        details={"filter": filter.dict(), "deleted_count": count}
    )
    
    return {"message": f"已清空 {count} 条日志"} 