# Zeabur 部署问题解决方案

## 🚨 问题：Zeabur 无法识别项目类型

### 解决方案

#### 方案 1：使用环境变量覆盖（推荐）

在 Zeabur 控制台中设置以下环境变量：

```bash
# 构建配置
BUILD_COMMAND = pip install -r requirements.txt
START_COMMAND = gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 app:app

# 框架检测
FRAMEWORK = python
RUNTIME = python

# 端口配置
PORT = 8080
```

#### 方案 2：手动配置 Zeabur

1. **删除所有配置文件**（如果自动识别失败）
2. **在 Zeabur 控制台手动配置**：
   - **Framework**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 app:app`
   - **Port**: 8080

#### 方案 3：使用 Docker 部署

如果上述方案都不行，使用 Docker 部署：

1. **在 Zeabur 选择 Docker 部署**
2. **使用提供的 Dockerfile**
3. **设置环境变量**：
   ```bash
   FLASK_ENV=production
   PORT=8080
   PYTHONUNBUFFERED=1
   ```

## 📋 项目文件结构

```
podcast-display/
├── app.py                    # Flask 应用
├── requirements.txt          # Python 依赖
├── runtime.txt              # Python 版本
├── Procfile                 # 启动命令
├── zeabur.yml              # Zeabur 配置
├── .zeabur/
│   ├── config.yml          # 详细配置
│   └── deploy.yml          # 简化配置
├── .zeaburignore           # 构建忽略文件
├── Dockerfile              # Docker 配置
├── docker-compose.yml      # Docker Compose
├── deploy.sh               # 部署脚本
└── public/                 # 静态文件
```

## 🔧 关键配置文件

### 1. runtime.txt
```
3.11.0
```

### 2. Procfile
```
web: gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 --access-logfile - --error-logfile - app:app
```

### 3. requirements.txt
```
Flask==3.0.3
requests==2.31.0
Werkzeug==3.0.3
gunicorn==21.2.0
python-dotenv==1.0.0
```

## 🚀 部署步骤

### 步骤 1：推送代码
```bash
git add .
git commit -m "修复部署配置"
git push origin main
```

### 步骤 2：Zeabur 配置
1. **进入 Zeabur 控制台**
2. **选择项目**
3. **点击 "Settings"**
4. **设置环境变量**：
   ```bash
   PORT=8080
   FLASK_ENV=production
   PYTHONUNBUFFERED=1
   ```

### 步骤 3：重新部署
1. **点击 "Redeploy"**
2. **观察构建日志**
3. **检查启动状态**

## 📊 验证部署

### 1. 健康检查
```bash
curl https://your-app.zeabur.app/api/status
```

### 2. 查看日志
在 Zeabur 控制台查看应用日志，应该看到：
```
🎧 播客展示应用启动
📡 监听地址: 0.0.0.0:8080
🌍 环境: production
🚀 检测到 Zeabur 环境
🔄 生产模式启动
```

## ⚠️ 常见错误

### 1. ModuleNotFoundError
确保 `requirements.txt` 中的所有包都正确安装。

### 2. Port already in use
检查端口配置，确保没有其他进程占用 8080 端口。

### 3. Permission denied
确保应用有权限写入 `/tmp` 目录。

### 4. Build failed
查看构建日志，检查 Python 版本和依赖包是否兼容。

## 🎯 最终解决方案

如果所有自动配置都失败，**最简单的方法是**：

1. **在 Zeabur 控制台手动设置**：
   ```
   Framework: Python
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 app:app
   Port: 8080
   ```

2. **设置环境变量**：
   ```
   PORT=8080
   FLASK_ENV=production
   PYTHONUNBUFFERED=1
   ```

3. **点击 "Deploy"**

这样应该可以解决所有识别问题！

---

**💡 提示**: 如果仍有问题，请检查 Zeabur 的构建日志，通常会有具体的错误信息可以帮助定位问题。