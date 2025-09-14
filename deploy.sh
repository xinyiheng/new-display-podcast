#!/bin/bash

# Zeabur 部署脚本
echo "🚀 开始部署播客展示应用..."

# 检查Python版本
echo "📋 检查Python版本..."
python --version

# 安装依赖
echo "📦 安装Python依赖..."
pip install -r requirements.txt

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p /tmp/podcast_files/audio
mkdir -p /tmp/podcast_files/transcripts
mkdir -p static

# 设置环境变量
export PORT=${PORT:-8080}
export FLASK_ENV=${FLASK_ENV:-production}
export PYTHONUNBUFFERED=1

# 检查配置文件
echo "⚙️ 检查配置文件..."
if [ -f "env.example" ]; then
    echo "✅ 环境变量示例文件存在"
fi

if [ -f "ZEABUR_PERSISTENCE.md" ]; then
    echo "✅ 持久化存储配置文件存在"
fi

# 运行应用
echo "🎧 启动播客展示应用..."
echo "📡 监听端口: $PORT"
echo "🌍 环境: $FLASK_ENV"

# 使用 gunicorn 启动应用
exec gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 --access-logfile - --error-logfile - app:app