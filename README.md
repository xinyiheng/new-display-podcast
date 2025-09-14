# 播客展示网站

一个美观的播客展示网站，自动从GitHub项目获取播客数据并展示。专为中国用户优化，部署在Zeabur平台。

## ✨ 特性

- 🎨 **美观的界面设计** - 现代化的渐变背景和卡片式布局
- 📱 **响应式设计** - 完美适配桌面端和移动端
- 🔍 **智能搜索** - 支持标题和内容搜索
- 📅 **日期筛选** - 按时间范围筛选播客
- 🎧 **内嵌音频播放器** - 直接在页面播放音频
- 📄 **文稿查看** - 一键查看播客文稿
- ⬇️ **下载功能** - 支持音频文件下载
- 🔄 **自动更新** - 通过GitHub Webhook自动更新内容
- ⚡ **快速加载** - 优化的性能和缓存策略
- 🇨🇳 **中国优化** - 在中国大陆访问稳定快速

## 🚀 快速开始

### 1. 部署到Zeabur

手动部署步骤：

1. **Fork这个项目**到你的GitHub
2. **登录Zeabur**：访问 [zeabur.com](https://zeabur.com)
3. **创建新项目**：
   - 选择 "Import from GitHub"
   - 选择你Fork的 `podcast-display` 仓库
   - 选择 `main` 分支
4. **配置部署**：
   - Framework: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`
5. **设置环境变量**（可选）：
   ```
   PORT=8080
   DATA_SOURCE=https://pod.zeabur.app/podcast_index.json
   BASE_URL=https://pod.zeabur.app
   ```
6. **部署完成**！获得形如 `https://podcast-display-xxx.zeabur.app` 的访问地址

### 2. 本地开发

```bash
# 克隆项目
git clone https://github.com/your-username/podcast-display.git
cd podcast-display

# 安装Python依赖
pip install -r requirements.txt

# 启动开发服务器
python app.py
```

访问 http://localhost:8080 查看效果。

## ⚙️ 配置

### 数据源配置

在 \`public/script.js\` 中修改数据源配置：

```javascript
const CONFIG = {
    // 主数据源URL（你的播客项目地址）
    DATA_SOURCE: 'https://your-podcast-domain.com/podcast_index.json',
    // 备用数据源
    BACKUP_DATA_SOURCE: 'https://raw.githubusercontent.com/username/repo/gh-pages/podcast_index.json',
    // 播客文件基础URL
    BASE_URL: 'https://your-podcast-domain.com',
    // 每页显示数量
    EPISODES_PER_PAGE: 6
};
```

### GitHub Webhook配置

1. 在你的播客项目仓库中设置Webhook：
   - 进入 Settings > Webhooks
   - 添加新的Webhook
   - Payload URL: \`https://your-display-site.zeabur.app/api/webhook\`
   - Content type: \`application/json\`
   - 选择 "Just the push event"
   - 勾选 "Active"

2. 每当播客项目有新的推送时，展示网站会自动更新。

## 📁 项目结构

```
podcast-display/
├── public/
│   ├── index.html          # 主页面
│   ├── style.css           # 样式文件
│   ├── script.js           # 前端逻辑
│   └── favicon.ico         # 网站图标
├── app.py                  # Flask后端服务
├── requirements.txt        # Python依赖
├── package.json            # 项目配置
├── env.example            # 环境变量示例
└── README.md              # 项目说明
```

## 🛠️ 自定义

### 修改样式

编辑 \`public/style.css\` 文件来自定义网站外观：

- 修改颜色主题
- 调整布局样式
- 添加动画效果
- 响应式断点调整

### 修改功能

编辑 \`public/script.js\` 文件来扩展功能：

- 添加新的筛选选项
- 修改搜索逻辑
- 增加统计图表
- 集成第三方服务

### 添加页面

在 \`public/\` 目录下添加新的HTML文件，比如：

- \`about.html\` - 关于页面
- \`contact.html\` - 联系页面
- \`archive.html\` - 播客归档页面

## 🔧 API接口

### Webhook接口

\`POST /api/webhook\`

接收GitHub的Webhook通知，自动处理播客内容更新。

响应格式：
```json
{
  "success": true,
  "message": "更新处理完成",
  "updateLog": {
    "timestamp": "2025-01-13T10:30:00.000Z",
    "files": ["web/public/podcasts/20250113/podcast.mp3"],
    "commits": [...]
  }
}
```

## 📊 性能优化

- ✅ **静态资源缓存** - 1小时缓存时间
- ✅ **图片懒加载** - 减少初始加载时间
- ✅ **代码压缩** - 自动压缩CSS和JS
- ✅ **CDN加速** - Vercel全球CDN
- ✅ **Progressive Web App** - 支持离线访问

## 🌍 浏览器支持

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+
- 移动端浏览器

## 📜 许可证

MIT License - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🤝 贡献

欢迎提交 Issues 和 Pull Requests！

1. Fork 这个项目
2. 创建你的功能分支 (\`git checkout -b feature/AmazingFeature\`)
3. 提交你的改动 (\`git commit -m 'Add some AmazingFeature'\`)
4. 推送到分支 (\`git push origin feature/AmazingFeature\`)
5. 开启一个 Pull Request

## 📞 支持

如果你遇到任何问题，可以：

- 提交 [GitHub Issue](https://github.com/your-username/podcast-display/issues)
- 发邮件到 your-email@example.com
- 查看 [常见问题](https://github.com/your-username/podcast-display/wiki/FAQ)

---

🎧 **享受你的播客展示网站！**
