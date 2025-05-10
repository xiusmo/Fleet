# syntax=docker/dockerfile:1.4

# 1. 构建 Admin Dashboard
FROM node:18-alpine AS admin_builder
WORKDIR /app
COPY admin_dashboard/package*.json ./
RUN npm ci --silent
COPY admin_dashboard/ ./
RUN npm run build

# 2. 构建 User Frontend
FROM node:18-alpine AS user_builder
WORKDIR /app
COPY user_frontend/package*.json ./
RUN npm ci --silent
RUN npm install terser --no-save
COPY user_frontend/ ./
RUN npm run build

# 3. 最终 Nginx 镜像
FROM owasp/modsecurity-crs:nginx-alpine

# 复制 Nginx 配置 & ModSecurity 规则
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY nginx/conf.d/ /etc/nginx/conf.d/
COPY nginx/.htpasswd /etc/nginx/.htpasswd
COPY nginx/modsecurity.d/ /etc/nginx/modsecurity.d/

# 创建 SSL 目录，生成 dhparam.pem，并设置权限
RUN mkdir -p /etc/nginx/ssl \
 && chown -R nginx:nginx /etc/nginx/ssl \
 && openssl dhparam -out /etc/nginx/ssl/dhparam.pem 2048

# 复制前端静态资源
COPY --from=admin_builder /app/dist /usr/share/nginx/frontend/admin
COPY --from=user_builder /app/dist /usr/share/nginx/frontend/user

# 挂载证书和 Certbot Webroot
VOLUME ["/etc/letsencrypt", "/var/www/certbot"]

# 暴露端口
EXPOSE 80 443

# 简化启动命令，直接启动 Nginx
CMD ["nginx", "-g", "daemon off;"]