# 使用Python 3.9作为基础镜像
FROM python:3.13-slim

# 设置工作目录
WORKDIR /app

# 设置Python环境变量
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements.txt
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建非root用户
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# 创建日志目录
RUN mkdir -p logs && chown -R appuser:appuser logs

# 容器启动命令在docker-compose中定义 