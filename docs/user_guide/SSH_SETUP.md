# 🔒 SSH环境配置指南

专为Windows用户通过SSH连接Linux服务器开发MCP反馈通道而设计。

## 📋 环境概述

- **本地环境**: Windows客户端
- **远程环境**: Linux服务器 (您的开发环境)
- **连接方式**: SSH
- **访问目标**: Web界面 (端口5000)

## 🚀 快速配置

### 方案一：命令行SSH端口转发（推荐）

```bash
# 在Windows命令行或PowerShell中执行
ssh -L 5000:localhost:5000 username@your-server-ip

# 参数说明：
# -L 5000:localhost:5000  将本地5000端口转发到远程5000端口
# username@your-server-ip  您的SSH连接信息
```

### 方案二：使用PuTTY配置端口转发

1. **打开PuTTY配置**
2. **设置SSH隧道**：
   - 进入 `Connection` → `SSH` → `Tunnels`
   - `Source port`: `5000`
   - `Destination`: `localhost:5000`
   - 选择 `Local`
   - 点击 `Add`
3. **保存会话配置**
4. **连接到服务器**

### 方案三：VS Code SSH配置

如果您使用VS Code的Remote SSH插件：

```json
// .ssh/config 文件配置
Host your-server
    HostName your-server-ip
    User your-username
    LocalForward 5000 localhost:5000
    LocalForward 8080 localhost:8080
```

## 🖥️ 启动和访问流程

### 1. 建立SSH连接（端口转发）
```bash
# Windows命令行
ssh -L 5000:localhost:5000 username@your-server-ip
```

### 2. 在服务器上启动MCP服务
```bash
# 在SSH会话中执行
cd /path/to/mcp-feedback-pipe
source .venv/bin/activate
python scripts/start_server.py
```

### 3. 在Windows浏览器中访问
打开浏览器，访问：`http://localhost:5000`

## 🔧 高级配置

### 自定义端口
如果5000端口被占用：

```bash
# 使用8080端口
ssh -L 8080:localhost:8080 username@your-server-ip

# 启动服务时指定端口
export FLASK_PORT=8080
python scripts/start_server.py
```

### 多端口转发
```bash
# 同时转发多个端口
ssh -L 5000:localhost:5000 -L 8080:localhost:8080 username@your-server-ip
```

### 后台运行SSH隧道
```bash
# Windows PowerShell中后台运行
Start-Process ssh -ArgumentList "-L 5000:localhost:5000 username@your-server-ip" -WindowStyle Hidden
```

## 🔍 故障排除

### 问题1：端口已被占用
```bash
# 检查本地端口占用（Windows）
netstat -ano | findstr :5000

# 解决方案：使用其他端口
ssh -L 8080:localhost:5000 username@your-server-ip
# 然后访问 http://localhost:8080
```

### 问题2：SSH连接中断
```bash
# 保持连接活跃
ssh -L 5000:localhost:5000 -o ServerAliveInterval=60 username@your-server-ip
```

### 问题3：防火墙阻止
```bash
# 检查Windows防火墙设置
# 允许SSH客户端通过防火墙
```

### 问题4：浏览器无法访问
1. 确认SSH隧道建立成功
2. 确认远程服务正在运行
3. 尝试访问 `http://127.0.0.1:5000`
4. 检查浏览器代理设置

## 📱 测试连接

### 1. 测试SSH连接
```bash
ssh username@your-server-ip "echo 'SSH连接成功'"
```

### 2. 测试端口转发
```bash
# 建立连接后，在本地测试
curl http://localhost:5000
# 或在浏览器中访问
```

### 3. 测试MCP服务
```bash
# 在服务器上运行测试
python tests/integration/deploy_test.py
```

## 🔄 自动化脚本

### Windows批处理脚本
创建 `start_mcp_dev.bat`：

```batch
@echo off
echo 启动MCP反馈通道开发环境...
echo 正在建立SSH隧道...
start /B ssh -L 5000:localhost:5000 username@your-server-ip
timeout /t 3
echo 请在SSH会话中启动服务：
echo   cd /path/to/mcp-feedback-pipe
echo   source .venv/bin/activate  
echo   python scripts/start_server.py
echo.
echo 然后访问: http://localhost:5000
pause
```

### PowerShell脚本
创建 `start_mcp_dev.ps1`：

```powershell
Write-Host "🚀 启动MCP反馈通道开发环境" -ForegroundColor Green
Write-Host "📡 建立SSH隧道..." -ForegroundColor Yellow

# 启动SSH隧道
Start-Process ssh -ArgumentList "-L 5000:localhost:5000 username@your-server-ip"

Start-Sleep 3

Write-Host "✅ SSH隧道已建立" -ForegroundColor Green
Write-Host "📋 请在SSH会话中执行以下命令:" -ForegroundColor Cyan
Write-Host "   cd /path/to/mcp-feedback-pipe" -ForegroundColor White
Write-Host "   source .venv/bin/activate" -ForegroundColor White
Write-Host "   python scripts/start_server.py" -ForegroundColor White
Write-Host ""
Write-Host "🌐 然后访问: http://localhost:5000" -ForegroundColor Green
```

## 🎯 最佳实践

1. **保持SSH会话活跃**：使用 `ServerAliveInterval` 参数
2. **使用SSH密钥**：避免每次输入密码
3. **配置SSH配置文件**：简化连接命令
4. **使用tmux/screen**：在服务器上保持会话
5. **设置别名**：简化常用命令

## 🔐 安全建议

1. **仅绑定本地**：确保服务只监听 127.0.0.1
2. **使用强密码**：或更好的，使用SSH密钥
3. **定期更新**：保持SSH客户端和服务器端软件更新
4. **监控连接**：注意异常的网络活动

---

**适用环境**: Windows → Linux SSH开发  
**版本**: v3.0.0  
**更新时间**: 2024-12-31 