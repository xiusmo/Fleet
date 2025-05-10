from fastapi import APIRouter

from app.api.v1 import auth, fleet, workers, admin, logs, monitor, sign_configs, activity, test, announcement
from shared.core.config import settings

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(workers.router, prefix="/workers", tags=["工作节点"])
api_router.include_router(admin.router, prefix="/admin", tags=["管理"])
api_router.include_router(logs.router, prefix="/logs", tags=["日志"])
api_router.include_router(fleet.router, prefix="/abracadabra", tags=["集群"])
api_router.include_router(monitor.router, prefix="/monitor", tags=["监控"])
api_router.include_router(sign_configs.router, prefix="/sign-configs", tags=["签到配置"])
api_router.include_router(activity.router, prefix="/activity", tags=["活动"])
api_router.include_router(announcement.router, prefix="/announcement", tags=["公告"])
if settings.DEBUG:
    api_router.include_router(test.router, prefix="/test", tags=["测试"])