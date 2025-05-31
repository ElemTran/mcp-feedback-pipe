# SSH远程连接和手机使用指南

## 🔗 SSH远程连接使用

### 1. 基本SSH端口转发

当您通过SSH连接到远程服务器时，需要设置端口转发来访问Web界面：

```bash
# 方法1: SSH连接时直接设置端口转发
ssh -L 5000:127.0.0.1:5000 user@remote-server

# 方法2: 动态端口转发（推荐）
ssh -L 8080:127.0.0.1:5000 user@remote-server
```

### 2. 使用mcp-feedback-pipe-dev进行测试

如果您需要使用开发版本进行测试：

```bash
# 1. 克隆开发版本
git clone https://github.com/ElemTran/mcp-feedback-pipe.git
cd mcp-feedback-pipe

# 2. 安装开发依赖
pip install -e .

# 3. 直接运行开发版本
python -m mcp_feedback_pipe.server

# 4. 或者使用uvx运行本地版本
uvx --from . mcp-feedback-pipe
```

### 3. SSH配置文件设置

在 `~/.ssh/config` 中添加配置：

```
Host myserver
    HostName your-server-ip
    User your-username
    LocalForward 5000 127.0.0.1:5000
    LocalForward 5001 127.0.0.1:5001
    LocalForward 5002 127.0.0.1:5002
```

这样每次连接时会自动设置端口转发。

## 📱 手机使用MCP服务

### 1. 通过SSH隧道访问

**步骤1: 设置SSH隧道**
```bash
# 在您的本地机器上设置SSH隧道
ssh -L 0.0.0.0:8080:127.0.0.1:5000 user@remote-server
```

**步骤2: 手机访问**
- 确保手机和电脑在同一网络
- 在手机浏览器中访问: `http://your-computer-ip:8080`

### 2. 使用Termux (Android)

**安装Termux:**
```bash
# 在Termux中安装Python和SSH
pkg update && pkg upgrade
pkg install python openssh

# 安装mcp-feedback-pipe
pip install mcp-feedback-pipe

# 设置SSH隧道到远程服务器
ssh -L 5000:127.0.0.1:5000 user@remote-server
```

**在另一个Termux会话中:**
```bash
# 启动MCP服务
uvx mcp-feedback-pipe
```

### 3. 使用iSH (iOS)

**在iSH中:**
```bash
# 安装Python和依赖
apk add python3 py3-pip openssh-client

# 安装mcp-feedback-pipe
pip install mcp-feedback-pipe

# 连接到远程服务器
ssh -L 5000:127.0.0.1:5000 user@remote-server
```

### 4. 云服务器方案

**使用云服务器作为中转:**

```bash
# 在云服务器上安装
pip install mcp-feedback-pipe

# 启动服务（绑定到所有接口，注意安全）
python -c "
from mcp_feedback_pipe.server_manager import ServerManager
sm = ServerManager()
port = sm.start_server('测试连接', 300)
print(f'访问地址: http://your-cloud-server-ip:{port}')
sm.wait_for_feedback(300)
"
```

**安全注意事项:**
- 只在可信网络环境下使用
- 考虑使用VPN或防火墙限制访问
- 使用完毕后及时关闭服务

## 🛠️ 故障排除

### 1. 端口被占用
```bash
# 查找占用端口的进程
lsof -i :5000
netstat -tulpn | grep 5000

# 杀死占用进程
kill -9 <PID>
```

### 2. SSH连接问题
```bash
# 检查SSH连接状态
ssh -v user@remote-server

# 测试端口转发
curl http://127.0.0.1:5000/ping
```

### 3. 防火墙问题
```bash
# Ubuntu/Debian
sudo ufw allow 5000

# CentOS/RHEL
sudo firewall-cmd --add-port=5000/tcp --permanent
sudo firewall-cmd --reload
```

## 📋 最佳实践

### 1. 安全建议
- 使用SSH密钥认证而非密码
- 定期更新SSH配置
- 限制端口转发的IP范围
- 使用VPN进行远程访问

### 2. 性能优化
- 使用压缩: `ssh -C -L 5000:127.0.0.1:5000 user@server`
- 保持连接: `ssh -o ServerAliveInterval=60`
- 多路复用: `ssh -o ControlMaster=auto`

### 3. 开发调试
```bash
# 启用详细日志
export PYTHONPATH=/path/to/mcp-feedback-pipe/src
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from mcp_feedback_pipe import collect_feedback
collect_feedback('调试测试', 300)
"
```

## 🔧 高级配置

### 1. 自定义端口范围
```python
# 在代码中指定端口范围
from mcp_feedback_pipe.server_manager import ServerManager

class CustomServerManager(ServerManager):
    def find_free_port(self):
        # 在特定范围内查找端口
        for port in range(8000, 8100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', port))
                    return port
            except OSError:
                continue
        raise Exception("无可用端口")
```

### 2. 多设备同时访问
```bash
# 启动多个实例
uvx mcp-feedback-pipe &  # 端口5000
uvx mcp-feedback-pipe &  # 端口5001
uvx mcp-feedback-pipe &  # 端口5002
```

这样您就可以在SSH环境和手机上顺利使用MCP反馈通道了！ 