# Zeabur 部署指南

## 🚀 快速部署

### 1. 推送代码到 GitHub
```bash
git add .
git commit -m "添加 Zeabur 部署配置"
git push origin main
```

### 2. 在 Zeabur 创建项目
1. 登录 [Zeabur 控制台](https://zeabur.com)
2. 点击 "New Project"
3. 选择 "Deploy from GitHub"
4. 选择你的代码仓库
5. 选择 `main` 分支

### 3. 配置环境变量
在 Zeabur 项目设置中添加以下环境变量：

```bash
# ===== 基础配置 =====
PORT=8080
FLASK_ENV=production
PYTHON_VERSION=3.11

# ===== 数据源配置 =====
DATA_SOURCE=https://xinyiheng.github.io/newpody/podcast_index.json
BACKUP_DATA_SOURCE=https://raw.githubusercontent.com/xinyiheng/newpody/gh-pages/podcast_index.json
BASE_URL=https://xinyiheng.github.io/newpody

# ===== Webhook 配置 =====
GITHUB_WEBHOOK_SECRET=your_generated_secret_here

# ===== 缓存配置 =====
CACHE_DURATION=3600

# ===== 持久化存储配置 =====
USE_PERSISTENT_STORAGE=true
PERSISTENT_STORAGE=/tmp/podcast_files
AUTO_CLEANUP_DAYS=30
STORAGE_WARNING_THRESHOLD=90
```

## 📋 部署文件说明

### 配置文件
- **`zeabur.yml`**: 主要的 Zeabur 配置文件
- **`.zeabur/config.yml`**: 详细的 Zeabur 配置
- **`Procfile`**: Heroku 风格的启动命令文件
- **`deploy.sh`**: 部署脚本
- **`requirements.txt`**: Python 依赖包列表

### 应用文件
- **`app.py`**: Flask 应用主文件
- **`package.json`**: 项目信息和脚本配置
- **`public/`**: 静态文件目录

## 🔧 部署检测功能

应用已内置 Zeabur 环境检测：

```python
# 自动检测 Zeabur 环境
if 'ZEABUR' in os.environ:
    print("🚀 检测到 Zeabur 环境")
    USE_PERSISTENT_STORAGE = True
    PERSISTENT_STORAGE = '/tmp/podcast_files'
```

## 📊 部署成功验证

部署完成后，访问以下端点验证：

### 1. 健康检查
```bash
curl https://your-app.zeabur.app/api/status
```

### 2. 文件存储状态
```bash
curl https://your-app.zeabur.app/api/files/storage
```

### 3. 播客数据
```bash
curl https://your-app.zeabur.app/api/podcasts
```

## ⚠️ 常见问题

### 1. 部署失败
- 检查 `requirements.txt` 中的包版本是否兼容
- 确保所有配置文件格式正确
- 查看 Zeabur 构建日志

### 2. 环境变量问题
- 确保所有必需的环境变量都已设置
- 检查变量值是否正确（特别是 URL）

### 3. 文件权限问题
- 确保应用有权限写入 `/tmp` 目录
- 检查持久化存储配置

### 4. 端口问题
- 确保应用监听 `0.0.0.0:8080`
- 检查 Zeabur 的端口映射配置

## 🚨 监控和日志

### 查看日志
```bash
# 在 Zeabur 控制台查看应用日志
# 或者通过 API 访问
curl https://your-app.zeabur.app/api/status
```

### 监控指标
- CPU 使用率
- 内存使用率
- 响应时间
- 错误率

## 🔁 自动更新

项目已配置 GitHub Webhook，当 GitHub 仓库更新时：

1. GitHub 发送 webhook 通知
2. Zeabur 自动重新部署
3. 应用自动获取最新播客数据
4. 文件缓存自动更新

## 🎯 性能优化

### 1. 持久化存储
使用 `/tmp/podcast_files` 目录存储文件，Zeabur 会保持数据持久化。

### 2. 缓存策略
- 数据缓存：1小时
- 文件缓存：永久（除非手动清理）
- 自动清理：30天前的文件

### 3. 负载均衡
- 使用 gunicorn 多 worker 进程
- 每个 worker 处理 4 个并发请求
- 超时时间：120秒

## ✅ 部署检查清单

- [ ] GitHub 仓库已推送代码
- [ ] Zeabur 项目已创建
- [ ] 环境变量已配置
- [ ] 域名已设置
- [ ] HTTPS 已启用
- [ ] 健康检查通过
- [ ] 文件存储正常
- [ ] 播客数据加载正常
- [ ] Webhook 已配置

**部署完成！** 🎉

现在你的播客展示应用已成功部署到 Zeabur，可以正常使用了！