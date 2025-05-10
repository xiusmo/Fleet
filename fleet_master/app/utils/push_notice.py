from shared.utils.http import AsyncHttpClient
from shared.utils.logger import DBLogger
from shared.models.log import LogCategory

async def push_to_bark(*, title, message, key, logger: DBLogger, http_client: AsyncHttpClient):
    url = f"https://api.day.app/{key}/{title}/{message}"
    try:
        response = await http_client.get(url)
        await logger.info(f"推送Bark通知: key={key}, 状态码={response.status_code}, 内容={title}/{message}", category=LogCategory.PUSH)
        if response.status_code == 200:
            return True
        else:
            await logger.error(f"推送Bark通知失败: 状态码={response.status_code}, 响应={response.text}", category=LogCategory.PUSH)
            return False
    except Exception as e:
        await logger.error(f"推送Bark通知异常: {str(e)}", category=LogCategory.PUSH)
        return False


async def push_to_ntfy(*, title, message, key, priority="info", logger: DBLogger, http_client: AsyncHttpClient):
    enum_priority = {
        "error": "urgent",
        "warning": "high",
        "info": "default",
        "debug": "low",
    }
    headers = {
        "Title": title.encode('utf-8'),
        "Priority": enum_priority[priority],
        "Tags": "tags",
        "Content-Type": "text/plain; charset=utf-8",
        # "Actions": "test",
        # "Icon": "https://ntfy.sh/icons/ntfy.png",
    }
    url = f"https://ntfy.sh/{key}"
    
    try:
        response = await http_client.post(url, data=message.encode('utf-8'), headers=headers)
        await logger.info(f"推送Ntfy通知: key={key}, 状态码={response.status_code}, 内容={title}/{message}", category=LogCategory.PUSH)
        if response.status_code == 200:
            return True
        else:
            await logger.error(f"推送Ntfy通知失败: 状态码={response.status_code}, 响应={response.text}", category=LogCategory.PUSH)
            return False
    except Exception as e:
        await logger.error(f"推送Ntfy通知异常: {str(e)}", category=LogCategory.PUSH)
        return False
