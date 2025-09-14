FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用文件
COPY . .

# 创建必要的目录
RUN mkdir -p /tmp/podcast_files/audio /tmp/podcast_files/transcripts

# 暴露端口
EXPOSE 8080

# 设置环境变量
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# 启动应用
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "--workers", "4", "--timeout", "120", "app:app"]