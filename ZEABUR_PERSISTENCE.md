# Zeabur 持久化存储配置指南

## 💾 Zeabur 存储选项分析

Zeabur 提供了几种存储方案，针对我们的播客文件缓存需求：

### 方案1：使用 `/tmp` 目录（推荐）
- **持久性**: ✅ 在重新部署之间保持
- **容量**: 通常 1-10GB
- **速度**: 最快（本地存储）
- **成本**: 免费

### 方案2：挂载磁盘（如果可用）
- **持久性**: ✅ 永久存储
- **容量**: 可配置（10GB+）
- **速度**: 快速
- **成本**: 可能需要付费

### 方案3：对象存储（R2/S3）
- **持久性**: ✅ 永久存储
- **容量**: 几乎无限
- **速度**: 中等（网络延迟）
- **成本**: 按使用量付费

## 🚀 推荐配置（方案1：/tmp 目录）

### 1. Zeabur 环境变量配置

在 Zeabur 项目设置中添加以下环境变量：

```bash
# ===== 基础配置 =====
PORT=8080
DATA_SOURCE=https://xinyiheng.github.io/newpody/podcast_index.json
BACKUP_DATA_SOURCE=https://raw.githubusercontent.com/xinyiheng/newpody/gh-pages/podcast_index.json
BASE_URL=https://xinyiheng.github.io/newpody
GITHUB_WEBHOOK_SECRET=your_generated_secret
CACHE_DURATION=3600

# ===== 持久化存储配置 =====
USE_PERSISTENT_STORAGE=true
PERSISTENT_STORAGE=/tmp/podcast_files
AUTO_CLEANUP_DAYS=30
STORAGE_WARNING_THRESHOLD=90
```

### 2. 存储特点

#### ✅ 优点
- **零配置**: 无需额外设置
- **高性能**: 本地文件系统访问
- **自动持久化**: 重新部署时文件保持
- **免费包含**: 在 Zeabur 免费额度内

#### ⚠️ 注意事项
- **容量限制**: 通常 1-10GB（取决于 Zeabur 配置）
- **定期清理**: 需要自动清理旧文件避免空间不足
- **备份**: 建议定期备份重要文件

## 🔧 可选：挂载磁盘配置

如果 Zeabur 提供磁盘挂载功能：

### 1. 创建磁盘
```bash
# 在 Zeabur 控制台
1. 进入项目设置
2. 选择 "Storage" 或 "Volumes"
3. 创建新磁盘（建议 10GB）
4. 挂载路径: /mnt/podcast_files
```

### 2. 更新环境变量
```bash
PERSISTENT_STORAGE=/mnt/podcast_files
```

## 📊 存储管理功能

### 1. 自动存储管理
系统已实现以下功能：

#### 🧹 自动清理
- **触发条件**: 存储使用率 > 90%
- **清理策略**: 删除 30 天前的文件
- **智能清理**: 只删除旧文件，保留最新内容

#### 📈 存储监控
- **实时监控**: API 端点 `/api/files/storage`
- **使用统计**: 文件数量、大小、使用率
- **预警机制**: 空间不足时自动清理

#### 🔄 智能缓存
- **优先级**: 本地文件 > GitHub 文件
- **自动下载**: 首次访问时下载
- **断点续传**: 避免重复下载

### 2. 管理API端点

#### 查看存储状态
```bash
curl http://your-app.zeabur.app/api/files/storage
```

响应示例：
```json
{
  "storage": {
    "total_space": 10737418240,
    "used_space": 691836050,
    "free_space": 4045582190,
    "usage_percent": 64.4
  },
  "files": {
    "audio_count": 27,
    "transcript_count": 18,
    "total_count": 45,
    "total_size": 691836050
  },
  "configuration": {
    "persistent_storage": true,
    "storage_path": "/tmp/podcast_files",
    "current_base_dir": "/tmp/podcast_files"
  }
}
```

#### 手动清理文件
```bash
curl -X POST http://your-app.zeabur.app/api/files/cleanup \
  -H "Content-Type: application/json" \
  -d '{"max_age_days": 30}'
```

#### 查看文件状态
```bash
curl http://your-app.zeabur.app/api/files/status
```

## 🚀 部署步骤

### 1. 推送代码到 GitHub
```bash
git add .
git commit -m "添加持久化存储功能"
git push origin main
```

### 2. 配置 Zeabur 环境变量
在 Zeabur 控制台设置环境变量（见上文配置）

### 3. 部署应用
- Zeabur 会自动重新部署
- 部署后文件会自动下载到持久化存储

### 4. 验证部署
```bash
# 检查存储模式
curl http://your-app.zeabur.app/api/files/storage

# 查看文件下载状态
curl http://your-app.zeabur.app/api/files/status
```

## 📈 性能优化建议

### 1. 存储策略
- **保留最新**: 只保留最近 3 个月的播客
- **压缩存储**: 考虑压缩不常用的文件
- **定期备份**: 重要文件定期备份到 GitHub

### 2. 监控设置
- **设置告警**: 存储使用率 > 80% 时通知
- **定期检查**: 每周检查存储状态
- **性能监控**: 跟踪下载和访问速度

### 3. 成本优化
- **控制数量**: 限制同时缓存的文件数量
- **定期清理**: 自动清理过期文件
- **压缩策略**: 使用压缩减少存储占用

## 🎯 总结

**推荐使用 `/tmp` 目录方案**，因为：

1. **零配置成本**: 无需额外设置
2. **良好性能**: 本地存储访问快速
3. **自动持久化**: Zeabur 会保持文件
4. **智能管理**: 自动清理和监控
5. **免费使用**: 在免费额度内

这样可以确保：
- ✅ 中国用户快速访问
- ✅ 文件持久化存储
- ✅ 自动空间管理
- ✅ 零运营成本

**现在你可以安心部署到 Zeabur，数据会安全持久化存储！** 🚀