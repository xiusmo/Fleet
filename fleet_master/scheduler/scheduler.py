import sys
import os
import logging

# 将项目根目录添加到Python路径中
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 配置标准日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
std_logger = logging.getLogger("scheduler")

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import asyncio
from shared.db.session import async_session
from jobs.jobs import clean_logs, measure_ws_connections



# 记录调度器启动
std_logger.info("调度器模块初始化")



async def main():
    """主函数"""
    std_logger.info("调度器主程序启动")
    
    # 创建并配置调度器
    scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")
    
    # 每天凌晨 2:00 清理日志（或按需时间）
    scheduler.add_job(
        clean_logs,
        trigger=CronTrigger(hour=2, minute=0),  # 可改为 hour=0 表示午夜
        id="log_cleaner"
    )

    # 每 30 分钟执行一次 WebSocket 检测
    scheduler.add_job(
        measure_ws_connections,
        trigger=IntervalTrigger(minutes=10),
        id="measure_ws_connections"
    )
    
    # 启动调度器
    scheduler.start()
    std_logger.info("调度器已启动")
    
    try:
        # 保持主线程运行
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        std_logger.info("接收到终止信号，正在关闭调度器...")
        scheduler.shutdown()
        std_logger.info("调度器已关闭")


if __name__ == "__main__":
    std_logger.info("调度器程序开始执行")
    try:
        asyncio.run(main())
    except Exception as e:
        std_logger.critical(f"调度器主程序异常终止: {str(e)}", exc_info=True)
    

