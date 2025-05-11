import os
from typing import Any, Dict, Optional, List

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings
import logging
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    API_PREFIX: str = "/api/v1"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DEBUG: bool = False
    CURRENT_NODE: str
    ALLOW_REGISTER: bool = False
    
    # 用于节点公钥自动注册的引导令牌
    BOOTSTRAP_TOKEN: str = ""
    
    # Turnstile设置
    TURNSTILE_SECRET_KEY: str = ""
    TURNSTILE_SITE_KEY: str = ""
    
    # CORS设置
    ALLOWED_ORIGINS: List[str] = []
    
    @field_validator("ALLOWED_ORIGINS", mode="before")
    def parse_allowed_origins(cls, v: Optional[str]) -> List[str]:
        if isinstance(v, list):
            return v
        if isinstance(v, str) and v:
            return [origin.strip() for origin in v.split(",")]
        # 开发环境下允许所有来源，生产环境必须明确配置
        return ["*"] if os.getenv("DEBUG", "False").lower() == "true" else []
    
    # 数据库设置
    DATABASE_URL: PostgresDsn
    
    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(cls, v: Optional[str]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres"),
            host=os.getenv("POSTGRES_SERVER", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            path=f"/{os.getenv('POSTGRES_DB', 'task_scheduler')}",
        )
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
logger.info(f"加载的配置文件路径: {os.path.abspath(__file__)}")
logger.info(f"数据库连接字符串: {settings.DATABASE_URL}")
logger.info(f"是否调试模式: {settings.DEBUG}")
logger.info(f"当前节点: {settings.CURRENT_NODE}")
logger.info(f"是否允许注册: {settings.ALLOW_REGISTER}")
logger.info(f"CORS允许的来源: {settings.ALLOWED_ORIGINS}")