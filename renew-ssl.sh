#!/bin/bash

# 手动触发证书续期
echo "开始证书续期..."
docker compose run --rm certbot renew

# 重新加载Nginx以应用新证书
echo "重载Nginx配置..."
docker compose exec nginx nginx -s reload

echo "证书续期完成！" 