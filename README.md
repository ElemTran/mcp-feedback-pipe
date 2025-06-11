# 🎯 MCP反馈通道 (MCP Feedback Pipe)


![Version](https://img.shields.io/badge/version-3.0.5-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)
![SSH Compatible](https://img.shields.io/badge/SSH-Compatible-success)
![Markdown](https://img.shields.io/badge/Markdown-Supported-brightgreen)
![Mermaid](https://img.shields.io/badge/Mermaid-Diagrams-blue)


一个基于Flask的现代化Web界面反馈收集工具，专为MCP (Model Context Protocol) 环境设计。从GUI架构完全重构为Web架构，完美支持SSH远程环境和Cursor等现代开发工具。支持Markdown渲染、Mermaid图表、代码高亮等丰富的内容展示功能。

---

## 🆕 开发计划 (v3.0.6) - 开发中

### ✅ **已完成工作**
- **🐛 调试日志清理**: 移除生产环境中的调试日志输出，优化日志级别
- **🧪 测试脚本整合**: 合并 `run_feedback_test.py` 和 `test_mcp_conversion.py` 为统一的 [`tools/run_integrated_test.py`](tools/run_integrated_test.py:1)
- **🔧 代码质量改进**: 修复多个小型bug，提升代码稳定性

### 🎯 **重点修复计划**
- **⚡ 界面性能提升**: 解决控件渲染速度慢的问题，添加缓存机制
- **⏱️ 反馈时间延长**: 扩展用户界面反馈收集的时间窗口
- **🔗 SSH连接简化**: 简化SSH端口转发配置，提供一键设置方案
- **🔄 多客户端阻塞修复**: 解决多个客户端链接MCP服务器时导致的阻塞问题，实现并发连接支持，服务器重启结束所有客户端的对话。
- **🖼️ 图片上传修复**: 解决图片上传时因Base64编码处理不当导致的TypeError问题
- **🔧 编码问题解决**: 修复Windows环境下emoji字符显示的GBK编码错误

### 📋 **其他计划改进**
- **🎨 加载动画**: 添加加载进度指示器，改善等待体验
- **📱 移动端优化**: 完善响应式设计，提升移动设备使用体验
- **🔄 错误重试**: 实现网络错误自动重试机制
- **⌨️ 快捷键支持**: 添加键盘快捷键，提高操作效率

---

## 🆕 最新发布 (v3.0.5)

### 🐛 **关键修复**
- **⏰ 超时显示修复**: 修复120秒超时显示为300秒（5分钟）的问题，现在正确显示为2分钟
- **🎯 参数传递修复**: 修复ServerManager向FeedbackApp传递参数顺序错误导致的timeout_seconds未正确传递问题
- **🎨 界面布局修复**: 修复调整大小按钮对齐问题，现在右对齐显示
- **📝 模板变量修复**: 修复HTML模板中suggest变量名错误，确保建议选项正确显示

### ✨ **功能增强**
- **🔧 参数处理优化**: 使用关键字参数传递，避免参数顺序错误
- **🎯 建议选项功能**: 确认建议选项列表正确显示和交互
- **📱 用户体验改进**: 界面布局优化，按钮对齐，响应式设计完善
- **🎨 界面重构**: 紧凑化布局、动态大小调整、图片上传体验优化
- **📝 内容渲染**: Markdown语法支持、Mermaid图表渲染、代码语法高亮

### 🛠️ **技术改进**
- **✅ 参数类型验证**: suggest 参数使用标准数组格式 `List[str]`
- **🧪 功能测试**: 通过实际测试验证所有功能正常
- **📋 代码质量**: 确保参数处理符合最佳实践
- **📚 文档完善**: 新增TODO.md记录性能优化和待办事项
- **🚀 发布管理**: 成功发布v3.0.5到PyPI，解决依赖问题

---

## 🚀 快速开始

### ⭐ 推荐：uvx一键安装

```bash
# ✅ PyPI正式发布，零配置一键运行
uvx mcp-feedback-pipe
```

> **🎉 发布状态**: 已正式发布到PyPI！使用全新名称`mcp-feedback-pipe`，无冲突，即装即用

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
python tools/start_server.py
```

---

## 🎯 核心特性

### ✨ 用户体验
- **🌐 现代Web界面**: 基于Flask + HTML5的响应式设计
- **📱 多设备支持**: 手机、平板、电脑完美适配
- **🎨 优雅交互**: 实时反馈、动画效果、直观操作
- **📝 丰富内容**: Markdown渲染、Mermaid图表、代码高亮

### 🔧 技术架构
- **🏗️ 模块化设计**: 8个核心模块，关注点分离
- **📊 实时监控**: 服务状态、端口管理、进程监控

### 🌍 环境兼容
- **🔗 SSH远程支持**: 完美支持SSH端口转发
- **🎯 Cursor集成**: 无缝集成Cursor MCP工具链
- **⚡ uvx零配置**: 一键安装，即开即用

---

## 🛠️ Cursor MCP配置

### ⭐ 推荐配置 (PyPI版本)
```json
{
  "mcpServers": {
    "mcp-feedback-pipe": {
      "command": "uvx",
      "args": ["mcp-feedback-pipe"],
      "env": {
        "MCP_DIALOG_TIMEOUT": "600",
        "MCP_USE_WEB": "true",
        // "MCP_FEEDBACK_PREFERRED_PORT": "8765", // 可选：用户可自定义Web服务首选端口
        // "MCP_FEEDBACK_LOCAL_FORWARD_PORT": "8888"  // 可选：用户可自定义本地SSH转发端口
      }
    }
  }
}
```

> **✅ 零配置**: 已移除编码环境变量依赖，代码自动处理编码问题

### 备选配置 (本地开发)
```json
{
  "mcpServers": {
    "mcp-feedback-pipe-dev": {
      "command": ".venv/bin/python",
      "args": ["-m", "mcp_feedback_pipe.server"],
      "env": {
        "PYTHONPATH": "src",
        "MCP_USE_WEB": "true"
      }
    }
  }
}
```
Windows下使用: "/path/to/mcp-feedback-pipe/.venv/Scripts/python",
---

## 🔗 SSH环境部署

### Web服务端口行为

`mcp-feedback-pipe` 的Web服务（由 `collect_feedback` 和 `pick_image` 工具启动）具有以下端口选择机制：

1.  **首选固定端口**：服务会优先尝试在预定义的固定端口上运行。
    *   此端口通过环境变量 `MCP_FEEDBACK_PREFERRED_PORT` 配置。
    *   默认值为 `8765`。
2.  **动态回退**：如果首选端口（例如 `8765`）已被占用，系统将自动查找并使用一个当前空闲的端口。
    *   服务实际监听的端口号（无论是首选端口还是动态分配的端口）都会在启动时于终端输出中显示。请留意此输出以获取正确的端口号。

### SSH端口转发指南

要在SSH环境下访问远程服务器上运行的Web服务，您通常需要设置端口转发。这将把您本地计算机上的一个端口映射到远程服务器上Web服务正在监听的端口。

**推荐的本地转发端口**：我们建议使用本地端口 `8888` 进行转发。此推荐端口可以通过环境变量 `MCP_FEEDBACK_LOCAL_FORWARD_PORT` 进行配置，其默认值为 `8888`。

**SSH本地端口转发命令示例**：

打开您的本地终端，使用以下命令格式：

```bash
ssh -L <本地转发端口>:127.0.0.1:<远程服务实际监听端口> your_user@your_remote_server_ip
```

**请务必替换以下占位符**：
*   `<本地转发端口>`：替换为您希望在本地计算机上使用的端口。如果遵循建议且未修改环境变量，则为 `8888`。
*   `<远程服务实际监听端口>`：替换为远程服务器上 `mcp-feedback-pipe` 服务实际监听的端口号。**请查看服务启动时的终端输出获取此端口号** (可能是默认的 `8765` 或一个动态分配的端口)。
*   `your_user@your_remote_server_ip`：替换为您的远程服务器用户名和IP地址或主机名。

**示例**：

1.  如果远程服务运行在首选端口 `8765`，并且您使用推荐的本地端口 `8888`：
    ```bash
    ssh -L 8888:127.0.0.1:8765 your_user@your_remote_server_ip
    ```
2.  如果远程服务因端口占用而运行在动态分配的端口（例如 `12345`），并且您使用推荐的本地端口 `8888`：
    ```bash
    ssh -L 8888:127.0.0.1:12345 your_user@your_remote_server_ip
    ```

**访问Web服务**：

成功建立SSH连接并设置端口转发后，在您本地计算机的浏览器中打开以下URL：

```
http://127.0.0.1:<本地转发端口>/
```
例如，如果使用本地端口 `8888`，则访问 `http://127.0.0.1:8888/`。

### 💡 VSCode Remote SSH 用户特别说明

如果您正在使用VSCode的**Remote SSH**扩展连接到远程服务器并在此环境中运行 `mcp-feedback-pipe`：

*   **自动端口转发**：VSCode的Remote SSH扩展通常会自动检测到在远程服务器 `127.0.0.1` (localhost) 上启动的服务，并将其端口转发到您的本地计算机。
*   **无需手动命令**：在这种情况下，您可能**不需要**手动执行上述 `ssh -L ...` 命令。
*   **访问方式**：您可以直接尝试在本地浏览器中访问 `http://localhost:<远程服务实际监听端口>` 或留意VSCode右下角弹出的端口转发通知，它会提供一个可直接点击的链接。

请检查VSCode的“端口”视图（通常在底部面板的“终端”标签页旁边）查看已自动转发的端口。

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
  - `work_summary`: AI工作汇报内容
  - `timeout_seconds`: 超时时间（默认300秒）
  - `suggest`: 建议选项列表，格式如：`["选项1", "选项2", "选项3"]` ✨**已验证**
- **`pick_image`**: 图片选择和上传功能
- **`get_image_info_tool`**: 获取图片详细信息

### 💡 使用示例
```python
# 在Cursor中调用collect_feedback工具
# 1. 基础反馈收集
collect_feedback(work_summary="任务完成情况汇报")

# 2. 带建议选项的反馈收集 ✨新功能验证
collect_feedback(
    work_summary="功能开发完成，请提供反馈",
    suggest=["功能正常", "需要优化", "有问题", "建议修改"]
)

# 3. 自定义超时时间
collect_feedback(
    work_summary="长时间任务完成",
    timeout_seconds=600,
    suggest=["满意", "需要调整", "继续优化"]
)
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
├── tools/                      # 实用脚本
├── tests/                        # 测试套件
└── docs/                         # 完整文档
```

### 🧪 质量保证
- **单元测试**: 32个测试用例
- **集成测试**: 11个测试用例
- **代码覆盖率**: 65%
- **代码规范**: 每个文件<250行
- **集成测试工具**: [`tools/run_integrated_test.py`](tools/run_integrated_test.py:1) - 统一的测试脚本，支持多种测试模式

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

### v3.0.6 (开发中)
- **🎯 重点修复**: 图片上传优化、界面性能提升、反馈时间延长、SSH连接简化
- **🔧 编码问题**: 修复Windows环境emoji字符显示问题，零配置部署
- **✨ 体验增强**: 加载动画、移动端优化、错误重试、快捷键支持
- **📋 计划状态**: 正在开发中，预计解决多个用户反馈的核心问题

### v3.0.5 (当前版本)
- **🐛 关键修复**: 修复120秒超时显示问题、参数传递错误、界面布局问题
- **✨ 功能增强**: 优化参数处理、改善用户体验、完善建议选项功能
- **🛠️ 技术改进**: 使用关键字参数、完善功能测试、修复模板变量
- **📚 文档完善**: 新增TODO.md、完善使用示例和参数说明
- **🚀 发布管理**: 成功发布到PyPI，解决依赖问题

### v3.0.1
- **✅ suggest参数验证**: 确认数组类型参数处理正确
- **🎯 功能测试完善**: 实际验证建议选项功能
- **🌐 界面优化**: 前端交互体验改进
- **🎨 界面重构**: 紧凑化布局、动态调整、上传体验优化
- **📝 内容渲染**: Markdown语法、Mermaid图表、代码高亮支持

### v3.0.0 (重大版本)
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

# 集成测试（推荐）
python tools/run_integrated_test.py --mode all

# 代码格式化
black src/ tests/
```

### 🧪 测试工具使用

项目提供了统一的集成测试脚本 [`tools/run_integrated_test.py`](tools/run_integrated_test.py:1)，支持多种测试模式：

```bash
# 基础反馈收集测试
python tools/run_integrated_test.py --mode feedback

# MCP转换流程测试
python tools/run_integrated_test.py --mode mcp_conversion

# 运行所有集成测试
python tools/run_integrated_test.py --mode all

# 非调试模式运行
python tools/run_integrated_test.py --mode feedback --no-debug
```

**测试模式说明**：
- `feedback`: 测试基础反馈收集功能，包括文本和图片上传
- `mcp_conversion`: 测试MCP协议转换功能
- `all`: 依次运行所有测试模式

**命令行选项**：
- `--mode`: 选择测试模式（默认：`feedback`）
- `--no-debug`: 关闭Flask调试模式
- `--use-reloader`: 启用Flask重新加载器（不推荐在测试中使用）

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