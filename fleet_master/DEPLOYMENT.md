# 分布式任务调度系统 - 生产环境部署指南

## 环境要求

- Python 3.9+
- PostgreSQL 13+
- 足够的系统资源（取决于预期负载）

## 部署步骤

### 1. 准备环境变量

创建一个包含以下内容的`.env`文件：

```env
# 基本设置
DEBUG=False
SECRET_KEY=your-secure-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
CURRENT_NODE=main-scheduler
ALLOW_REGISTER=False

# 数据库设置
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_SERVER=your_db_host
POSTGRES_PORT=5432
POSTGRES_DB=task_scheduler

# CORS设置
ALLOWED_ORIGINS=https://your-domain.com,https://admin.your-domain.com

# Gunicorn 设置
GUNICORN_WORKERS=8  # 或根据您的CPU核心数调整
GUNICORN_THREADS=1
GUNICORN_TIMEOUT=120
GUNICORN_KEEPALIVE=5
GUNICORN_MAX_REQUESTS=1000
GUNICORN_MAX_REQUESTS_JITTER=50
GUNICORN_GRACEFUL_TIMEOUT=30
GUNICORN_ACCESS_LOG=/var/log/fleet/access.log
GUNICORN_ERROR_LOG=/var/log/fleet/error.log
GUNICORN_LOG_LEVEL=warning
```

确保替换所有敏感信息为强密码和适合您环境的配置。

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

也可以考虑使用虚拟环境:

```bash
python -m venv venv
source venv/bin/activate  # 在Windows上使用 venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 准备数据库

确保PostgreSQL数据库已创建并配置好。应用启动时会自动创建必要的表。

### 4. 启动应用

使用Gunicorn作为生产服务器：

```bash
gunicorn -c main.py main:app
```

建议使用进程管理工具（如Supervisor或Systemd）来管理Gunicorn进程：

#### Systemd 配置示例

创建文件 `/etc/systemd/system/fleet-scheduler.service`:

```
[Unit]
Description=Fleet Distributed Task Scheduler
After=network.target postgresql.service

[Service]
User=fleet
Group=fleet
WorkingDirectory=/path/to/fleet_task_scheduler
Environment="PATH=/path/to/venv/bin"
EnvironmentFile=/path/to/fleet_task_scheduler/.env
ExecStart=/path/to/venv/bin/gunicorn -c main.py main:app
Restart=always
RestartSec=5
StartLimitInterval=0

[Install]
WantedBy=multi-user.target
```

然后启用并启动服务：

```bash
sudo systemctl enable fleet-scheduler
sudo systemctl start fleet-scheduler
```

### 5. 配置反向代理

建议使用Nginx作为反向代理:

```nginx
server {
    listen 80;
    server_name api.your-domain.com;

    # 重定向到HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name api.your-domain.com;

    ssl_certificate /path/to/fullchain.pem;
    ssl_certificate_key /path/to/privkey.pem;
    
    # SSL配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 6. 设置监控

建议设置监控系统以跟踪应用的性能和健康状况。您可以使用Prometheus和Grafana或其他监控工具。

API提供了`/health`端点，可以用于健康检查。

### 7. 日志管理

设置日志轮转以防止日志文件过大：

```
/var/log/fleet/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 fleet fleet
    sharedscripts
    postrotate
        systemctl reload fleet-scheduler
    endscript
}
```

## 安全建议

1. 确保使用强密码和密钥
2. 限制数据库访问权限
3. 配置防火墙以限制对服务器的访问
4. 定期更新系统和依赖
5. 设置SSL/TLS证书和HTTPS
6. 启用CSRF保护和安全头部

## 性能优化

1. 根据服务器资源调整Gunicorn工作进程数
2. 优化数据库查询和索引
3. 考虑使用缓存（如Redis）提高性能
4. 进行负载测试以确定最佳配置

## 问题排查

常见问题解决方案：

1. 检查日志文件（`/var/log/fleet/error.log`）
2. 确保数据库连接正常
3. 验证.env文件中的环境变量配置
4. 检查网络和防火墙配置

如有需要，请联系技术支持团队获取帮助。 