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

# 复制前端静态资源
COPY --from=admin_builder /app/dist /usr/share/nginx/frontend/admin
COPY --from=user_builder /app/dist /usr/share/nginx/frontend/user

# 挂载证书和 Certbot Webroot
VOLUME ["/etc/letsencrypt", "/var/www/certbot"]

# 暴露端口
EXPOSE 80 443

# 默认启动：生成 dhparam（如不存在）并启动 Nginx
CMD ["/bin/sh", "-c", "[ -f /etc/nginx/ssl/dhparam.pem ] || openssl dhparam -out /etc/nginx/ssl/dhparam.pem 2048 && nginx -g 'daemon off;'"] 