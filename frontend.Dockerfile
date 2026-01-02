# 构建阶段
FROM node:18-alpine AS build
WORKDIR /app

# 复制并安装依赖
COPY frontend/package*.json ./
RUN npm install --registry=https://registry.npmmirror.com

# 复制代码并构建
COPY frontend/ .
RUN npm run build

# 运行阶段
FROM nginx:alpine

# 复制构建产物到 Nginx 静态目录
COPY --from=build /app/dist /usr/share/nginx/html

# 复制自定义 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动 Nginx
CMD ["nginx", "-g", "daemon off;"]