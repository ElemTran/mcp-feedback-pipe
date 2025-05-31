# 🔧 MCP反馈通道配置指南

## 📋 配置文件路径

### Cursor编辑器
```
~/.cursor/mcp.json
```

### Claude Desktop
```
~/.config/claude-desktop/claude_desktop_config.json
```

## 📦 示例配置文件

项目包含以下配置文件示例（位于docs目录）：
- `claude_desktop_config_uvx.json` - uvx部署配置示例（推荐）
- `claude_desktop_config_v3.json` - 标准配置示例
- `claude_desktop_config_deploy.json` - 使用部署脚本的配置示例

## 🚀 推荐配置：uvx部署（零配置）

### 优势
- ✅ **零配置**: 无需手动设置虚拟环境和依赖
- ✅ **自动管理**: uvx自动处理Python环境和包管理
- ✅ **隔离安全**: 每个项目独立的运行环境
- ✅ **便携性**: 配置文件简洁，易于分享

### 1. Cursor配置（推荐）
```json
{
  "mcpServers": {
    "mcp-feedback-pipe": {
      "command": "uvx",
      "args": [
        "--from", "/path/to/mcp-feedback-pipe",
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

### 2. Claude Desktop配置（推荐）
```json
{
  "mcpServers": {
    "mcp-feedback-pipe": {
      "command": "uvx",
      "args": [
        "--from", "/path/to/mcp-feedback-pipe",
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

## 🔧 传统配置（备选方案）

<details>
<summary>点击展开传统配置方式</summary>

### 1. Cursor配置（传统）
```json
{
  "mcpServers": {
    "mcp-feedback-pipe": {
      "command": "/path/to/mcp-feedback-pipe/.venv/bin/python",
      "args": [
        "/path/to/mcp-feedback-pipe/src/mcp_feedback_pipe/server.py"
      ],
      "env": {
        "PYTHONPATH": "/path/to/mcp-feedback-pipe/src",
        "PYTHONIOENCODING": "utf-8",
        "MCP_DIALOG_TIMEOUT": "600",
        "MCP_USE_WEB": "true"
      }
    }
  }
}
```

### 2. Claude Desktop配置（传统）
```json
{
  "mcpServers": {
    "mcp-feedback-pipe": {
      "command": "/path/to/mcp-feedback-pipe/.venv/bin/python",
      "args": [
        "/path/to/mcp-feedback-pipe/src/mcp_feedback_pipe/server.py"
      ],
      "env": {
        "PYTHONPATH": "/path/to/mcp-feedback-pipe/src",
        "PYTHONIOENCODING": "utf-8",
        "MCP_DIALOG_TIMEOUT": "600",
        "MCP_USE_WEB": "true"
      }
    }
  }
}
```

</details>

## 🎯 可用的MCP工具

### 1. `collect_feedback`
- **功能**: 收集用户反馈（文字+图片）
- **参数**: 
  - `work_summary`: 工作汇报内容
  - `timeout_seconds`: 超时时间（默认300秒）

### 2. `pick_image` 
- **功能**: 快速图片选择
- **参数**: 无
- **返回**: 选择的图片数据

### 3. `get_image_info_tool`
- **功能**: 获取图片信息
- **参数**: 
  - `image_path`: 图片文件路径

## 🛠️ 安装配置步骤

### uvx方式（推荐）

#### 1. 安装uvx
```bash
pip install uv
```

#### 2. 获取项目
```bash
git clone https://github.com/your-username/mcp-feedback-pipe.git
```

#### 3. 更新配置路径
将配置文件中的 `/path/to/mcp-feedback-pipe` 替换为您的实际项目路径：
```bash
# 例如：
/home/username/mcp-feedback-pipe
```

#### 4. 复制配置文件
```bash
# 对于Cursor
cp docs/claude_desktop_config_uvx.json ~/.cursor/mcp.json

# 对于Claude Desktop
cp docs/claude_desktop_config_uvx.json ~/.config/claude-desktop/claude_desktop_config.json
```

### 传统方式（备选）

<details>
<summary>点击展开传统安装步骤</summary>

#### 1. 创建虚拟环境
```bash
cd /path/to/mcp-feedback-pipe
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows
```

#### 2. 安装依赖
```bash
pip install -r requirements.txt
```

#### 3. 确认虚拟环境
```bash
which python
# 应该指向项目的.venv目录
```

#### 4. 复制配置文件
```bash
# 对于Cursor
cp docs/claude_desktop_config_v3.json ~/.cursor/mcp.json

# 对于Claude Desktop
cp docs/claude_desktop_config_v3.json ~/.config/claude-desktop/claude_desktop_config.json
```

#### 5. 更新配置中的路径
编辑配置文件，确保所有路径指向正确的位置。

</details>

## 🔍 故障排除

### 问题1: "No tools available"
**解决方案**:
1. **uvx方式**: 确认uvx已安装 (`pip install uv`)
2. **传统方式**: 确认虚拟环境路径正确
3. 检查项目路径是否正确
4. 重启编辑器/应用

### 问题2: uvx命令未找到
**解决方案**:
```bash
# 安装uv工具链
pip install uv

# 验证安装
uvx --version
```

### 问题3: 导入错误
**解决方案**:
1. 确认server.py已修复导入问题
2. **uvx方式**: 自动处理依赖，无需手动安装
3. **传统方式**: 检查依赖安装 `pip install mcp flask pillow`

### 问题4: Web界面无法访问
**解决方案**:
1. 在SSH环境中配置端口转发
2. 使用Web服务模式测试: `python scripts/mcp_deploy.py`
3. 检查防火墙设置

## 🚀 测试步骤

### 1. uvx测试（推荐）
```bash
cd /path/to/mcp-feedback-pipe
uvx --from . mcp-feedback-pipe
# 应该启动MCP服务器
```

### 2. 传统测试
```bash
cd /path/to/mcp-feedback-pipe
source .venv/bin/activate
python src/mcp_feedback_pipe/server.py
```

### 3. 在编辑器中测试
- 重启编辑器
- 检查MCP服务器状态（应显示绿色）
- 尝试使用工具

### 4. Web界面测试
```bash
python scripts/mcp_deploy.py
# 选择模式1（Web服务模式）
```

## 📱 SSH环境使用

当在SSH环境中使用时：
1. MCP工具会自动启动Web服务器
2. 系统会显示端口转发指令
3. 在本地浏览器中访问界面
4. 提交反馈后自动返回结果

## 🔄 配置迁移

### 从传统配置迁移到uvx

1. **备份现有配置**
```bash
cp ~/.cursor/mcp.json ~/.cursor/mcp.json.backup
```

2. **安装uvx**
```bash
pip install uv
```

3. **更新配置**
将配置中的:
```json
"command": "/path/to/.venv/bin/python",
"args": ["/path/to/src/mcp_feedback_pipe/server.py"],
"env": {"PYTHONPATH": "/path/to/src", ...}
```

替换为:
```json
"command": "uvx",
"args": ["--from", "/path/to/mcp-feedback-pipe", "mcp-feedback-pipe"],
"env": {...}  // 移除PYTHONPATH
```

4. **测试新配置**
重启编辑器并验证功能正常。

---
**更新时间**: 2024-12-31  
**版本**: v3.0.0 