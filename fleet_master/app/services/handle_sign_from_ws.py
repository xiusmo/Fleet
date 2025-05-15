from fastapi import HTTPException
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.core.security import create_fleet_jwt
from shared.models.user import User
from shared.models.sign_activity import SignActivity
from shared.models.sign_config import SignConfig
from shared.db.session import async_session

from shared.core.config import settings
from shared.models.user_activity_detection import UserActivityDetection
from shared.schemas.sign_activity import SignActivityFromWS
from app.services.sign_config import get_config_for_sign
from shared.utils.http import AsyncHttpClient

from shared.models.log import LogCategory, LogLevel
from shared.utils.logger import DBLogger, get_logger
from app.utils.push_notice import push_to_bark, push_to_ntfy
from shared.schemas.sign_activity import APIActivityResponse



async def check_activity_exist(sign_activity: SignActivityFromWS, db: AsyncSession, http_client: AsyncHttpClient):
    user = await db.execute(
        select(User)
        .where(User.im_username == sign_activity.detected_by)
        .options(selectinload(User.worker))
        .limit(1)
    )
    user = user.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    worker = user.worker
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    result = await db.execute(
        select(SignActivity)
        .where(SignActivity.activity_id == sign_activity.activity_id)
        .limit(1)
    )
    activity = result.scalars().first()
    if not activity:
        sign_activity.cookies = user.cookies
        if settings.DEBUG:
            result = await http_client.post(
                "http://localhost:8001/api/v1/fleet/activity",
                json=sign_activity.model_dump(by_alias=False),
                headers={"Authorization": f"Bearer {create_fleet_jwt(worker.name)}"}
            )
        else:
            result = await http_client.post(
                f"https://{worker.subdomain}.xiusmo.com/api/v1/fleet/activity",
                json=sign_activity.model_dump(by_alias=False),
                headers={"Authorization": f"Bearer {create_fleet_jwt(worker.name)}"}
            )
        if result.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to create activity")
        response_data = result.json()
        # 使用专门的 Pydantic 模型解析 API 返回值
        api_response = APIActivityResponse.model_validate(response_data)
        
        # 将 API 响应转换为 SignActivity 模型需要的字典
        activity_dict = api_response.to_sign_activity(
            course_id=sign_activity.course_id,
            class_id=sign_activity.class_id,
            course_name=sign_activity.course_name,
            teacher_name=sign_activity.teacher_name
        )
        
        # 创建 SignActivity 并存入数据库
        activity = SignActivity(**activity_dict)
        db.add(activity)
        await db.commit()
    
    return activity, user
    
        
        
        
async def handle_sign_from_ws(user: User, activity: SignActivity):
    async with async_session() as db:
        logger = DBLogger(db)
        http_client = AsyncHttpClient(logger=logger)
        config = await get_config_for_sign(db, user, activity.class_id)
        await _push_notice_when_detect(user=user, activity=activity, config=config, logger=logger, http_client=http_client)
        user_activity_detection = UserActivityDetection.from_activity(activity, user)
        if activity.other_id == 2:
            user_activity_detection.status = "enc"
            db.add(user_activity_detection)
            await db.commit()
            return
        db.add(user_activity_detection)
        await db.commit()
        if config.trigger_type == "immediate":
            await handle_immediate_sign(user=user, activity=activity, detection=user_activity_detection, db=db, http_client=http_client, logger=logger)
        elif config.trigger_type == "threshold":
            user_activity_detection.status = "polling"
            await db.commit()
            await handle_threshold_sign(user=user, activity=activity, config=config, detection=user_activity_detection, db=db, http_client=http_client, logger=logger)
            # await handle_manual_sign(detection=user_activity_detection, db=db)
        elif config.trigger_type == "manual":
            await handle_manual_sign(detection=user_activity_detection, db=db)
    


async def handle_immediate_sign(*, user: User, activity: SignActivity, enc: Optional[str] = None, detection: UserActivityDetection, db: AsyncSession, http_client: AsyncHttpClient, logger: DBLogger):
    config = await get_config_for_sign(db, user, activity.class_id)
    if activity.other_id == 2:
        if not enc:
            return
    if settings.DEBUG:
        result = await http_client.post(f"http://localhost:8001/api/v1/fleet/signin", json={**activity.model_dump(by_alias=False), "cookies": user.cookies, "enc": enc, "random_photo": config.use_random_photo}, headers={"Authorization": f"Bearer {create_fleet_jwt(user.worker.name)}"})
    else:
        result = await http_client.post(f"https://{user.worker.subdomain}.xiusmo.com/api/v1/fleet/signin", json={**activity.model_dump(by_alias=False), "cookies": user.cookies, "enc": enc, "random_photo": config.use_random_photo}, headers={"Authorization": f"Bearer {create_fleet_jwt(user.worker.name)}"})
    if result.status_code != 200:
        await logger.error(
            message="Failed to sign activity",
            category=LogCategory.TASK,
            user_id=user.id,
            worker_id=user.worker.id,
            task_id=activity.activity_id,
            details={"user_name": user.person_name or user.username, "activity_type": activity.other_id},
            source="app.services.handle_sign_from_ws.handle_immediate_sign"
        )
        raise HTTPException(status_code=400, detail="Failed to sign")
    await logger.info(
        message="Sign activity succeeded",
        category=LogCategory.TASK,
        user_id=user.id,
        worker_id=user.worker.id,
        task_id=activity.activity_id,
        details={"user_name": user.person_name or user.username, "activity_type": activity.other_id},
        source="app.services.handle_sign_from_ws.handle_immediate_sign"
    )
    
    response_data = result.json()
    await _push_notice_when_sign(user=user, activity=activity, config=config, response_data=response_data, logger=logger, http_client=http_client)
    if response_data.get("result") == True:
        detection.status = "success"
        detection.message = f"签到成功: {response_data.get('message')}"
        await db.commit()
        return response_data
    elif response_data.get("result") == False:
        message = {
            "result": False,
            "message": f"{response_data.get('message')} {response_data.get('response_data')}",
        }
        detection.status = "failed"
        detection.message = json.dumps(message, ensure_ascii=False)
        await logger.error(
            message="Failed to sign activity with response",
            category=LogCategory.TASK,
            user_id=user.id,
            worker_id=user.worker.id,
            task_id=activity.activity_id,
            details={
                "user_name": user.person_name or user.username,
                "activity_type": activity.other_id,
                "error": message
            },
            source="app.services.handle_sign_from_ws.handle_immediate_sign"
        )
        await db.commit()
        return message
    else:
        detection.status = "failed"
        detection.message = "未知错误, 日志已记录"
        await logger.error(
            message="Failed to sign activity with unexpected response",
            category=LogCategory.TASK,
            user_id=user.id,
            worker_id=user.worker.id,
            task_id=activity.activity_id,
            details={
                "user_name": user.person_name or user.username,
                "activity_type": activity.other_id,
                "response_data": response_data
            },
            source="app.services.handle_sign_from_ws.handle_immediate_sign"
        )
        await db.commit()
        raise HTTPException(status_code=400, detail="Failed to sign, unknown error")

async def handle_threshold_sign(*, user: User, activity: SignActivity, config: SignConfig, detection: UserActivityDetection, db: AsyncSession, http_client: AsyncHttpClient, logger: DBLogger):
    worker = user.worker
    if settings.DEBUG:
        result = await http_client.post(f"http://localhost:8001/api/v1/fleet/threshold",raise_for_status=False, json={
            **activity.model_dump(by_alias=False), 
            "cookies": user.cookies, 
            "uuid": detection.uuid, 
            "threshold_time": config.threshold_time,
            "poll_interval": config.poll_interval,
            "threshold_count": config.threshold_count,
            "threshold_percent": config.threshold_percent,
            "random_photo": config.use_random_photo,
        }, headers={"Authorization": f"Bearer {create_fleet_jwt(worker.name)}"})
    else:
        result = await http_client.post(f"https://{worker.subdomain}.xiusmo.com/api/v1/fleet/threshold", json={
            **activity.model_dump(by_alias=False), 
            "cookies": user.cookies, 
            "uuid": detection.uuid, 
            "threshold_time": config.threshold_time,
            "poll_interval": config.poll_interval,
            "threshold_count": config.threshold_count,
            "threshold_percent": config.threshold_percent,
            "random_photo": config.use_random_photo,
        }, headers={"Authorization": f"Bearer {create_fleet_jwt(worker.name)}"})
    if result.status_code != 200:
        await logger.error(
            message="Failed to sign activity",
            category=LogCategory.TASK,
            user_id=user.id,
            worker_id=worker.id if worker else None,
            task_id=activity.activity_id,
            details={"user_name": user.person_name or user.username, "activity_type": activity.other_id},
            source="app.services.handle_sign_from_ws.handle_threshold_sign"
        )
        raise HTTPException(status_code=400, detail="Failed to sign")
    await logger.info(
        message="Threshold sign activity succeeded",
        category=LogCategory.TASK,
        user_id=user.id,
        worker_id=worker.id if worker else None,
        task_id=activity.activity_id,
        details={"user_name": user.person_name or user.username, "activity_type": activity.other_id},
        source="app.services.handle_sign_from_ws.handle_threshold_sign"
    )

async def handle_manual_sign(detection: UserActivityDetection, db: AsyncSession):
    detection.status = "waiting"
    await db.commit()


async def _push_notice_when_detect(*, user: User, activity: SignActivity, config: SignConfig, logger: DBLogger, http_client: AsyncHttpClient):
    if not config.notify_on_detect:
        return
    message = f"{activity.course_name} 课程的 {activity.title} {activity.sign_type}签到: {activity.title}"
    if config.ios_bark_key:
        await push_to_bark(title=f"签到检测", message=message, key=config.ios_bark_key, logger=logger, http_client=http_client)
    if config.android_ntfy_key:
        await push_to_ntfy(title=f"签到检测", message=message, key=config.android_ntfy_key, logger=logger, http_client=http_client)
        

async def _push_notice_when_sign(*, user: User, activity: SignActivity, config: SignConfig, response_data: dict, logger: DBLogger, http_client: AsyncHttpClient):
    if not config.notify_on_sign:
        return
    if response_data.get("result"):
        title = "签到成功"
    else:
        title = "签到失败"
    message = f"{activity.course_name} 课程的 {activity.title} {activity.sign_type}签到: {activity.title}"
    if config.ios_bark_key:
        await push_to_bark(title=title, message=message, key=config.ios_bark_key, logger=logger, http_client=http_client)
    if config.android_ntfy_key:
        await push_to_ntfy(title=title, message=message, key=config.android_ntfy_key, logger=logger, http_client=http_client)
