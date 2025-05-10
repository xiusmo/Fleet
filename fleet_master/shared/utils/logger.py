import logging
import functools
import inspect
from typing import Dict, Any, Optional, Callable, TypeVar, Awaitable

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.db.session import get_db
from shared.models.log import LogLevel, LogCategory
from app.services.log import add_log, log_exception

# 标准logger，用于控制台输出
logger = logging.getLogger("app")

# 类型定义
T = TypeVar("T")
AsyncFunc = Callable[..., Awaitable[T]]


class DBLogger:
    """数据库日志工具类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def log(
        self,
        message: str,
        level: LogLevel = LogLevel.INFO,
        category: LogCategory = LogCategory.OTHER,
        details: Dict[str, Any] = None,
        source: str = None,
        user_id: Optional[int] = None,
        task_id: Optional[int] = None,
        worker_id: Optional[int] = None
    ):
        """记录日志到数据库"""
        # 如果没有指定source，尝试自动获取调用者信息
        if not source:
            frame = inspect.currentframe().f_back
            if frame:
                module = frame.f_globals.get('__name__', '')
                func = frame.f_code.co_name
                source = f"{module}.{func}"
        
        # 同时输出到控制台
        log_msg = f"[{level}] {message}"
        if category != LogCategory.OTHER:
            log_msg = f"[{category}] {log_msg}"
        
        if level == LogLevel.DEBUG:
            logger.debug(log_msg)
        elif level == LogLevel.INFO:
            logger.info(log_msg)
        elif level == LogLevel.WARNING:
            logger.warning(log_msg)
        elif level == LogLevel.ERROR:
            logger.error(log_msg)
        elif level == LogLevel.CRITICAL:
            logger.critical(log_msg)
        
        # 记录到数据库
        return await add_log(
            db=self.db,
            message=message,
            level=level,
            category=category,
            details=details or {},
            source=source,
            user_id=user_id,
            task_id=task_id,
            worker_id=worker_id
        )
    
    async def debug(self, message: str, **kwargs):
        """记录DEBUG级别日志"""
        return await self.log(message, level=LogLevel.DEBUG, **kwargs)
    
    async def info(self, message: str, **kwargs):
        """记录INFO级别日志"""
        return await self.log(message, level=LogLevel.INFO, **kwargs)
    
    async def warning(self, message: str, **kwargs):
        """记录WARNING级别日志"""
        return await self.log(message, level=LogLevel.WARNING, **kwargs)
    
    async def error(self, message: str, **kwargs):
        """记录ERROR级别日志"""
        return await self.log(message, level=LogLevel.ERROR, **kwargs)
    
    async def critical(self, message: str, **kwargs):
        """记录CRITICAL级别日志"""
        return await self.log(message, level=LogLevel.CRITICAL, **kwargs)
    
    async def exception(self, exc: Exception, message: str = None, **kwargs):
        """记录异常"""
        return await log_exception(
            db=self.db,
            exception=exc,
            message=message,
            **kwargs
        )


def get_logger(db: AsyncSession = Depends(get_db)) -> DBLogger:
    """依赖项，用于获取日志工具实例"""
    return DBLogger(db)


def log_operation(
    level: LogLevel = LogLevel.INFO,
    category: LogCategory = LogCategory.OTHER,
    message: str = None
):
    """
    装饰器：记录函数操作到日志
    
    用法示例：
    @log_operation(level=LogLevel.INFO, category=LogCategory.TASK, message="处理任务")
    async def process_task(task_id: int, db: AsyncSession = Depends(get_db)):
        ...
    """
    def decorator(func: AsyncFunc) -> AsyncFunc:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # 尝试从参数中获取db会话
            db = kwargs.get('db')
            if not db:
                for arg in args:
                    if isinstance(arg, AsyncSession):
                        db = arg
                        break
            
            if not db:
                # 如果找不到db会话，只能使用标准logger
                logger.warning(f"无法记录数据库日志，找不到数据库会话: {func.__name__}")
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    logger.exception(f"函数执行出错: {func.__name__}")
                    raise
            
            # 创建日志工具
            db_logger = DBLogger(db)
            
            # 获取函数信息
            func_name = func.__name__
            module_name = func.__module__
            source = f"{module_name}.{func_name}"
            
            # 构建日志消息
            log_message = message or f"执行函数 {func_name}"
            
            # 提取关联ID
            user_id = kwargs.get('user_id')
            if not user_id and 'current_user' in kwargs:
                user_id = getattr(kwargs['current_user'], 'id', None)
            
            task_id = kwargs.get('task_id')
            worker_id = kwargs.get('worker_id')
            
            try:
                # 记录开始执行的日志
                await db_logger.log(
                    message=f"{log_message} - 开始",
                    level=level,
                    category=category,
                    source=source,
                    user_id=user_id,
                    task_id=task_id,
                    worker_id=worker_id,
                    details={"args": str(args), "kwargs": str(kwargs)}
                )
                
                # 执行原函数
                result = await func(*args, **kwargs)
                
                # 记录执行成功的日志
                await db_logger.log(
                    message=f"{log_message} - 成功",
                    level=level,
                    category=category,
                    source=source,
                    user_id=user_id,
                    task_id=task_id,
                    worker_id=worker_id
                )
                
                return result
            
            except Exception as e:
                # 记录异常
                await db_logger.exception(
                    exc=e,
                    message=f"{log_message} - 失败",
                    category=category,
                    user_id=user_id,
                    task_id=task_id,
                    worker_id=worker_id
                )
                # 重新抛出异常
                raise
        
        return wrapper
    
    return decorator 