from datetime import datetime, timedelta, timezone
import logging
import sys

from app.core.security import create_fleet_jwt
from shared.db.session import async_session
from shared.models.log import Log, LogLevel, LogCategory
from shared.models.user import User
from shared.models.worker import Worker, WorkerStatus
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload
from shared.core.config import settings
from shared.utils.http import AsyncHttpClient
from shared.utils.logger import DBLogger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

async def clean_logs():
    async with async_session() as db:
        try:
            await db.execute(
                delete(Log)
                .where(Log.created_at < datetime.now(timezone.utc) - timedelta(days=30)))
            await db.commit()
            logger.info("日志清理完成")
        except Exception as e:
            logger.error(f"日志清理失败: {e}")

async def measure_ws_connections():
    """
    监控WebSocket连接，检查是否有连接异常中断，并尝试重新连接
    """
    try:
        # 创建HTTP客户端
        async with async_session() as db:
            db_logger = DBLogger(db)
            http_client = AsyncHttpClient()
            
            async with async_session() as db:
                # 获取所有活跃且需要监控的用户
                users_result = await db.execute(
                    select(User)
                    .where(User.is_active == True)
                    .where(User.monitor_status == True)
                    .options(selectinload(User.worker))
                )
                users = users_result.scalars().all()
                
                if not users:
                    return
                
                # 获取所有在线工作节点
                workers_result = await db.execute(
                    select(Worker)
                    .where(Worker.status == WorkerStatus.ONLINE)
                )
                workers = workers_result.scalars().all()
                
                if not workers:
                    return
                
                # 获取当前所有WebSocket连接
                all_connections = []
                
                if settings.DEBUG:
                    for worker in workers:
                        response = await http_client.get("http://localhost:8001/api/v1/fleet/ws/get-all-connections", headers={"Authorization": f"Bearer {create_fleet_jwt(worker.name)}"})
                        if response.status_code == 200:
                            all_connections = response.json()
                            await db_logger.log(
                                message=f"从本地开发服务器获取到{len(all_connections)}个WebSocket连接",
                                level=LogLevel.INFO,
                                category=LogCategory.SCHEDULER,
                                source="scheduler.jobs.measure_ws_connections"
                            )
                else:
                    for worker in workers:
                        worker_url = f"https://{worker.subdomain}.xiusmo.com/api/v1/fleet/ws/get-all-connections"
                        response = await http_client.get(worker_url, headers={"Authorization": f"Bearer {create_fleet_jwt(worker.name)}"})
                        if response.status_code == 200:
                            worker_connections = response.json()
                            all_connections.extend(worker_connections)
                            await db_logger.log(
                                message=f"从 {worker.subdomain} 获取到 {len(worker_connections)} 个WebSocket连接",
                                level=LogLevel.INFO,
                                category=LogCategory.SCHEDULER,
                                source="scheduler.jobs.measure_ws_connections"
                            )
                
                
                # 比较需要监控的用户和活跃连接
                missing_connections = []
                for user in users:
                    if user.im_username not in all_connections:
                        missing_connections.append(user)
                
                # 尝试重新建立丢失的连接
                for user in missing_connections:
                    if not user.worker:
                        continue
                        
                    await open_ws_monitor(
                        im_username=user.im_username, 
                        im_password=user.im_password, 
                        subdomain=user.worker.subdomain,
                        db_logger=db_logger
                    )
                
                await db_logger.log(
                    message=f"WebSocket连接检查完成，已尝试重新连接 {len(missing_connections)} 个断开的连接, 总连接数 {len(all_connections)}",
                    level=LogLevel.INFO,
                    category=LogCategory.SCHEDULER,
                    source="scheduler.jobs.measure_ws_connections"
                )
                logger.info(f"WebSocket连接监控任务执行完成{len(missing_connections)}个断开的连接, 总连接数 {len(all_connections)}")
            
    except Exception as e:
        await db_logger.log(
            message=f"执行WebSocket连接监控任务时出现未处理异常: {str(e)}",
            level=LogLevel.ERROR,
            category=LogCategory.SCHEDULER,
            details={"error": str(e)},
            source="scheduler.jobs.measure_ws_connections"
        )
        logger.error(f"执行WebSocket连接监控任务时出现未处理异常: {str(e)}")

async def open_ws_monitor(im_username: str, im_password: str, subdomain: str, db_logger: DBLogger):
    """
    为指定用户打开WebSocket监控连接
    """
    try:
        http_client = AsyncHttpClient()
        
        if settings.DEBUG:
            url = f"http://localhost:8001/api/v1/fleet/ws/connect"
        else:
            url = f"https://{subdomain}.xiusmo.com/api/v1/fleet/ws/connect"
            
        params = {"im_username": im_username, "im_password": im_password}
        
        response = await http_client.get(url, params=params, headers={"Authorization": f"Bearer {create_fleet_jwt(subdomain)}"})
        
        if response.status_code == 200:
            return True
        else:
            await db_logger.log(
                message=f"为用户 {im_username} 建立WebSocket连接失败: HTTP {response.status_code} - {response.text}",
                level=LogLevel.ERROR,
                category=LogCategory.SCHEDULER,
                details={"error": str(e)},
                source="scheduler.jobs.open_ws_monitor"
            )
            return False
            
    except Exception as e:
        await db_logger.log(
            message=f"为用户 {im_username} 打开WebSocket连接时出现异常: {str(e)}",
            level=LogLevel.ERROR,
            category=LogCategory.SCHEDULER,
            details={"error": str(e)},
            source="scheduler.jobs.open_ws_monitor"
        )
        return False