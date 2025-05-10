from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from shared.db.session import get_db
from shared.models.sign_config import SignConfig
from app.utils.push_notice import push_to_bark, push_to_ntfy
from shared.utils.logger import DBLogger
from shared.utils.http import AsyncHttpClient
from shared.utils.logger import get_logger
from shared.utils.http import get_http_client
router = APIRouter()


@router.post("/push-notice")
async def push_notice(
    user_id: int,
    message: str,
    db: AsyncSession = Depends(get_db),
    http_client: AsyncHttpClient = Depends(get_http_client),
    logger: DBLogger = Depends(get_logger),
):
    db_config = await db.execute(
        select(SignConfig)
        .where(SignConfig.user_id == user_id)
        .where(
            or_(
                SignConfig.ios_bark_key.isnot(None),
                SignConfig.android_ntfy_key.isnot(None)
            )
        )
        .limit(1)
    )
    config = db_config.scalars().first()
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    
    result = {}
    if config.ios_bark_key:
        result["bark"] = await push_to_bark(
            title=config.name,
            message=message,
            key=config.ios_bark_key,
            logger=logger,
            http_client=http_client,
        )
    if config.android_ntfy_key:
        result["ntfy"] = await push_to_ntfy(
            title=config.name,
            message=message,
            key=config.android_ntfy_key,
            logger=logger,
            http_client=http_client,
    )
    if not result:
        raise HTTPException(status_code=400, detail="Push notice failed")
    return result