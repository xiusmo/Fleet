import asyncio
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from shared.db.session import get_db, async_session
from shared.models.user_activity_detection import UserActivityDetection
from app.services.handle_sign_from_ws import handle_immediate_sign
from shared.utils.http import AsyncHttpClient, get_http_client
from shared.utils.logger import DBLogger, get_logger
from shared.models.user import User
from app.api.deps import get_current_user
from shared.schemas.sign_activity import UserActivityDetectionResponse
from typing import List, Dict, Any
import copy

router = APIRouter()

@router.get("/active-activities", response_model=List[UserActivityDetectionResponse])
async def get_activities(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    detections = await db.execute(
        select(UserActivityDetection)
        .where(UserActivityDetection.user_id == current_user.id)
        .options(selectinload(UserActivityDetection.activity))
        .order_by(UserActivityDetection.detected_at.desc())
        .limit(50)
    )
    detections = detections.scalars().all()
    results = []
    for detection in detections:
        results.append(UserActivityDetectionResponse.model_validate(detection, from_attributes=True))
    return results

class qrcode_data(BaseModel):
    activity_id: str
    enc: str

@router.post("/qr-code")
async def qrcode_signin(
    data: qrcode_data,
    db: AsyncSession = Depends(get_db),
):
    # 步骤1: 先获取所有需要签到的用户检测记录
    detections_query = await db.execute(
        select(UserActivityDetection)
        .where(UserActivityDetection.activity_id == data.activity_id)
        .options(selectinload(UserActivityDetection.activity))
        .options(selectinload(UserActivityDetection.user).selectinload(User.worker))
    )
    detections = detections_query.scalars().all()
    
    if not detections:
        raise HTTPException(status_code=400, detail="没有需要签到的记录")
    # TODO: 优化已签到返回，错误返回，前端渲染字段更新，优化实现逻辑
    # 步骤2: 创建签到函数，确保每个签到任务使用独立的数据库会话和HTTP客户端
    async def sign_for_detection(detection) -> Dict[str, Any]:
        async with async_session() as session:
            try:
                task_http_client = AsyncHttpClient()
                task_logger = DBLogger(session)
                
                # 从数据库获取最新的用户和活动数据，避免使用过期数据
                user_query = await session.execute(
                    select(User)
                    .where(User.id == detection.user_id)
                    .options(selectinload(User.worker))
                )
                user = user_query.scalars().first()
                
                activity_query = await session.execute(
                    select(UserActivityDetection)
                    .where(UserActivityDetection.id == detection.id)
                    .options(selectinload(UserActivityDetection.activity))
                )
                fresh_detection = activity_query.scalars().first()
                
                if not fresh_detection:
                    return {
                        user.person_name: {
                            "status": "failed",
                            "message": "未开启监控"
                        }
                    }
                if fresh_detection.status == "success":
                    return {
                        user.person_name: {
                            "status": "success",
                            "message": "签到成功"
                        }
                    }
                
                # 执行签到
                result = await handle_immediate_sign(
                    user=user,
                    activity=fresh_detection.activity,
                    enc=data.enc,
                    detection=fresh_detection,
                    db=session,
                    http_client=task_http_client,
                    logger=task_logger
                )
                
                # 成功时返回用户相关信息
                if isinstance(result, dict) and result.get("result") == True:
                    return {
                        user.person_name: {
                            "status": "success",
                            "message": "签到成功"
                        }
                    }
                
                # 返回结果，包含错误信息（如果有）
                return {
                    user.person_name: {
                        "status": "failed",
                        "message": result.get('message', '未知错误')
                    }
                }
                
            except Exception as e:
                # 捕获并记录所有异常，确保一个任务的失败不会影响其他任务
                return {
                    user.person_name: {
                        "status": "failed",
                        "message": str(e)
                    }
                }
    
    # 步骤3: 并发执行所有签到任务
    tasks = [sign_for_detection(detection) for detection in detections]
    results = await asyncio.gather(*tasks)
    
    return results

@router.get("/{uuid}")
async def get_activity(
    uuid: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    detections = await db.execute(
        select(UserActivityDetection)
        .where(UserActivityDetection.uuid == uuid)
        .options(selectinload(UserActivityDetection.activity))
        .limit(1)
    )
    detections = detections.scalars().first()
    if not detections:
        raise HTTPException(status_code=404, detail="User activity detection not found")
    return UserActivityDetectionResponse.model_validate(detections, from_attributes=True)

# 处理用户的手动触发签到
@router.post("/{uuid}")
async def trigger_signin(
    uuid: str,
    db: AsyncSession = Depends(get_db), 
    http_client: AsyncHttpClient = Depends(get_http_client),
    logger: DBLogger = Depends(get_logger),
    current_user: User = Depends(get_current_user),
):
    user_activity_detection = await db.execute(
        select(UserActivityDetection)
        .where(UserActivityDetection.uuid == uuid)
        .limit(1)
        .options(selectinload(UserActivityDetection.activity))
        .options(selectinload(UserActivityDetection.user).selectinload(User.worker))
    )
    user_activity_detection = user_activity_detection.scalars().first()
    if not user_activity_detection:
        raise HTTPException(status_code=404, detail="User activity detection not found")
    if user_activity_detection.user.id != current_user.id:
        raise HTTPException(status_code=403, detail="No permission")
    # TODO: 检查是否已经签到及其他
    
    return await handle_immediate_sign(user=user_activity_detection.user, activity=user_activity_detection.activity,detection=user_activity_detection, db=db, http_client=http_client, logger=logger)







