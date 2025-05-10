import asyncio
import logging
import signal
import sys
import time
from typing import Callable

from fastapi import FastAPI
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine

from shared.core.config import settings
from shared.db.session import engine

logger = logging.getLogger(__name__)


async def create_database_tables():
    """
    创建所有数据库表
    """
    try:
        from sqlalchemy.schema import CreateSchema
        from sqlmodel import SQLModel
        
        # 导入所有模型以确保它们都被注册
        # 通过导入shared.models下的所有模型类确保所有表都被创建
        from shared.models import (
            User, 
            Worker, WorkerStatus,
            Log, LogLevel, LogCategory,
            SignActivity,
            SignConfig,
            UserActivityDetection,
            Announcement, AnnouncementStatus
        )
        
        # 创建表
        async with engine.begin() as conn:
            # 仅在SQLModel 0.0.8版本中需要
            # 在较新版本中可以直接使用 await conn.run_sync(SQLModel.metadata.create_all)
            await conn.run_sync(SQLModel.metadata.create_all)
        
        logger.info("数据库表创建完成")
    except SQLAlchemyError as e:
        logger.error(f"创建数据库表时出错: {e}")
        raise
    except ImportError as e:
        logger.error(f"导入模型时出错: {e}")
        raise


async def create_initial_data():
    """
    创建初始数据
    """
    try:
        from app.services.auth import create_user
        from shared.schemas.user import UserCreate
        from shared.db.session import async_session
        from sqlalchemy.future import select
        from shared.models.user import User
        
        # 在生产环境中可以通过配置控制是否创建初始数据
        if settings.ALLOW_REGISTER or settings.DEBUG:
            async with async_session() as db:
                result = await db.execute(select(User).where(User.username == "admin"))
                admin = result.scalars().first()
                
                if not admin:
                    admin_user = UserCreate(
                        username="***REMOVED***",
                        tel="***REMOVED***",
                        password="***REMOVED***",
                        is_active=True,
                        is_admin=True,
                    )
                    await create_user(db, admin_user)
                    logger.info("管理员用户创建完成")
    except Exception as e:
        logger.error(f"创建初始数据时出错: {e}")
        # 非关键错误，不需要抛出异常中断启动




async def startup_event():
    """
    应用启动时的事件处理
    """
    start_time = time.time()
    logger.info(f"开始启动应用，环境: {'开发' if settings.DEBUG else '生产'}")
    
    try:
        # 创建数据库表
        await create_database_tables()
        
        # 创建初始数据
        await create_initial_data()
        
        
        
        elapsed = time.time() - start_time
        logger.info(f"应用启动完成，耗时 {elapsed:.2f} 秒")
    except Exception as e:
        logger.critical(f"应用启动失败: {e}")
        raise


async def shutdown_event():
    """
    应用关闭时的事件处理
    """
    logger.info("应用关闭中...")
    await asyncio.sleep(1)
    logger.info("应用已关闭")