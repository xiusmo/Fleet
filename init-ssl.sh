#!/bin/bash

# 创建必要的目录
mkdir -p nginx/ssl nginx/logs nginx/modsecurity.d nginx/frontend/admin nginx/frontend/user

# 生成伪证书以便Nginx初始启动
mkdir -p nginx/ssl/dummy
openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
  -keyout nginx/ssl/dummy/privkey.pem \
  -out nginx/ssl/dummy/fullchain.pem \
  -subj "/CN=localhost"

# 创建临时Nginx配置文件，只包括.well-known路径
cat > nginx/conf.d/init.conf << 'EOF'
server {
    listen 80;
    server_name xiusmo.com www.xiusmo.com;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 444;
    }
}
EOF

# 启动Nginx容器
echo "启动Nginx容器..."
docker compose up -d nginx

# 请求SSL证书前先停止Nginx（使用standalone模式）
echo "停止Nginx以使用独立模式申请证书..."
docker compose stop nginx

# 请求SSL证书
echo "请求SSL证书..."
docker compose run --rm certbot certonly --standalone \
  --email admin@xiusmo.com \
  --agree-tos \
  --no-eff-email \
  --rsa-key-size 4096 \
  -d xiusmo.com -d www.xiusmo.com

# 重新启动Nginx
echo "重新启动Nginx..."
docker compose start nginx

# 检查证书是否成功申请
if [ ! -d "certbot_data/live/xiusmo.com" ] && [ ! -d "volumes/certbot_data/live/xiusmo.com" ]; then
  echo "证书申请失败，查看日志以获取更多信息"
  docker compose logs certbot
  exit 1
fi

# 恢复正常Nginx配置
echo "恢复正常Nginx配置..."
if [ -f "nginx/conf.d/default.conf" ]; then
  cp nginx/conf.d/default.conf nginx/conf.d/init.conf
else
  echo "警告：没有找到default.conf文件，请确保您已创建了此文件"
fi

# 重启Nginx以应用新证书
echo "重启Nginx..."
docker compose restart nginx

echo "SSL证书设置完成！"
echo "请检查 volumes/certbot_data/live/xiusmo.com/ 目录中是否有证书文件。"
echo "如果证书成功颁发，您现在可以通过 https://xiusmo.com 访问您的网站。" 