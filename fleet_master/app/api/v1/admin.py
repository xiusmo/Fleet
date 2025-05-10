from typing import List, Dict, Any
import datetime
import psutil
from datetime import timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.deps import get_current_active_admin
from shared.db.session import get_db, engine
from shared.models.user import User
from shared.schemas.user import UserResponse, UserUpdate, UserDetail, UserResponseForAdmin
from app.core.security import get_password_hash

import time
import traceback
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()


@router.get("/users", response_model=List[UserResponseForAdmin])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    获取所有用户（管理员）
    """
    result = await db.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()
    return users


@router.get("/users/{user_id}", response_model=UserDetail)
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    获取指定用户详情（管理员）
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    删除用户（管理员）
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    await db.delete(user)
    await db.commit()



@router.get("/system/status", response_model=Dict[str, Any])
async def get_server_status(
    current_user: User = Depends(get_current_active_admin)
):
    """
    获取服务器系统状态信息（管理员）
    
    返回包括CPU使用率、内存使用、磁盘使用、网络IO等系统信息
    """
    # 转换数据结构为可序列化格式
    def convert_to_serializable(obj):
        if isinstance(obj, dict):
            return {k: convert_to_serializable(v) for k, v in obj.items()}
        elif hasattr(obj, "_asdict"):
            return {k: convert_to_serializable(v) for k, v in obj._asdict().items()}
        elif isinstance(obj, (list, tuple)):
            return [convert_to_serializable(i) for i in obj]
        elif isinstance(obj, bytes):
            return str(obj)
        return obj
    
    # 收集系统信息
    system_info = {
        "cpu_percent": psutil.cpu_percent(interval=0.5),
        "cpu_count": psutil.cpu_count(logical=True),
        "cpu_physical_count": psutil.cpu_count(logical=False),
        "load_avg": psutil.getloadavg(),
        "memory": psutil.virtual_memory()._asdict(),
        "swap": psutil.swap_memory()._asdict(),
        "disk": {part.mountpoint: psutil.disk_usage(part.mountpoint)._asdict() 
                for part in psutil.disk_partitions() if not part.mountpoint.startswith('/Volumes/')},
        "boot_time": datetime.datetime.fromtimestamp(psutil.boot_time()).isoformat(),
        "process_count": len(psutil.pids()),
        "uptime_seconds": int(datetime.datetime.now(timezone.utc).timestamp() - psutil.boot_time())
    }
    
    # 收集网络信息，并处理bytes类型
    net_io = psutil.net_io_counters(pernic=True)
    system_info["net_io"] = {}
    for nic, data in net_io.items():
        if not nic.startswith('utun') and not nic.startswith('llw'):  # 过滤掉不需要的网络接口
            system_info["net_io"][nic] = data._asdict()
    
    # 确保所有数据可序列化
    return convert_to_serializable(system_info)


@router.get("/system/processes", response_model=List[Dict[str, Any]])
async def get_server_processes(
    limit: int = 20,
    sort_by: str = "memory_percent",  # memory_percent, cpu_percent
    current_user: User = Depends(get_current_active_admin)
):
    """
    获取服务器进程列表（管理员）
    
    返回系统中占用资源最多的进程列表
    """
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_percent', 'cpu_percent', 'create_time', 'status']):
        try:
            # 获取进程信息
            proc_info = proc.info
            proc_info['create_time'] = datetime.datetime.fromtimestamp(proc_info['create_time']).isoformat() if proc_info['create_time'] else None
            processes.append(proc_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    # 按指定字段排序并限制返回数量
    if sort_by in ['memory_percent', 'cpu_percent']:
        # 确保排序键返回的值始终是数值，将None替换为0
        processes.sort(key=lambda x: 0 if x.get(sort_by) is None else float(x.get(sort_by, 0)), reverse=True)
    
    return processes[:limit]



@router.get("/database/health", response_model=Dict[str, Any])
async def check_database_health(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    检查数据库健康状态（管理员）
    
    返回数据库连接状态、响应时间、表信息等
    """
    health_info = {
        "status": "healthy",
        "timestamp": datetime.datetime.now(timezone.utc).isoformat(),
        "details": {},
        "tables": [],
        "table_stats": {},
        "connection": {
            "dialect": str(engine.dialect.name),
            "driver": str(engine.dialect.driver),
            "pool_size": engine.pool.size(),
            "pool_timeout": engine.pool.timeout(),
            "max_overflow": getattr(engine.pool, "max_overflow", None),
        }
    }
    
    try:
        # 测试连接和查询性能
        start_time = time.time()
        await db.execute(text("SELECT 1"))
        query_time = time.time() - start_time
        health_info["details"]["connection_test"] = {
            "success": True,
            "response_time_ms": round(query_time * 1000, 2)
        }
        
        # 获取数据库大小信息（仅适用于PostgreSQL）
        try:
            result = await db.execute(text("""
                SELECT pg_database_size(current_database()) as db_size,
                       pg_size_pretty(pg_database_size(current_database())) as db_size_pretty
            """))
            db_size_info = result.mappings().first()
            health_info["details"]["database_size"] = {
                "bytes": db_size_info["db_size"],
                "formatted": db_size_info["db_size_pretty"]
            }
        except Exception as e:
            health_info["details"]["database_size"] = {
                "error": str(e)
            }
        
        # 检查连接池状态
        health_info["details"]["connection_pool"] = {
            "checked_out": engine.pool.checkedout(),
            "overflow": engine.pool.overflow(),
            "checkedin": engine.pool.checkedin()
        }
        
        # 获取表信息
        try:
            # 正确的异步方式获取表名列表
            async with engine.begin() as conn:
                table_names = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())
            health_info["tables"] = table_names
            
            # 获取各表的行数和大小（对于PostgreSQL）
            for table_name in table_names:
                try:
                    # 获取表行数
                    result = await db.execute(text(f"SELECT COUNT(*) as row_count FROM {table_name}"))
                    row_count = result.scalar()
                    
                    # 获取表大小
                    result = await db.execute(text(f"""
                        SELECT pg_relation_size('{table_name}') as table_size_bytes,
                               pg_size_pretty(pg_relation_size('{table_name}')) as table_size
                    """))
                    size_info = result.mappings().first()
                    
                    health_info["table_stats"][table_name] = {
                        "row_count": row_count,
                        "size_bytes": size_info["table_size_bytes"],
                        "size_formatted": size_info["table_size"]
                    }
                except Exception as e:
                    health_info["table_stats"][table_name] = {
                        "error": str(e)
                    }
        except Exception as e:
            health_info["tables_error"] = {
                "message": str(e),
                "type": e.__class__.__name__
            }
        
        # 检查数据库版本
        result = await db.execute(text("SELECT version()"))
        version_info = result.scalar()
        health_info["details"]["database_version"] = version_info
        
    except SQLAlchemyError as e:
        health_info["status"] = "unhealthy"
        health_info["error"] = {
            "type": e.__class__.__name__,
            "message": str(e),
            "traceback": traceback.format_exc()
        }
    except Exception as e:
        health_info["status"] = "error"
        health_info["error"] = {
            "type": e.__class__.__name__,
            "message": str(e),
            "traceback": traceback.format_exc()
        }
    
    return health_info


@router.get("/database/slow-queries", response_model=List[Dict[str, Any]])
async def get_slow_queries(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    获取慢查询信息（管理员）
    
    返回数据库中执行时间最长的查询
    注意：此功能需要PostgreSQL已开启pg_stat_statements扩展
    """
    try:
        # 检查pg_stat_statements扩展是否可用
        result = await db.execute(text("""
            SELECT COUNT(*) FROM pg_extension WHERE extname = 'pg_stat_statements'
        """))
        extension_exists = result.scalar()
        
        if not extension_exists:
            # 返回列表中包含一个错误信息字典，而不是直接返回字典
            return [{
                "error": "pg_stat_statements扩展未启用",
                "instructions": "请在PostgreSQL中执行: CREATE EXTENSION pg_stat_statements;"
            }]
        
        # 尝试获取慢查询
        try:
            result = await db.execute(text("""
                SELECT 
                    substring(query, 1, 200) as query_text,
                    round(total_exec_time::numeric, 2) as total_time_ms,
                    round(mean_exec_time::numeric, 2) as avg_time_ms,
                    calls as execution_count,
                    round((100 * total_exec_time / sum(total_exec_time) OVER ())::numeric, 2) as time_percent
                FROM pg_stat_statements
                ORDER BY total_exec_time DESC
                LIMIT :limit
            """), {"limit": limit})
            
            slow_queries = [dict(row) for row in result.mappings().all()]
            return slow_queries
            
        except Exception as e:
            error_message = str(e)
            if "must be loaded via shared_preload_libraries" in error_message:
                return [{
                    "error": "pg_stat_statements模块未在PostgreSQL配置中正确加载",
                    "message": "虽然pg_stat_statements扩展已安装，但未在PostgreSQL配置中正确加载",
                    "solution": [
                        "1. 编辑PostgreSQL配置文件(postgresql.conf)",
                        "2. 添加或修改: shared_preload_libraries = 'pg_stat_statements'",
                        "3. 重启PostgreSQL服务",
                        "4. 执行: CREATE EXTENSION IF NOT EXISTS pg_stat_statements;"
                    ],
                    "details": error_message
                }]
            else:
                raise  # 重新抛出其他类型的错误
    
    except Exception as e:
        # 错误情况下也返回列表
        return [{
            "error": str(e),
            "traceback": traceback.format_exc()
        }]

