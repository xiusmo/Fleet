from datetime import datetime, timezone
from typing import Optional

from sqlmodel import SQLModel

# 保留空的基类，避免导入错误
class TimestampModel(SQLModel):
    """
    该类已不再使用，所有模型都直接包含自己的时间戳字段，
    此处仅为向后兼容保留。
    
    请不要在新模型中继承此类，而是直接在模型中添加 created_at 和 updated_at 字段。
    """
    pass

