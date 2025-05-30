# 📋 发布说明

## 🎯 MCP Feedback Collector v3.0.0

### 项目简介
MCP反馈收集器 - 为AI助手提供现代化Web界面的交互式反馈收集功能。已从GUI架构重构为Web架构，完美支持SSH远程环境。

### ✨ 主要特性

#### 🌐 现代化Web界面
- 响应式Web设计，支持所有现代浏览器
- 美观的Bootstrap风格界面
- 无需GUI依赖，完美支持SSH远程环境
- 实时反馈状态显示和进度条

#### 📷 强大的图片功能
- 支持同时选择和提交多张图片
- 支持文件选择和剪贴板粘贴两种方式
- 实时图片预览和信息显示
- 图片格式验证和大小检查
- 每张图片独立管理，批量操作支持

#### 💬 灵活的反馈方式
- 纯文字反馈：多行文本输入
- 纯图片反馈：只提交图片
- 混合反馈：文字+多张图片组合
- 自动时间戳记录和反馈历史

#### 🏗️ 模块化架构
- 关注点分离，代码结构清晰
- 8个专门模块，每个文件<250行
- 前后端分离设计
- 完善的错误处理和日志记录

### 🔧 核心功能

1. **collect_feedback()** - 主要的反馈收集功能
2. **pick_image()** - 简化的图片选择功能  
3. **get_image_info()** - 获取图片详细信息

### 🚀 安装和部署

#### 方式一：直接运行（推荐）
```bash
# 克隆项目
git clone <repository-url>
cd mcp-feedback-collector

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
python -m mcp_feedback_collector.server
```

#### 方式二：使用uvx
```bash
# 安装uvx
pip install uvx

# 配置Claude Desktop
{
  "mcpServers": {
    "mcp-feedback-collector": {
      "command": "uvx",
      "args": ["mcp-feedback-collector"],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "MCP_DIALOG_TIMEOUT": "600",
        "FLASK_PORT": "5000"
      }
    }
  }
}
```

#### SSH环境部署
```bash
# SSH端口转发（本地5000端口映射到远程5000端口）
ssh -L 5000:localhost:5000 user@remote-server

# 在浏览器中访问
http://localhost:5000
```

### 💻 技术栈
- **MCP协议**：FastMCP框架
- **Web框架**：Flask + Jinja2
- **前端**：HTML5 + CSS3 + JavaScript
- **图片处理**：PIL/Pillow
- **数据处理**：Python multipart
- **测试框架**：pytest + coverage

### 🎯 使用场景
- AI助手完成任务后收集用户反馈
- 收集包含图片的详细用户意见
- 获取用户对AI工作的评价和建议
- 收集相关的截图或图片资料
- SSH远程开发环境中的反馈收集

### 📦 项目结构
```
src/mcp_feedback_collector/
├── __init__.py          # 包初始化（24行）
├── server.py           # MCP服务器主程序（120行）
├── app.py              # Flask Web应用（114行）
├── feedback_handler.py # 反馈数据处理（62行）
├── server_manager.py   # 服务器管理（82行）
├── utils.py            # 工具函数（95行）
├── static/             # 静态资源
│   ├── css/           # 样式文件
│   └── js/            # JavaScript文件
└── templates/          # HTML模板
```

### 🧪 测试覆盖
- **单元测试**: 32个测试，100%通过
- **集成测试**: 11个测试，100%通过
- **代码覆盖率**: 65%
- **端到端测试**: 基础覆盖

### 🔄 版本更新

#### v3.0.0 - 架构重构 (2024-12-31)
- 🎉 **重大更新**: 从GUI架构重构为Web架构
- ✅ **SSH兼容**: 完美支持远程SSH环境
- 🏗️ **模块化**: 8个专门模块，关注点分离
- 🧪 **测试完善**: 43个测试用例，65%覆盖率
- 📝 **代码质量**: 所有Python文件<250行

#### v2.0.0 - GUI版本
- 图形用户界面实现
- tkinter + PIL图片处理
- 多线程队列管理

### 🎉 重要改进
这是MCP Feedback Collector的重大架构升级，实现了：
- **SSH环境兼容**: 彻底解决远程开发环境问题
- **模块化设计**: 清晰的架构和代码组织
- **Web原生**: 现代化的Web技术栈
- **测试覆盖**: 完善的自动化测试体系

---

**开发者**: MCP Feedback Collector Team  
**许可证**: MIT License  
**Python要求**: >=3.8  
**核心依赖**: mcp, flask, pillow>=8.0.0  
**版本**: v3.0.0 