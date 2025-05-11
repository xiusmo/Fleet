FROM python:3.11-slim-bookworm

# 添加构建参数，用于注入引导令牌
ARG BOOTSTRAP_TOKEN
ENV BOOTSTRAP_TOKEN=${BOOTSTRAP_TOKEN}

WORKDIR /app

# 安装系统依赖并进行安全更新
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    procps \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 设置Python环境
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app:${PYTHONPATH}"

# 复制项目文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建日志目录
RUN mkdir -p /var/log/fleet && \
    chmod 777 /var/log/fleet

# 创建非root用户运行应用
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -s /bin/bash -m appuser && \
    chown -R appuser:appuser /app && \
    chown -R appuser:appuser /var/log/fleet

USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# 设置环境变量
ENV DEBUG=False
ENV HOST=0.0.0.0
ENV PORT=8000
# Gunicorn配置可通过环境变量进行覆盖
ENV GUNICORN_WORKERS=9
# 将日志输出到标准输出/错误流
ENV GUNICORN_ACCESS_LOG="-"
ENV GUNICORN_ERROR_LOG="-"
ENV GUNICORN_LOG_LEVEL=info
ENV GUNICORN_CAPTURE_OUTPUT=true

# 使用Gunicorn启动应用
CMD gunicorn \
    --workers=${GUNICORN_WORKERS:-9} \
    --bind=${HOST:-0.0.0.0}:${PORT:-8000} \
    --worker-class=uvicorn.workers.UvicornWorker \
    --log-level=${GUNICORN_LOG_LEVEL:-debug} \
    --access-logfile=${GUNICORN_ACCESS_LOG:--} \
    --error-logfile=${GUNICORN_ERROR_LOG:--} \
    main:app