#!/bin/bash

# 创建必要的目录
mkdir -p nginx/ssl nginx/logs nginx/modsecurity.d nginx/frontend/admin nginx/frontend/user

# 生成伪证书以便Nginx初始启动
mkdir -p nginx/ssl/dummy
openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
  -keyout nginx/ssl/dummy/privkey.pem \
  -out nginx/ssl/dummy/fullchain.pem \
  -subj "/CN=localhost"

# 确保已停止所有容器
echo "停止所有容器..."
docker compose down

# 只启动certbot容器申请证书
echo "请求SSL证书..."
docker compose run --rm \
  -p 80:80 \
  -p 443:443 \
  certbot certonly --standalone \
  --preferred-challenges http \
  --email admin@xiusmo.com \
  --agree-tos \
  --no-eff-email \
  --rsa-key-size 4096 \
  -d xiusmo.com -d www.xiusmo.com

# 检查证书是否成功申请
if [ ! -d "certbot_data/live/xiusmo.com" ] && [ ! -d "./volumes/certbot_data/live/xiusmo.com" ]; then
  echo "证书申请失败，查看是否存在以下问题："
  echo "1. 域名未正确指向此服务器IP"
  echo "2. 80/443端口被占用或未开放"
  echo "3. 防火墙阻止了外部访问"
  echo "4. Let's Encrypt速率限制（24小时内尝试次数过多）"
  echo "查看日志获取更多信息..."
  exit 1
fi

# 创建正式的Nginx配置文件
echo "创建Nginx配置..."
cat > nginx/conf.d/default.conf << 'EOF'
# 设置HTTP重定向到HTTPS
server {
    listen 80;
    server_name xiusmo.com www.xiusmo.com;
    
    # Certbot验证目录
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    # 将所有HTTP请求重定向到HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

# 主服务器配置(HTTPS)
server {
    listen 443 ssl;
    server_name xiusmo.com www.xiusmo.com;
    client_max_body_size 100M;
    
    # SSL证书配置
    ssl_certificate /etc/letsencrypt/live/xiusmo.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/xiusmo.com/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/xiusmo.com/chain.pem;
    
    # SSL参数
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_session_tickets off;
    ssl_dhparam /etc/nginx/ssl/dhparam.pem;
    
    # 安全性headers
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; connect-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; font-src 'self' data:;" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

    # 禁用服务器版本显示
    server_tokens off;

    # 用户前端
    location / {
        root /usr/share/nginx/frontend/user;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    # 管理员前端
    location /admin/ {
        alias /usr/share/nginx/frontend/admin/;
        index index.html;
        try_files $uri $uri/ /admin/index.html;
        
        auth_basic "管理员区域";
        auth_basic_user_file /etc/nginx/.htpasswd;
    }

    # 后端API
    location /api/ {
        proxy_pass http://backend:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 健康检查
    location /health {
        proxy_pass http://backend:8000/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # pgAdmin访问
    location /pgadmin/ {
        proxy_pass http://pgadmin:5050/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Script-Name /pgadmin;
        
        auth_basic "管理员区域";
        auth_basic_user_file /etc/nginx/.htpasswd;
    }
}
EOF

# 生成DH参数
echo "生成DH参数文件（这可能需要一些时间）..."
openssl dhparam -out nginx/ssl/dhparam.pem 2048

# 创建基本认证文件
if [ ! -f "nginx/.htpasswd" ]; then
    echo "创建基本认证文件..."
    echo "admin:$(openssl passwd -apr1 admin123)" > nginx/.htpasswd
    echo "创建了默认用户名 'admin' 密码 'admin123'，请尽快修改！"
fi

# 启动所有服务
echo "启动所有服务..."
docker compose up -d

echo "SSL证书设置完成！"
echo "您现在可以通过 https://xiusmo.com 访问您的网站。"
echo "请确保修改默认的管理员密码！" 