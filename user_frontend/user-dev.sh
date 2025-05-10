#!/bin/bash

# 设置环境变量
export VITE_API_BASE_URL="https://localhost:8000/api/v1"

echo "=== 启动用户前端开发服务器(HTTPS) ==="
echo "访问地址: https://localhost:8080"
echo "API地址: $VITE_API_BASE_URL"

# 先执行npm安装（如果需要）
if [ ! -d "node_modules" ] || [ ! -f "node_modules/.vite/deps/_metadata.json" ]; then
  echo "安装依赖..."
  npm install
fi

# 启动Vite开发服务器
npm run dev 