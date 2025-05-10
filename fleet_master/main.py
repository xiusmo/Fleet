import asyncio
from contextlib import asynccontextmanager
import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from shared.core.config import settings
from app.core.events import startup_event, shutdown_event
from app.middleware.fleet_jwt_auth import JWTAuthMiddleware

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def create_application() -> FastAPI:
    """构建并返回 FastAPI 实例。"""
    app = FastAPI(
        title="分布式任务调度系统",
        description="一个用于分布式任务调度的 API 服务",
        version="0.1.0",
        debug=settings.DEBUG,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )

    # ---------------- CORS ----------------
    if settings.DEBUG:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    else:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.ALLOWED_ORIGINS,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["Authorization", "Content-Type"],
        )

    # ---------------- 业务中间件 & 路由 ----------------
    app.add_middleware(JWTAuthMiddleware)
    app.include_router(api_router, prefix=settings.API_PREFIX)


    return app

@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_event()
    yield
    await shutdown_event()

# 供 gunicorn 调用的顶级变量
app = create_application()

# ------------------------------------------- 业务端点 -------------------------------------------
@app.get("/")
async def root():
    return {"msg": "welcome", "worker_pid": os.getpid()}


@app.get("/health")
async def health():
    return {"status": "healthy", "version": "0.1.0"}



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
    )