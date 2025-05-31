# 🚀 MCP反馈通道部署指南

本指南将帮助您在各种环境中部署MCP反馈通道v3.0。

## 📋 部署方式对比

| 部署方式 | 复杂度 | 推荐指数 | 适用场景 |
|---------|-------|---------|----------|
| **uvx部署** | ⭐ | ⭐⭐⭐⭐⭐ | 推荐所有用户 |
| 传统部署 | ⭐⭐⭐ | ⭐⭐⭐ | 特殊需求/开发者 |
| Docker部署 | ⭐⭐ | ⭐⭐⭐⭐ | 容器化环境 |

## 🌟 方式一：uvx部署（推荐）

### 优势
- ✅ **零配置**: 无需手动创建虚拟环境
- ✅ **自动依赖管理**: uvx自动解析和安装所有依赖
- ✅ **环境隔离**: 每个项目独立运行环境
- ✅ **便携性**: 配置文件简洁，易于分享
- ✅ **更新方便**: 支持自动更新

### 前置要求
- Python 3.8+
- uv工具链

### 1. 安装uv工具链
```bash
# 使用pip安装
pip install uv

# 验证安装
uvx --version
```

### 2. 获取项目代码
```bash
git clone https://github.com/your-username/mcp-feedback-pipe.git
cd mcp-feedback-pipe
```

### 3. 测试uvx部署
```bash
# 测试运行
uvx --from . mcp-feedback-pipe

# 验证输出类似：
# MCP反馈通道 v3.0 启动成功...
# 等待来自MCP客户端的连接...
```

### 4. 配置MCP客户端

#### Cursor配置 (`~/.cursor/mcp.json`)
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

#### Claude Desktop配置 (`~/.config/claude-desktop/claude_desktop_config.json`)
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

### 5. 重启客户端
重启Cursor/Claude Desktop，验证MCP工具可用。

## 🔧 方式二：传统部署（备选）

<details>
<summary>点击展开传统部署方式</summary>

### 前置要求
- Python 3.8+
- pip包管理器
- 虚拟环境支持

### 1. 克隆项目
```bash
git clone https://github.com/your-username/mcp-feedback-pipe.git
cd mcp-feedback-pipe
```

### 2. 创建虚拟环境
```bash
# Linux/Mac
python -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 验证安装
```bash
python src/mcp_feedback_pipe/server.py
```

### 5. 配置MCP客户端

#### Cursor配置
```json
{
  "mcpServers": {
    "mcp-feedback-pipe": {
      "command": "/absolute/path/to/.venv/bin/python",
      "args": [
        "/absolute/path/to/src/mcp_feedback_pipe/server.py"
      ],
      "env": {
        "PYTHONPATH": "/absolute/path/to/src",
        "PYTHONIOENCODING": "utf-8",
        "MCP_DIALOG_TIMEOUT": "600",
        "MCP_USE_WEB": "true"
      }
    }
  }
}
```

### 注意事项
- 必须使用绝对路径
- 需要手动管理虚拟环境
- PYTHONPATH配置容易出错

</details>

## 🐳 方式三：Docker部署

### 1. 构建Docker镜像
```bash
docker build -t mcp-feedback-pipe:v3.0 .
```

### 2. 运行容器
```bash
docker run -d \
  --name mcp-feedback-pipe \
  -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  mcp-feedback-pipe:v3.0
```

### 3. MCP配置
```json
{
  "mcpServers": {
    "mcp-feedback-pipe": {
      "command": "docker",
      "args": [
        "exec", "mcp-feedback-pipe",
        "python", "/app/src/mcp_feedback_pipe/server.py"
      ],
      "env": {
        "MCP_USE_WEB": "true"
      }
    }
  }
}
```

## 🔧 高级配置

### 部署脚本使用
项目提供了智能部署脚本：

```bash
python scripts/mcp_deploy.py
```

支持三种模式：
1. **Web服务模式** - 仅启动Web界面（调试用）
2. **MCP服务模式** - 启动MCP服务器
3. **混合模式** - 同时启动Web和MCP服务

### 环境变量配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `MCP_DIALOG_TIMEOUT` | 300 | 反馈收集超时时间（秒） |
| `MCP_USE_WEB` | true | 强制使用Web界面 |
| `PYTHONIOENCODING` | utf-8 | 字符编码设置 |
| `AUTO_MODE` | - | 部署脚本自动模式 |

## 🌐 SSH环境部署

### 1. 服务器端配置
```bash
# 在服务器上部署（推荐uvx方式）
uvx --from /path/to/project mcp-feedback-pipe
```

### 2. 本地端口转发
```bash
# 方式1：本地端口转发（推荐）
ssh -L 8080:127.0.0.1:8080 username@server-ip

# 方式2：动态端口转发
ssh -D 1080 username@server-ip
```

### 3. VS Code Remote配置
```json
// .vscode/settings.json
{
  "remote.SSH.localServerDownload": "always",
  "remote.SSH.enableDynamicForwarding": true
}
```

详见：[SSH配置指南](SSH_SETUP.md)

## 🧪 部署验证

### 1. 基础功能测试
```bash
# uvx方式
uvx --from . mcp-feedback-pipe

# 传统方式
source .venv/bin/activate
python src/mcp_feedback_pipe/server.py
```

### 2. Web界面测试
```bash
python scripts/mcp_deploy.py
# 选择模式1：Web服务模式
# 访问显示的URL
```

### 3. MCP集成测试
- 重启MCP客户端
- 检查工具是否可用：
  - `collect_feedback`
  - `pick_image`
  - `get_image_info_tool`

### 4. SSH环境测试
```bash
# 在SSH环境中测试端口转发
curl http://127.0.0.1:8080/
```

## 🛠️ 故障排除

### uvx相关问题

#### 问题1: uvx命令未找到
```bash
# 解决方案
pip install uv
export PATH="$HOME/.local/bin:$PATH"
```

#### 问题2: 依赖解析失败
```bash
# 清除uvx缓存
uvx cache clean

# 重新运行
uvx --from . mcp-feedback-pipe
```

### 传统部署问题

#### 问题1: 虚拟环境问题
```bash
# 重新创建虚拟环境
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### 问题2: 路径问题
```bash
# 获取绝对路径
pwd
which python
```

### Web界面问题

#### 问题1: 端口被占用
```bash
# 检查端口占用
netstat -tlnp | grep :8080

# 停止冲突进程
pkill -f "mcp_feedback_pipe"
```

#### 问题2: 浏览器无法访问
- 检查防火墙设置
- 确认端口转发配置
- 验证IP地址绑定

## 📦 生产环境部署

### 1. 系统服务配置
```ini
# /etc/systemd/system/mcp-feedback-pipe.service
[Unit]
Description=MCP Feedback Collector
After=network.target

[Service]
Type=simple
User=mcp-user
WorkingDirectory=/opt/mcp-feedback-pipe
ExecStart=/usr/local/bin/uvx --from /opt/mcp-feedback-pipe mcp-feedback-pipe
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. 启动服务
```bash
sudo systemctl enable mcp-feedback-pipe
sudo systemctl start mcp-feedback-pipe
sudo systemctl status mcp-feedback-pipe
```

### 3. 反向代理配置
```nginx
# /etc/nginx/sites-available/mcp-feedback-pipe
server {
    listen 80;
    server_name mcp.yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 性能优化

### 1. 内存使用优化
- 使用uvx自动管理虚拟环境
- 配置合理的超时时间
- 定期清理临时文件

### 2. 网络优化
- 配置适当的端口转发
- 使用本地缓存
- 优化图片传输格式

### 3. 并发处理
- Web服务器支持多并发
- 异步文件上传
- 智能超时管理

## 🔐 安全考虑

### 1. 网络安全
- 仅绑定到127.0.0.1（本地）
- SSH隧道加密传输
- 禁用外部直接访问

### 2. 文件安全
- 限制上传文件类型
- 文件大小限制
- 临时文件自动清理

### 3. 权限控制
- 最小权限原则
- 虚拟环境隔离
- 用户权限分离

---

**更新时间**: 2024-12-31  
**版本**: v3.0.0

## 🎯 部署总结

- **首选方案**: uvx部署（零配置，自动管理）
- **备选方案**: 传统部署（开发者/特殊需求）
- **生产环境**: Docker + 系统服务
- **SSH环境**: uvx + 端口转发

选择适合您环境的部署方式，开始使用MCP反馈通道吧！