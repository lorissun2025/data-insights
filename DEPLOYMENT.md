FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制后端代码
COPY backend/ /app/backend/
COPY requirements.txt /app/

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制前端代码
COPY frontend/ /app/frontend/

# 创建日志目录
RUN mkdir -p /app/backend/logs

# 暴露端口
EXPOSE 8000 8001 8002 8003 8004

# 复制启动脚本
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# 启动所有服务
CMD ["/app/docker-entrypoint.sh"]
