# 使用官方 Python 3 镜像作为基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件到容器内的工作目录
COPY . /app

# 安装项目的依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置 Flask 应用默认运行端口
EXPOSE 5000

# 启动 Flask 应用
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:5000", "--timeout", "120", "--log-level", "info", "app:app"]