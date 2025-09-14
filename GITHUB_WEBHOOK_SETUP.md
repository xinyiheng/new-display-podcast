# GitHub Webhook 设置指南

## 步骤详解

### 1. 进入 newpody 仓库

1. 打开浏览器，访问：`https://github.com/xinyiheng/newpody`
2. 确保你已登录 GitHub 账号
3. 有仓库的管理员权限

### 2. 进入 Webhook 设置页面

**方法一：通过仓库设置**
1. 点击仓库页面右上角的 **"Settings"** 按钮
   - 位于仓库右上角，靠近 "Star"、"Fork" 按钮
2. 在左侧菜单中找到并点击 **"Webhooks"**
   - 通常在 "Options" 部分

**方法二：直接访问 URL**
- 直接访问：`https://github.com/xinyiheng/newpody/settings/hooks`

### 3. 添加新 Webhook

1. 在 Webhooks 页面，点击绿色的 **"Add webhook"** 按钮
2. 如果提示输入密码，请输入你的 GitHub 密码进行验证

### 4. 配置 Webhook 详细信息

#### **Payload URL**
```
https://your-app-name.zeabur.app/api/webhook
```
- **注意**：将 `your-app-name` 替换为你在 Zeabur 中实际的应用名称
- 示例：`https://podcast-display-demo.zeabur.app/api/webhook`

#### **Content type**
- 选择 **`application/json`**
- 不要选择 `application/x-www-form-urlencoded`

#### **Secret**
```
your_webhook_secret_here
```
- 输入你在 Zeabur 中设置的 `GITHUB_WEBHOOK_SECRET`
- 例如：`2598fc2d61f533afa48e6e745df163032078887b`
- **重要**：这个 Secret 必须与 Zeabur 环境变量中的完全一致

#### **Which events would you like to trigger this webhook?**

选择 **"Just the push event"**
- 这样只有当有代码推送时才会触发
- 更安全，不会因为其他事件（如 issue 创建）而触发

#### **Active**
- ✅ **勾选** 这个复选框
- 确保 Webhook 处于激活状态

### 5. 完成设置

1. 点击绿色的 **"Add webhook"** 按钮
2. 等待页面刷新，你应该能看到新创建的 Webhook

### 6. 验证 Webhook 设置

#### 检查 Webhook 状态
- 在 Webhooks 列表中，你应该看到：
  - 绿色的勾号 ✓ 表示 Webhook 工作正常
  - 最后触发时间
  - 最后响应状态

#### 测试 Webhook
1. 在 Webhook 列表中找到你创建的 Webhook
2. 点击右侧的 **"..."** 菜单
3. 选择 **"Redeliver"** 重新发送最后一次推送
4. 或者选择 **"Test webhook"** → **"Push event"** 发送测试请求

#### 查看 Webhook 日志
1. 点击 Webhook 名称进入详情页面
2. 查看 **"Recent Deliveries"** 部分
3. 检查每个请求的：
   - 请求时间
   - 响应状态（应该是 200 OK）
   - 响应内容

### 7. 验证 Zeabur 端点

#### 测试 Webhook 端点
在浏览器中访问：
```
https://your-app-name.zeabur.app/api/webhook
```

应该返回类似以下的 JSON 响应：
```json
{
  "message": "Webhook endpoint is working",
  "timestamp": "2025-01-14T10:30:00.000Z",
  "data_source": "https://xinyiheng.github.io/newpody/podcast_index.json",
  "base_url": "https://xinyiheng.github.io/newpody"
}
```

#### 检查应用状态
访问：
```
https://your-app-name.zeabur.app/api/status
```

应该返回应用状态信息。

## 故障排除

### 常见问题

#### 1. Webhook 显示红色警告
- **原因**：URL 不可达或返回错误状态码
- **解决**：
  - 检查 Zeabur 应用是否正常运行
  - 验证 URL 是否正确
  - 查看 Zeabur 日志

#### 2. 签名验证失败
- **原因**：Secret 不匹配
- **解决**：
  - 确保 GitHub 和 Zeabur 中的 Secret 完全一致
  - 检查是否有空格或特殊字符
  - 重新生成 Secret 并在两端更新

#### 3. CORS 错误
- **原因**：跨域请求被阻止
- **解决**：应用已配置 CORS 处理，如仍有问题请检查代码

#### 4. 404 错误
- **原因**：URL 路径错误
- **解决**：确保使用 `/api/webhook` 而不是 `/webhook`

### 调试步骤

1. **检查 Zeabur 日志**
   - 在 Zeabur 控制台查看应用日志
   - 查找 Webhook 相关的请求记录

2. **使用 curl 测试**
   ```bash
   curl -X POST https://your-app.zeabur.app/api/webhook \
     -H "Content-Type: application/json" \
     -H "X-GitHub-Event: push" \
     -H "X-Hub-Signature-256: sha256=your_signature" \
     -d '{"test": true}'
   ```

3. **查看网络请求**
   - 使用浏览器开发者工具检查网络请求
   - 查看请求头和响应内容

## 自动更新测试

### 手动触发更新
1. 在 newpody 仓库中创建一个测试文件
2. 提交并推送到 main 分支
3. 观察 GitHub Webhook 是否触发
4. 检查 Zeabur 应用是否更新了数据

### 验证更新效果
1. 访问你的 Zeabur 应用
2. 检查播客内容是否更新
3. 查看页面最后更新时间

---

**设置完成！** 🎉

现在每当 newpody 仓库有新的推送时，Zeabur 上的播客展示网站会自动更新内容。