# 本地文件缓存功能说明

## 🎯 功能概述

为了解决在中国大陆访问 GitHub 文件缓慢的问题，我们实现了本地文件缓存功能。系统会自动从 GitHub 下载音频和文稿文件到本地服务器，提供更快的访问速度。

## 🚀 工作原理

### 1. 文件下载机制
- **异步下载**: 当用户访问网站时，系统会自动在后台下载文件
- **智能缓存**: 文件只下载一次，避免重复下载
- **回退机制**: 如果本地文件不存在，自动使用远程链接

### 2. 文件存储结构
```
static_files/
├── audio/           # 音频文件
│   ├── 20250913_162139/
│   │   └── podcast.mp3
│   └── 20250913_141647/
│       └── podcast.mp3
└── transcripts/     # 文稿文件
    ├── 20250913_162139/
    │   └── summary.html
    └── 20250913_141647/
        └── summary.html
```

### 3. URL 优先级
1. **本地文件**: `/files/audio/20250913_162139/podcast.mp3`
2. **远程文件**: `https://xinyiheng.github.io/newpody/podcasts/20250913_162139/podcast.mp3`

## 📊 性能优势

### 访问速度对比
- **GitHub 访问**: 中国大陆可能 10-30 秒或超时
- **本地访问**: 通常 0.5-2 秒

### 存储空间
- **音频文件**: 约 660MB (27个文件)
- **文稿文件**: 约 5MB (18个文件)
- **总计**: 约 665MB

## 🔧 新增 API 端点

### 1. 文件状态查询
```bash
GET /api/files/status
```

响应示例：
```json
{
  "audio_files": 27,
  "transcript_files": 18,
  "total_size": 691836050,
  "audio_details": [...],
  "transcript_details": [...]
}
```

### 2. 手动刷新文件
```bash
GET /api/files/refresh
```

响应示例：
```json
{
  "success": true,
  "message": "文件刷新完成",
  "processed_podcasts": 25
}
```

### 3. 本地文件服务
```bash
GET /files/audio/<path:filename>     # 音频文件
GET /files/transcripts/<path:filename>  # 文稿文件
```

## 🎛️ 管理功能

### 1. 实时状态监控
网站会显示当前本地文件缓存状态：
- 🎵 本地音频文件数量
- 📄 本地文稿文件数量
- 💾 总存储大小

### 2. 自动更新
- **首次访问**: 自动开始下载文件
- **后台下载**: 不影响用户浏览体验
- **定期检查**: 每30秒检查文件状态

### 3. 错误处理
- **下载失败**: 自动使用远程链接
- **磁盘空间**: 监控可用空间
- **网络超时**: 30秒超时保护

## 🌍 部署配置

### Zeabur 环境变量
```bash
# 基础配置
PORT=8080
DATA_SOURCE=https://xinyiheng.github.io/newpody/podcast_index.json
BACKUP_DATA_SOURCE=https://raw.githubusercontent.com/xinyiheng/newpody/gh-pages/podcast_index.json
BASE_URL=https://xinyiheng.github.io/newpody
GITHUB_WEBHOOK_SECRET=your_secret_here

# 缓存配置
CACHE_DURATION=3600
```

### 磁盘空间要求
- **最小空间**: 1GB (推荐 2GB)
- **文件系统**: 支持长期存储
- **备份**: 建议定期备份重要文件

## 🚨 注意事项

### 1. 存储空间
- 文件会持续累积，建议定期清理旧文件
- 监控磁盘使用率，避免空间不足

### 2. 更新机制
- GitHub Webhook 会触发文件重新下载
- 新文件会自动下载，旧文件会保留

### 3. 网络带宽
- 首次部署时会消耗较多带宽
- 后续更新只下载新增/修改的文件

## 🔍 故障排除

### 1. 文件下载失败
检查日志中的错误信息：
```bash
# 查看应用日志
curl http://your-app.zeabur.app/api/files/status
```

### 2. 磁盘空间不足
```bash
# 检查文件状态
curl http://your-app.zeabur.app/api/files/status

# 手动清理文件（需要服务器访问权限）
rm -rf static_files/audio/202501*
rm -rf static_files/transcripts/202501*
```

### 3. 访问缓慢
- 确认文件已下载到本地
- 检查网络连接
- 验证 CDN 配置

## 📈 性能监控

### 关键指标
- **下载成功率**: 应该 > 95%
- **缓存命中率**: 应该 > 90%
- **响应时间**: < 2秒
- **磁盘使用率**: < 80%

### 优化建议
1. **定期清理**: 删除超过6个月的旧文件
2. **压缩存储**: 启用文件压缩功能
3. **CDN加速**: 配置静态文件CDN

---

## 🎉 总结

本地文件缓存功能显著提升了在中国大陆的访问体验：
- ✅ 访问速度提升 10-50 倍
- ✅ 避免 GitHub 访问限制
- ✅ 提供更稳定的服务
- ✅ 支持离线访问（缓存文件）

**现在用户在中国大陆也能流畅访问播客内容！** 🚀