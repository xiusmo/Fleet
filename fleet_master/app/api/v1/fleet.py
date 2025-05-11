import asyncio
from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
import orjson
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from shared.db.session import get_db
from shared.models.sign_config import SignConfig
from shared.models.user import User
from shared.models.user_activity_detection import UserActivityDetection
from shared.models.worker import Worker, WorkerStatus
from shared.schemas.worker import WorkerCreate
from shared.schemas.sign_activity import Activity, SignActivityFromWS
from shared.models.sign_activity import SignActivity
from app.services.handle_sign_from_ws import check_activity_exist, handle_sign_from_ws
from shared.utils.http import AsyncHttpClient, get_http_client
from shared.utils.logger import DBLogger, get_logger, LogCategory
from shared.core.config import settings
from app.utils.load_keys import save_node_public_key

router = APIRouter()

# 注册节点公钥
class KeyRegister(BaseModel):
    name: str
    public_key: str

@router.post("/register-key")
async def register_key(
    payload: KeyRegister,
    request: Request,
):
    # 校验引导令牌
    token = request.headers.get("X-Bootstrap-Token")
    if not token or token != settings.BOOTSTRAP_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid bootstrap token")
    
    if not save_node_public_key(payload.name, payload.public_key):
        raise HTTPException(status_code=500, detail="Failed to save public key")
    
    return {"status": "ok", "message": f"节点 {payload.name} 的公钥已注册"}

# 节点心跳
@router.post("/ping/{name}")
async def ping_fleet(
    name: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Worker).where(Worker.name == name))
    fleet = result.scalars().first()
    if not fleet:
        raise HTTPException(status_code=404, detail="Fleet not found")
    fleet.last_heartbeat = datetime.now(timezone.utc)
    fleet.status = WorkerStatus.ONLINE
    await db.commit()
    
    # Simulate a ping operation
    return {"fleet_id": fleet.id, "status": "pong"}


# 注册工作节点
@router.post("/register")
async def register_worker(
    worker_in: WorkerCreate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Worker).where(Worker.name == worker_in.name))
    worker = result.scalars().first()
    if not worker:
        worker = Worker(**worker_in.model_dump())
        db.add(worker)
        await db.commit()
        return worker
    
    worker.status = WorkerStatus.ONLINE
    worker.subdomain = worker_in.subdomain
    worker.capabilities = worker_in.capabilities
    worker.description = worker_in.description
    worker.endpoint = worker_in.endpoint
    await db.commit()
    return worker


# 处理节点发来的活动
@router.post("/activity")
async def activity(
    sign_activity: SignActivityFromWS,
    db: AsyncSession = Depends(get_db),
    http_client: AsyncHttpClient = Depends(get_http_client),
    logger: DBLogger = Depends(get_logger),
):
    activity, user = await check_activity_exist(sign_activity, db, http_client)
    asyncio.create_task(handle_sign_from_ws(user, activity))
    
    # TODO creat task
    return True


class UpdateDetectionStatus(BaseModel):
    uuid: str
    status: str
    message: Optional[str] = None
    total_users: Optional[int] = None
    signed_users: Optional[int] = None
    sign_percent: Optional[float] = None

@router.post("/update-detection-status")
async def update_detection_status(
    update_detection_status: UpdateDetectionStatus,
    db: AsyncSession = Depends(get_db),
    logger: DBLogger = Depends(get_logger),
):
    result = await db.execute(
        select(UserActivityDetection)
        .where(UserActivityDetection.uuid == update_detection_status.uuid)
        .options(selectinload(UserActivityDetection.activity))
    )  
    detection = result.scalars().first()
    if not detection:
        logger.error(f"when update detection status, detection not found: {update_detection_status.uuid}")
        raise HTTPException(status_code=404, detail="Detection not found")
    
    detection.status = update_detection_status.status
    detection.message = update_detection_status.message
    if update_detection_status.total_users != None:
        detection.activity.total_users = update_detection_status.total_users
    if update_detection_status.signed_users != None:
        detection.activity.signed_users = update_detection_status.signed_users
    if update_detection_status.sign_percent != None:
        detection.activity.sign_percent = update_detection_status.sign_percent
    await db.commit()
    return detection


class UpdateAttendInfo(BaseModel):
    activity_id: str
    total_users: Optional[int] = None
    signed_users: Optional[int] = None
    sign_percent: Optional[float] = None

@router.post("/update-attend-info")
async def update_attend_info(
    update_attend_info: UpdateAttendInfo,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SignActivity)
        .where(SignActivity.activity_id == update_attend_info.activity_id)
    )
    activity = result.scalars().first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    if update_attend_info.total_users != None:
        activity.total_users = update_attend_info.total_users
    if update_attend_info.signed_users != None:
        activity.signed_users = update_attend_info.signed_users
    if update_attend_info.sign_percent != None:
        activity.sign_percent = update_attend_info.sign_percent
    activity.attend_update_at = datetime.now(timezone.utc)
    await db.commit()
    return activity

class ReportWsError(BaseModel):
    message: str
    im_uname: str

@router.post("/report_ws_error")
async def report_ws_error(
    report_ws_error: ReportWsError,
    db: AsyncSession = Depends(get_db),
    logger: DBLogger = Depends(get_logger),
):
    logger.error(
        message=report_ws_error.message,
        category=LogCategory.WORKER,
        details={
            "im_uname": report_ws_error.im_uname,
        }
    )
    user = await db.execute(
        select(User)
        .where(User.im_uname == report_ws_error.im_uname)
    )
    user = user.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.monitor_status = False
    await db.commit()
    return True
