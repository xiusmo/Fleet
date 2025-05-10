from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.security import create_fleet_jwt
from shared.db.session import get_db
from shared.models.user import User
from app.services.worker import find_available_worker
from shared.utils.http import AsyncHttpClient, get_http_client
from shared.core.config import settings

router = APIRouter()



@router.get("/status")
async def get_status(
    current_user: User = Depends(get_current_user)
):
    return current_user.monitor_status


@router.get("/{bool}")
async def ws_monitor(
    bool: bool,
    http: AsyncHttpClient = Depends(get_http_client),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    current_user.monitor_status = bool
    params = {
        "im_username": current_user.im_username,
        "im_password": current_user.im_password
    }
    await db.commit()
    if bool:
        worker = await find_available_worker(db)
        current_user.worker = worker
    else:
        worker = current_user.worker
    subdomain = worker.subdomain

    if settings.DEBUG:
        if bool and worker:
            url = f"http://localhost:8001/api/v1/fleet/ws/connect"
            response = await http.get(url, params=params, headers={"Authorization": f"Bearer {create_fleet_jwt(worker.name)}"})
            return response.text
        elif not bool and worker:
            url = f"http://localhost:8001/api/v1/fleet/ws/disconnect"
            response = await http.get(url, params=params, headers={"Authorization": f"Bearer {create_fleet_jwt(worker.name)}"})
            return response.text
        else:
            raise HTTPException(status_code=404, detail="worker not found")

    if bool and worker:
        url = f"https://{subdomain}.xiusmo.com/api/v1/fleet/ws/connect"
        response = await http.get(url, params=params, headers={"Authorization": f"Bearer {create_fleet_jwt(worker.name)}"})
        return response.text
    elif not bool and worker:
        url = f"https://{subdomain}.xiusmo.com/api/v1/fleet/ws/disconnect"
        response = await http.get(url, params=params, headers={"Authorization": f"Bearer {create_fleet_jwt(worker.name)}"})
        return response.text
    else:
        raise HTTPException(status_code=404, detail="Worker not found")
    

