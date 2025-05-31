# 🎯 MCP反馈通道 (MCP Feedback Pipe)

**版本**: 3.0.0 | **架构**: Web版本 | **支持**: SSH远程环境

一个基于Flask的现代化Web界面反馈收集工具，专为MCP (Model Context Protocol) 环境设计。从GUI架构完全重构为Web架构，完美支持SSH远程环境和Cursor等现代开发工具。

---

## 🚀 快速开始

### ⭐ 推荐：uvx一键安装

```bash
# PyPI发布完成后，零配置一键运行
uvx mcp-feedback-pipe
```

> **📦 发布状态**: PyPI包已构建完成，使用全新名称`mcp-feedback-pipe`避免冲突

### 📦 传统方式安装

```bash
# 克隆项目
git clone https://github.com/ElemTran/mcp-feedback-pipe.git
cd mcp-feedback-pipe

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
python scripts/start_server.py
```

---

## 🎯 核心特性

### ✨ 用户体验
- **🌐 现代Web界面**: 基于Flask + HTML5的响应式设计
- **📱 多设备支持**: 手机、平板、电脑完美适配
- **🎨 优雅交互**: 实时反馈、动画效果、直观操作

### 🔧 技术架构
- **🏗️ 模块化设计**: 8个核心模块，关注点分离
- **🧪 完整测试**: 43个测试用例，65%代码覆盖率
- **📊 实时监控**: 服务状态、端口管理、进程监控

### 🌍 环境兼容
- **🔗 SSH远程支持**: 完美支持SSH端口转发
- **🎯 Cursor集成**: 无缝集成Cursor MCP工具链
- **⚡ uvx零配置**: 一键安装，即开即用

---

## 🛠️ Cursor MCP配置

### 推荐配置 (uvx方式)
```json
{
  "mcpServers": {
    "mcp-feedback-pipe": {
      "command": "uvx",
      "args": ["mcp-feedback-pipe"],
      "env": {
        "MCP_USE_WEB": "true",
        "MCP_DIALOG_TIMEOUT": "600"
      }
    }
  }
}
```

### 备选配置 (本地开发)
```json
{
  "mcpServers": {
    "mcp-feedback-pipe": {
      "command": "/path/to/mcp-feedback-pipe/.venv/bin/python",
      "args": ["-m", "mcp_feedback_pipe.server"],
      "env": {
        "PYTHONPATH": "/path/to/mcp-feedback-pipe/src",
        "MCP_USE_WEB": "true"
      }
    }
  }
}
```

---

## 🔗 SSH环境部署

### 端口转发配置
```bash
# 本地转发（推荐）
ssh -L 5000:localhost:5000 username@your-server-ip

# 使用VS Code SSH扩展会自动处理端口转发
```

## 🎯 在Cursor中的使用配置

在Cursor的自定义指令中可以这样配置：

```
"Whenever you want to ask a question, always call the MCP.

Whenever you're about to complete a user request, call the MCP instead of simply ending the process. Keep calling MCP until the user's feedback is empty, then end the request. mcp-feedback-pipe.collect_feedback"
```
---

## 📚 可用工具

### 🎯 核心功能
- **`collect_feedback`**: 启动Web界面收集用户反馈
- **`pick_image`**: 图片选择和上传功能
- **`get_image_info_tool`**: 获取图片详细信息

### 💡 使用示例
```python
# 在Cursor中调用
# 1. 收集用户反馈
工具会自动启动Web界面，用户可以输入文字或上传图片

# 2. 查看图片信息
自动解析图片格式、尺寸、大小等元数据
```

---

## 🏗️ 项目架构

### 📁 目录结构
```
mcp-feedback-pipe/
├── src/mcp_feedback_pipe/         # 核心源代码
│   ├── server.py                  # MCP服务器
│   ├── web_app.py                # Flask Web应用
│   ├── server_manager.py         # 服务管理器
│   └── templates/                # Web模板
├── scripts/                      # 实用脚本
├── tests/                        # 测试套件
└── docs/                         # 完整文档
```

### 🧪 质量保证
- **单元测试**: 32个测试用例
- **集成测试**: 11个测试用例  
- **代码覆盖率**: 65%
- **代码规范**: 每个文件<250行

---

## 📖 文档资源

### 📋 配置指南
- [SSH设置指南](docs/SSH_SETUP.md) - 完整的SSH配置说明
- [MCP配置手册](docs/MCP_SETUP.md) - Cursor和Claude配置
- [部署指南](docs/DEPLOYMENT_GUIDE.md) - 多种部署方案对比

### 🏛️ 技术文档  
- [架构设计](docs/ARCHITECTURE.md) - 系统架构和设计理念
- [测试报告](docs/TEST_REPORT.md) - 详细的测试覆盖率报告

---

## 🎯 版本历史

### v3.0.0 (当前版本)
- **🏗️ 架构重构**: GUI → Web，完全重写
- **🌐 现代化界面**: Flask + HTML5响应式设计  
- **🔗 SSH完美支持**: 无缝集成SSH远程环境
- **⚡ uvx零配置**: 一键安装即开即用
- **🧪 完整测试**: 43个测试用例，质量保证

### v2.x (已废弃)
- 基于tkinter的GUI版本
- SSH环境兼容性问题
- 已完全替换为Web版本

---

## 🤝 贡献指南

### 🛠️ 开发环境
```bash
# 开发者安装
git clone https://github.com/ElemTran/mcp-feedback-pipe.git
cd mcp-feedback-pipe
python -m venv .venv
source .venv/bin/activate
pip install -e .

# 运行测试
pytest

# 代码格式化
black src/ tests/
```

### 📝 提交规范
- 🐛 **fix**: 修复bug
- ✨ **feat**: 新功能
- 📚 **docs**: 文档更新
- 🧪 **test**: 测试相关
- 🔧 **refactor**: 代码重构

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

感谢所有贡献者和社区支持！

**让AI与用户的交互更高效直观！** 🎯