# 🔄 GitHub仓库重命名指南

本指南将帮助您将GitHub仓库从 `mcp-feedback-collector` 重命名为 `mcp-feedback-pipe`。

## 🎯 重命名步骤

### 1. 在GitHub网站上重命名仓库

1. **访问仓库设置**
   - 打开您的GitHub仓库页面
   - 点击 **Settings** 标签页

2. **重命名仓库**
   - 滚动到页面底部的 **Danger Zone** 区域
   - 点击 **Change repository name**
   - 输入新名称：`mcp-feedback-pipe`
   - 点击 **I understand, rename my repository**

### 2. 更新本地仓库配置

```bash
# 查看当前远程仓库URL
git remote -v

# 更新远程仓库URL
git remote set-url origin https://github.com/你的用户名/mcp-feedback-pipe.git

# 验证更新
git remote -v
```

### 3. 更新本地项目目录（可选）

```bash
# 重命名本地项目目录
cd ..
mv mcp-feedback-collector mcp-feedback-pipe
cd mcp-feedback-pipe
```

### 4. 更新Cursor MCP配置

编辑 `~/.cursor/mcp.json`：

```json
{
  "mcpServers": {
    "mcp-feedback-pipe": {
      "command": "uvx",
      "args": [
        "--from", "/home/yjb/mcp-feedback-pipe",
        "mcp-feedback-pipe"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "MCP_DIALOG_TIMEOUT": "600",
        "MCP_USE_WEB": "true"
      }
    }
  }
}
```

### 5. 推送更改到新仓库

```bash
# 添加所有更改
git add .

# 提交更改
git commit -m "🎯 项目重命名为 mcp-feedback-pipe (反馈通道)"

# 推送到新的远程仓库
git push origin main
```

## 🔍 验证重命名成功

1. **检查远程仓库**
   ```bash
   git remote -v
   # 应该显示新的URL: https://github.com/你的用户名/mcp-feedback-pipe.git
   ```

2. **测试克隆**
   ```bash
   # 在另一个目录测试克隆
   git clone https://github.com/你的用户名/mcp-feedback-pipe.git
   ```

3. **验证MCP工具**
   ```bash
   # 测试uvx安装
   uvx --from . mcp-feedback-pipe
   ```

## ⚠️ 注意事项

1. **旧链接失效**: 重命名后，所有指向旧仓库名的链接都会失效
2. **自动重定向**: GitHub会自动将旧URL重定向到新URL，但建议更新所有引用
3. **协作者通知**: 如果有协作者，需要通知他们更新本地仓库配置
4. **CI/CD更新**: 如果使用了CI/CD服务，需要更新相关配置

## 🚀 完成后的好处

- ✅ 项目名称统一为 `mcp-feedback-pipe`
- ✅ 避免与现有包的命名冲突
- ✅ 更清晰的项目定位（反馈通道）
- ✅ 为PyPI发布做好准备

## 🆘 遇到问题？

如果在重命名过程中遇到问题：

1. **权限问题**: 确保您是仓库的所有者或有管理权限
2. **名称冲突**: 确保新名称没有被其他仓库使用
3. **本地同步**: 使用 `git fetch` 和 `git pull` 同步最新更改

重命名完成后，您的项目就完全使用新名称 `mcp-feedback-pipe` 了！ 