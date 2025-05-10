from sqlalchemy import select
from fastapi import HTTPException, status
from app.core.security import create_fleet_jwt
from shared.models.worker import Worker
from shared.schemas.user import UserCreate, UserUpdate
from app.services.auth import generate_token, get_user_by_uid, create_user, update_cookies_by_uid, update_im_cookies_by_uid, update_person_info_by_uid
from shared.utils.http import AsyncHttpClient
from shared.db.session import async_session
from sqlalchemy.ext.asyncio import AsyncSession
import json
from shared.core.config import settings
async def login_by_cx(db: AsyncSession, http: AsyncHttpClient, tel: str, password: str) -> str:
    def raise_auth_error(msg: str = "未知错误"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg,
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 1. 登录超星
    async with async_session() as db:
        # 执行查询并获取结果
        result = await db.execute(select(Worker))
        worker = result.scalars().first()
        if not worker:
            raise_auth_error("Worker not found")
    
    if settings.DEBUG:
        url = "http://passport2.chaoxing.com/fanyalogin"
    else:
        url = f"https://{worker.subdomain}.xiusmo.com/api/v1/fleet/cx-login"
    response = await http.get(
        url,
        params={"tel": tel, "password": password}, 
        headers={"Authorization": f"Bearer {create_fleet_jwt(worker.name)}"}
    )
    if response.status_code != 200:
        raise_auth_error(response.text)

    token_dict, im_response_json = response.json()

    # 3. 获取/创建用户
    user = await get_user_by_uid(db, token_dict.get("_uid"))
    if not user:
        if not settings.ALLOW_REGISTER:
            raise_auth_error("Sorry, we closed the registration temporarily.")
        user_in = UserCreate(username=token_dict.get("_uid"), password=password, tel=tel)
        user = await create_user(db, user_in)

    if not user.is_active:
        raise_auth_error("Sorry, your account is not active. Please contact the administrator.")
    
    user = await update_cookies_by_uid(db, user.username, token_dict)

    # 4. 获取 IM 信息 TODO: 有些账号没有im信息，前端要做个提示

    if im_response_json.get("result") != 1:
        raise_auth_error(im_response_json.get("errorMsg", "IM登录失败"))

    # 5. 保存 IM 账号信息
    account_info = im_response_json.get("msg", {}).get("accountInfo", {}).get("imAccount", {})
    im_username = account_info.get("username", "")
    im_password = account_info.get("password", "")
    person_name = im_response_json.get("msg", {}).get("name", "")
    school_name = im_response_json.get("msg", {}).get("schoolname", "")
    fid = im_response_json.get("msg", {}).get("fid", "")
    
    if (not im_username or not im_password or not person_name or not school_name or not fid) and not settings.DEBUG:
        raise_auth_error("暂不支持未绑定单位/学校的用户登录")

    user = await update_im_cookies_by_uid(db, user.username, UserUpdate(im_username=im_username, im_password=im_password))
    user = await update_person_info_by_uid(db, user.username, UserUpdate(person_name=person_name, school_name=school_name, fid=fid))
    
    # 6. 生成 Access Token
    access_token = await generate_token(user)
    return access_token