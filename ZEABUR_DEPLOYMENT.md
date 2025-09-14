# Zeabur 部署指南

## 概述
这个播客展示网站部署到 Zeabur 平台后，可以通过 GitHub Webhook 实现自动更新。当 `https://xinyiheng.github.io/newpody` 项目更新时，Zeabur 上的展示网站会自动同步更新内容。

## 部署步骤

### 1. 准备项目
确保你的项目代码已经推送到 GitHub 仓库。

### 2. Zeabur 部署配置

1. **登录 Zeabur**
   - 访问 [zeabur.com](https://zeabur.com)
   - 使用 GitHub 账号登录

2. **创建新项目**
   - 点击 "New Project"
   - 选择 "Import from GitHub"
   - 选择你的播客展示项目仓库
   - 选择 `main` 分支

3. **配置部署设置**
   - **Framework**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Port**: 8080 (自动检测)

### 3. 设置环境变量
在 Zeabur 项目设置中添加以下环境变量：

```bash
# 数据源配置
DATA_SOURCE=https://xinyiheng.github.io/newpody/podcast_index.json
BACKUP_DATA_SOURCE=https://raw.githubusercontent.com/xinyiheng/newpody/gh-pages/podcast_index.json
BASE_URL=https://xinyiheng.github.io/newpody

# 安全配置 (推荐)
GITHUB_WEBHOOK_SECRET=your_generated_secret_here

# 缓存配置 (可选)
CACHE_DURATION=3600
PORT=8080
```

### 4. 生成 Webhook 密钥
在本地终端生成安全密钥：
```bash
openssl rand -hex 20
# 输出示例: a1b2c3d4e5f6789012345678901234567890abcd
```

## GitHub Webhook 设置

### 在 newpody 项目中设置 Webhook

1. **进入 newpody 仓库设置**
   - 打开 `https://github.com/xinyiheng/newpody`
   - 点击 "Settings" → "Webhooks"
   - 点击 "Add webhook"

2. **配置 Webhook**
   - **Payload URL**: `https://your-zeabur-app-url.zeabur.app/api/webhook`
   - **Content type**: `application/json`
   - **Secret**: 输入你在 Zeabur 中设置的 `GITHUB_WEBHOOK_SECRET`
   - **Which events would you like to trigger this webhook?**:
     - 选择 "Just the push event"
   - **Active**: ✓ 勾选

3. **完成设置**
   - 点击 "Add webhook"
   - 测试 Webhook 是否工作正常

## 自动更新机制

### 工作流程
1. 当 `newpody` 项目有新的推送 (push)
2. GitHub 向 Zeabur 应用发送 Webhook
3. Zeabur 应用接收并验证 Webhook
4. 清除数据缓存，强制从 GitHub Pages 重新获取数据
5. 访问者看到最新的播客内容

### 监控和调试

1. **检查 Webhook 状态**
   ```bash
   curl https://your-app.zeabur.app/api/status
   ```

2. **测试 Webhook 端点**
   ```bash
   curl https://your-app.zeabur.app/api/webhook
   ```

3. **查看日志**
   - 在 Zeabur 控制台查看应用日志
   - 检查 Webhook 请求和响应

## 故障排除

### 常见问题

1. **Webhook 验证失败**
   - 确保 `GITHUB_WEBHOOK_SECRET` 在 GitHub 和 Zeabur 中完全一致
   - 检查 Secret 是否包含特殊字符

2. **数据更新延迟**
   - 检查缓存设置 `CACHE_DURATION`
   - 手动触发 Webhook 测试

3. **CORS 错误**
   - 确保 Webhook 端点正确处理 CORS
   - 检查请求头设置

4. **数据源连接失败**
   - 验证 `DATA_SOURCE` 和 `BACKUP_DATA_SOURCE` URL 可访问性
   - 检查 GitHub Pages 是否正常工作

### 性能优化

1. **缓存策略**
   - 默认缓存 1 小时 (3600 秒)
   - 可根据更新频率调整 `CACHE_DURATION`

2. **备用数据源**
   - 主数据源失败时自动切换到备用数据源
   - 确保两个数据源都可用

## 安全建议

1. **启用 Webhook 验证**
   - 始终设置 `GITHUB_WEBHOOK_SECRET`
   - 定期更换密钥

2. **监控访问**
   - 监控 Webhook 请求频率
   - 设置异常告警

3. **定期更新**
   - 保持依赖包最新版本
   - 定期检查和更新配置

---

**部署完成！** 🎉

你的播客展示网站现在已部署到 Zeabur，并且会在 newpody 项目更新时自动同步内容。