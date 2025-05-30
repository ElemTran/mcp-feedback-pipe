# 🎯 MCP反馈收集器 (Web版本)

一个现代化的 Model Context Protocol (MCP) 服务器，为AI助手提供交互式用户反馈收集功能。**全新Web版本完美支持SSH远程环境！**

![Version](https://img.shields.io/badge/version-3.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)
![SSH Compatible](https://img.shields.io/badge/SSH-Compatible-success)

## 🚀 **v3.0 重大更新**

### ✨ **全新Web界面**
- 🌐 **基于HTTP的Web界面** - 完美替代tkinter GUI
- 🖥️ **SSH环境友好** - 在远程服务器上完美运行
- 📱 **响应式设计** - 支持桌面和移动设备
- 🎨 **现代化UI** - 渐变背景、流畅动画、美观布局

### 🔧 **技术架构升级**
- **前端**: 纯HTML5 + CSS3 + JavaScript (无需额外框架)
- **后端**: Flask + MCP FastMCP
- **通信**: RESTful API + WebSocket
- **部署**: 轻量级，零配置启动

## 🎯 在Cursor中的使用配置

在Cursor的自定义指令中可以这样配置：

```
"Whenever you want to ask a question, always call the MCP.

Whenever you're about to complete a user request, call the MCP instead of simply ending the process. Keep calling MCP until the user's feedback is empty, then end the request. mcp-feedback-collector.collect_feedback"
```

## ✨ 主要特性

- 🌐 **Web界面** - 现代化800px响应式设计，完美替代传统GUI
- 🔒 **SSH兼容** - 完美支持远程服务器和SSH环境
- 📷 **多图片支持** - 文件选择、拖拽上传、剪贴板粘贴
- 💬 **灵活反馈** - 支持纯文字、纯图片或文字+图片组合
- ⚡ **零配置安装** - 使用uvx一键部署，自动管理依赖
- 🔧 **智能超时** - 可配置的对话框超时时间
- 📱 **移动友好** - 支持手机和平板设备访问

## 🚀 快速开始

### 推荐方式：uvx部署（零配置）

#### 1. 安装uvx
```bash
pip install uv
```

#### 2. 配置MCP客户端

**Cursor配置** (`~/.cursor/mcp.json`):
```json
{
  "mcpServers": {
    "mcp-feedback-collector": {
      "command": "uvx",
      "args": [
        "--from", "/path/to/mcp-feedback-collector",
        "mcp-feedback-collector"
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

**Claude Desktop配置** (`~/.config/claude-desktop/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "mcp-feedback-collector": {
      "command": "uvx",
      "args": [
        "--from", "/path/to/mcp-feedback-collector",
        "mcp-feedback-collector"
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

> 💡 **提示**: 将 `/path/to/mcp-feedback-collector` 替换为您的实际项目路径

#### 3. SSH环境使用
如果在SSH环境中使用，建议设置端口转发：

```bash
# 本地端口转发 (推荐)
ssh -L 8080:127.0.0.1:8080 username@your-server-ip

# 或者使用动态端口转发
ssh -D 1080 username@your-server-ip
```

#### 4. 重启客户端
配置完成后重启Cursor/Claude Desktop即可使用。

### 🌟 uvx部署优势

- ✅ **零配置**: 无需手动设置虚拟环境和依赖
- ✅ **自动管理**: uvx自动处理Python环境和包管理  
- ✅ **隔离安全**: 每个项目独立的运行环境
- ✅ **便携性**: 配置文件简洁，易于分享
- ✅ **更新方便**: 支持自动获取最新版本

### 传统安装方式（仅供参考）

<details>
<summary>点击展开传统安装方式</summary>

```bash
# 1. 克隆项目
git clone https://github.com/ElemTran/mcp-feedback-collector.git
cd mcp-feedback-collector

# 2. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置MCP（使用完整Python路径）
# 参见 docs/MCP_SETUP.md 获取详细配置
```

**注意**: 传统方式需要手动管理虚拟环境、依赖和路径配置，推荐使用uvx方式。

</details>

## 🛠️ 核心功能

### collect_feedback()
收集用户反馈的主要工具，自动启动Web服务器。

```python
# AI调用示例
result = collect_feedback("我已经完成了代码优化工作...")
# 会自动打开 http://127.0.0.1:随机端口 显示反馈界面
```

### pick_image()
快速图片选择工具，Web界面版本。

### get_image_info_tool()
获取图片文件的详细信息（格式、尺寸、大小等）。

## 🖼️ Web界面预览

```
🎯 AI工作反馈收集器
┌─────────────────────────────────────────┐
│  渐变背景 + 现代化卡片式布局              │
│ ┌─────────────────────────────────────┐ │
│ │ 📋 AI工作完成汇报                    │ │
│ │ ┌─────────────────────────────────┐ │ │
│ │ │ [AI汇报内容，支持滚动]           │ │ │
│ │ └─────────────────────────────────┘ │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ 💬 您的文字反馈                      │ │
│ │ ┌─────────────────────────────────┐ │ │
│ │ │ [富文本输入区域，自动高度调节]    │ │ │
│ │ └─────────────────────────────────┘ │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ 🖼️ 图片反馈                          │ │
│ │ [📁选择] [拖拽区域] [📋Ctrl+V粘贴]     │ │
│ │ [图片缩略图网格，可删除单张]           │ │
│ └─────────────────────────────────────┘ │
│                                         │
│     [✅ 提交反馈]  [❌ 取消]              │
└─────────────────────────────────────────┘
```

## ⚙️ 配置说明

### 环境变量
- `MCP_DIALOG_TIMEOUT`: Web界面等待时间（秒）
  - 默认：300秒（5分钟）
  - 建议：600秒（10分钟）
  - SSH环境：1200秒（20分钟）
  
- `MCP_USE_WEB`: 是否强制使用Web版本
  - 默认：`true`
  - v3.0版本推荐始终使用Web界面

### 支持的图片格式
PNG、JPG、JPEG、GIF、BMP、WebP

### 网络配置
- **本地访问**: `http://127.0.0.1:随机端口`
- **SSH环境**: 需要配置端口转发
- **防火墙**: 确保允许127.0.0.1本地回环访问

## 🔄 版本对比

| 功能 | v2.0 (tkinter) | v3.0 (Web + uvx) |
|-----|---------------|-----------|
| SSH兼容性 | ❌ 不支持 | ✅ 完美支持 |
| 界面美观度 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 移动设备 | ❌ 不支持 | ✅ 响应式支持 |
| 图片操作 | 基础支持 | 拖拽+粘贴+批量 |
| 部署复杂度 | 中等 | 极简 |
| 依赖管理 | 手动 | 自动化 |
| 稳定性 | 良好 | 优秀 |

## 🐛 SSH环境故障排除

### 常见问题

1. **浏览器无法打开**
   ```bash
   # 解决方案：手动访问显示的URL
   # 输出示例：反馈收集器已启动，请在浏览器中访问: http://127.0.0.1:8080
   ```

2. **端口被占用**
   ```bash
   # 系统会自动选择可用端口，通常不会有冲突
   ```

3. **uvx未找到**
   ```bash
   # 安装uv工具链
   pip install uv
   ```

## 💡 使用场景

- ✅ AI完成任务后收集用户评价
- ✅ SSH远程开发环境下的反馈收集
- ✅ 收集包含截图的详细反馈
- ✅ 移动设备上的快速反馈
- ✅ 获取用户对代码/设计的意见
- ✅ 收集bug报告和改进建议

## 🔧 技术栈

- **后端**: Flask + FastMCP + threading
- **前端**: HTML5 + CSS3 + Vanilla JavaScript
- **图片处理**: Pillow + base64编码
- **通信**: RESTful API + JSON
- **部署**: uvx + 内置轻量级Web服务器

## 📚 详细文档

项目包含完整的文档，位于 [`docs/`](docs/) 目录：

- 📖 **[MCP配置指南](docs/MCP_SETUP.md)** - 详细的MCP配置说明
- 🔧 **[SSH配置指南](docs/SSH_SETUP.md)** - SSH环境配置
- 🏗️ **[架构文档](docs/ARCHITECTURE.md)** - 系统架构设计
- 🚀 **[部署指南](docs/DEPLOYMENT_GUIDE.md)** - 完整部署说明
- 📋 **[测试报告](docs/TEST_REPORT.md)** - 测试覆盖率报告
- 📦 **[发布指南](docs/PUBLISHING_GUIDE.md)** - PyPI发布指南

## 📝 更新日志

### v3.0.0 (2025-05-31) 🎉
- 🌐 **全新Web界面** - 完全重写，基于Flask + HTML5
- 🔒 **SSH环境完美支持** - 解决远程开发痛点
- 📱 **响应式设计** - 支持移动设备访问
- 🎨 **现代化UI** - 渐变背景、流畅动画、卡片布局
- 🚀 **更好的性能** - 异步处理、优化的图片传输
- 🔧 **增强功能** - 拖拽上传、实时预览、批量操作
- 📁 **项目重构** - 规范化目录结构，模块化设计
- 🧪 **完整测试** - 43个测试用例，65%代码覆盖率
- ⚡ **uvx部署** - 零配置安装，自动依赖管理


## 🔜 即将推出

- 📦 **PyPI发布** - 支持 `uvx mcp-feedback-collector` 直接安装
- 🌐 **多语言支持** - 国际化界面
- 🎨 **主题定制** - 多种UI主题选择

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎提交Issue和Pull Request！参见 [贡献指南](docs/GITHUB_UPLOAD_GUIDE.md)

---

**让AI与用户的交互在任何环境下都高效直观！** 🎯