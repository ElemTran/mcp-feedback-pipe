# 📦 MCP反馈通道 - 发布指南

本文档说明如何将MCP反馈通道项目发布到PyPI，以支持uvx部署。

## 🎯 发布目标

通过将项目发布到PyPI，用户可以使用以下方式安装和使用：

```bash
# 直接运行（推荐）
uvx mcp-feedback-pipe

# 或者先安装再运行
pip install mcp-feedback-pipe
mcp-feedback-pipe
```

## 🛠️ 准备发布

### 1. 确认项目结构

项目已经配置好了uvx支持：

```
mcp-feedback-pipe/
├── src/
│   └── mcp_feedback_pipe/
│       ├── __init__.py
│       ├── server.py          # 包含main()入口点
│       └── ...
├── pyproject.toml             # 包含[project.scripts]配置
├── README.md
└── requirements.txt
```

### 2. 检查pyproject.toml配置

关键配置项：

```toml
[project.scripts]
mcp-feedback-pipe = "mcp_feedback_pipe.server:main"
```

这配置了uvx可以调用的命令行入口点。

### 3. 更新版本和依赖

在`pyproject.toml`中：
- 更新`version = "3.0.0"`
- 确认依赖项正确
- 更新项目URL

## 🚀 发布流程

### 方法一：使用uv构建和发布

```bash
# 1. 安装uv（如果没有）
pip install uv

# 2. 构建包
uv build

# 3. 发布到PyPI（需要API token）
uv publish --token pypi-your-token-here
```

### 方法二：使用传统工具

```bash
# 1. 安装构建工具
pip install build twine

# 2. 清理旧构建
rm -rf dist/

# 3. 构建包
python -m build

# 4. 检查包
twine check dist/*

# 5. 发布到TestPyPI（测试）
twine upload --repository testpypi dist/*

# 6. 发布到PyPI（正式）
twine upload dist/*
```

## 🔧 PyPI账户设置

### 1. 注册PyPI账户
- 访问 https://pypi.org/account/register/
- 创建账户并验证邮箱

### 2. 创建API Token
- 登录PyPI，访问 https://pypi.org/manage/account/token/
- 创建新token，范围选择"Entire account"
- 保存token（格式：`pypi-...`）

### 3. 配置认证
创建`~/.pypirc`文件：

```ini
[distutils]
index-servers = pypi

[pypi]
username = __token__
password = pypi-your-token-here
```

## ✅ 发布后验证

### 1. 测试uvx安装
```bash
# 卸载本地版本（如果有）
pip uninstall mcp-feedback-pipe

# 使用uvx测试
uvx mcp-feedback-pipe

# 应该启动MCP服务器
```

### 2. 测试MCP配置
创建测试配置文件：

```json
{
  "mcpServers": {
    "mcp-feedback-pipe": {
      "command": "uvx",
      "args": ["mcp-feedback-pipe"],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "MCP_DIALOG_TIMEOUT": "600",
        "MCP_USE_WEB": "true"
      }
    }
  }
}
```

### 3. 检查PyPI页面
- 访问 https://pypi.org/project/mcp-feedback-pipe/
- 确认项目信息正确
- 检查README渲染

## 🔄 版本更新流程

### 1. 更新代码
- 修复bug或添加新功能
- 更新文档

### 2. 更新版本
在`pyproject.toml`中更新版本号：
```toml
version = "3.0.1"  # 遵循语义版本控制
```

### 3. 更新RELEASE_NOTES.md
记录版本变更：
```markdown
### v3.0.1 (2024-12-31)
- 🐛 修复uvx部署问题
- 📖 更新文档
```

### 4. 重新发布
```bash
uv build
uv publish --token pypi-your-token-here
```

## 🚨 注意事项

### 安全考虑
- ⚠️ **API Token安全**: 不要将PyPI token提交到代码仓库
- 🔒 **权限最小化**: 为每个项目创建独立的token
- 🔄 **定期轮换**: 定期更新API token

### 包命名
- ✅ **唯一性**: 确保包名在PyPI上唯一
- 📝 **描述性**: 包名应该清楚表达功能
- 🔗 **一致性**: 与GitHub仓库名保持一致

### 依赖管理
- 📌 **版本固定**: 重要依赖使用版本范围
- 🧪 **测试兼容性**: 测试不同Python版本
- 📊 **监控依赖**: 定期检查依赖更新

## 📊 发布清单

- [ ] 更新版本号
- [ ] 更新README.md
- [ ] 更新RELEASE_NOTES.md
- [ ] 运行测试套件
- [ ] 检查pyproject.toml配置
- [ ] 本地测试脚本入口点
- [ ] 构建包 (`uv build`)
- [ ] 检查构建产物
- [ ] 发布到PyPI
- [ ] 测试uvx安装
- [ ] 更新文档
- [ ] 标记Git版本

---

**更新时间**: 2024-12-31  
**版本**: v3.0.0 