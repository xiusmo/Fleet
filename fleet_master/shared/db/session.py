from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from shared.core.config import settings

# 数据库连接池配置
pool_settings = {
    # 连接池大小（默认保持的连接数）
    "pool_size": 25,
    
    # 最大溢出连接数（在pool_size之外允许创建的最大连接数）
    "max_overflow": 10,
    
    # 连接回收时间（秒）- 超过此时间的连接将被回收重建
    "pool_recycle": 3600,  # 1小时
    
    # 连接超时时间（秒）- 从池中获取连接的最大等待时间
    "pool_timeout": 30,
    
    # 连接预检 - 在使用连接前检查其有效性，可防止使用失效连接
    "pool_pre_ping": True,
    
    # 是否在日志中输出SQL语句，调试时设为True
    "echo": settings.DEBUG
}

# 创建异步数据库引擎
engine = create_async_engine(
    str(settings.DATABASE_URL),
    **pool_settings
)

# 创建会话工厂
async_session = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,  # 查询结果在提交后不会过期
    autoflush=False          # 不自动刷新更改
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """依赖项，用于获取数据库会话"""
    async with async_session() as session:
        try:
            yield session
        finally:
            # 确保会话被正确关闭，即使发生异常
            await session.close()


# 为了方便监控连接池状态，提供获取连接池信息的函数
def get_pool_status():
    """获取当前连接池状态信息"""
    if hasattr(engine.pool, "checkedin") and hasattr(engine.pool, "checkedout"):
        return {
            "checkedin": engine.pool.checkedin(),       # 空闲连接数
            "checkedout": engine.pool.checkedout(),     # 正在使用的连接数 
            "size": engine.pool.size(),                 # 总连接池大小
            "overflow": engine.pool.overflow(),         # 溢出连接数量
            "timeout": engine.pool.timeout(),           # 连接超时时间
        }
    return {"error": "连接池状态无法获取"}
