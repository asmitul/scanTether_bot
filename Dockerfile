# 使用官方 Python 运行时作为父镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制依赖配置并安装
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 复制项目代码
COPY . .

# 暴露服务端口（FastAPI 默认 8000）
EXPOSE 8000

# 默认启动命令（启动 FastAPI 应用）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 