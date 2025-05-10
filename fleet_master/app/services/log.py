from typing import List, Optional, Dict, Any
import inspect
import traceback
from datetime import datetime

from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from shared.models.log import Log, LogLevel, LogCategory


async def add_log(
    db: AsyncSession,
    message: str,
    level: LogLevel = LogLevel.INFO,
    category: LogCategory = LogCategory.OTHER,
    details: Dict[str, Any] = None,
    source: str = None,
    user_id: Optional[int] = None,
    task_id: Optional[int] = None,
    worker_id: Optional[int] = None
) -> Log:
    """添加日志到数据库"""
    # 如果没有指定source，尝试自动获取调用者信息
    if not source:
        frame = inspect.currentframe().f_back
        if frame:
            module = frame.f_globals.get('__name__', '')
            func = frame.f_code.co_name
            source = f"{module}.{func}"
    
    # 创建日志记录
    log = Log(
        level=level,
        category=category,
        message=message,
        details=details or {},
        source=source,
        user_id=user_id,
        task_id=task_id,
        worker_id=worker_id
    )
    
    db.add(log)
    await db.commit()
    await db.refresh(log)
    
    return log


async def get_logs(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    level: Optional[LogLevel] = None,
    category: Optional[LogCategory] = None,
    user_id: Optional[int] = None,
    task_id: Optional[int] = None,
    worker_id: Optional[int] = None
) -> List[Log]:
    """获取日志列表，支持多种筛选条件"""
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
    
    # 按时间降序排序
    query = query.order_by(desc(Log.created_at))
    
    # 分页
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


async def log_exception(
    db: AsyncSession,
    exception: Exception,
    message: str = None,
    category: LogCategory = LogCategory.SYSTEM,
    user_id: Optional[int] = None,
    task_id: Optional[int] = None,
    worker_id: Optional[int] = None
) -> Log:
    """记录异常到日志"""
    # 获取异常信息
    exc_type = type(exception).__name__
    exc_message = str(exception)
    exc_traceback = traceback.format_exc()
    
    # 如果没有提供自定义消息，使用异常类型和消息
    if not message:
        message = f"{exc_type}: {exc_message}"
    
    # 详细信息
    details = {
        "exception_type": exc_type,
        "exception_message": exc_message,
        "traceback": exc_traceback
    }
    
    # 调用添加日志函数
    return await add_log(
        db=db,
        message=message,
        level=LogLevel.ERROR,
        category=category,
        details=details,
        user_id=user_id,
        task_id=task_id,
        worker_id=worker_id
    ) 