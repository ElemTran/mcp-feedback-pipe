#!/usr/bin/env python3
"""
SSH配置助手脚本
自动生成SSH配置和连接命令
"""
import os
import sys
import subprocess
from pathlib import Path

def get_user_input():
    """获取用户输入的SSH连接信息"""
    print("🔒 SSH配置助手")
    print("=" * 30)
    
    # 获取服务器信息
    server_ip = input("请输入服务器IP地址: ").strip()
    username = input("请输入SSH用户名: ").strip()
    
    # 获取端口配置
    print("\n端口配置:")
    local_port = input("本地端口 (默认5000): ").strip() or "5000"
    remote_port = input("远程端口 (默认5000): ").strip() or "5000"
    
    # 验证输入
    if not server_ip or not username:
        print("❌ 服务器IP和用户名不能为空！")
        return None
        
    return {
        'server_ip': server_ip,
        'username': username,
        'local_port': local_port,
        'remote_port': remote_port
    }

def generate_ssh_commands(config):
    """生成SSH连接命令"""
    commands = {}
    
    # 基本SSH连接命令
    commands['basic'] = f"ssh {config['username']}@{config['server_ip']}"
    
    # 带端口转发的SSH命令
    commands['port_forward'] = f"ssh -L {config['local_port']}:localhost:{config['remote_port']} {config['username']}@{config['server_ip']}"
    
    # 保持连接活跃的命令
    commands['keep_alive'] = f"ssh -L {config['local_port']}:localhost:{config['remote_port']} -o ServerAliveInterval=60 {config['username']}@{config['server_ip']}"
    
    # PowerShell后台运行命令
    commands['powershell_bg'] = f'Start-Process ssh -ArgumentList "-L {config["local_port"]}:localhost:{config["remote_port"]} {config["username"]}@{config["server_ip"]}" -WindowStyle Hidden'
    
    return commands

def generate_ssh_config(config):
    """生成SSH配置文件内容"""
    ssh_config = f"""# MCP反馈通道SSH配置
Host mcp-server
    HostName {config['server_ip']}
    User {config['username']}
    LocalForward {config['local_port']} localhost:{config['remote_port']}
    ServerAliveInterval 60
    ServerAliveCountMax 3
    # 可选：使用SSH密钥认证
    # IdentityFile ~/.ssh/id_rsa
"""
    return ssh_config

def create_batch_script(config):
    """创建Windows批处理脚本"""
    batch_content = f"""@echo off
REM MCP反馈通道SSH连接脚本
echo 🚀 启动MCP反馈通道开发环境
echo 📡 建立SSH隧道到 {config['server_ip']}...
echo.

REM 启动SSH端口转发
ssh -L {config['local_port']}:localhost:{config['remote_port']} {config['username']}@{config['server_ip']}

pause
"""
    return batch_content

def create_powershell_script(config):
    """创建PowerShell脚本"""
    ps_content = f"""# MCP反馈通道SSH连接脚本
Write-Host "🚀 启动MCP反馈通道开发环境" -ForegroundColor Green
Write-Host "📡 建立SSH隧道到 {config['server_ip']}..." -ForegroundColor Yellow
Write-Host ""

# 启动SSH端口转发
$sshArgs = "-L {config['local_port']}:localhost:{config['remote_port']} {config['username']}@{config['server_ip']}"
Write-Host "执行命令: ssh $sshArgs" -ForegroundColor Cyan
Write-Host ""

# 可选：后台启动
# Start-Process ssh -ArgumentList $sshArgs -WindowStyle Hidden

# 前台启动（推荐用于首次连接）
ssh {config['username']}@{config['server_ip']} -L {config['local_port']}:localhost:{config['remote_port']}
"""
    return ps_content

def save_scripts(config, scripts_dir="ssh_scripts"):
    """保存生成的脚本到文件"""
    scripts_path = Path(scripts_dir)
    scripts_path.mkdir(exist_ok=True)
    
    saved_files = []
    
    # 保存SSH配置
    ssh_config_content = generate_ssh_config(config)
    ssh_config_file = scripts_path / "ssh_config"
    with open(ssh_config_file, 'w', encoding='utf-8') as f:
        f.write(ssh_config_content)
    saved_files.append(str(ssh_config_file))
    
    # 保存批处理脚本
    batch_content = create_batch_script(config)
    batch_file = scripts_path / "connect_mcp.bat"
    with open(batch_file, 'w', encoding='utf-8') as f:
        f.write(batch_content)
    saved_files.append(str(batch_file))
    
    # 保存PowerShell脚本
    ps_content = create_powershell_script(config)
    ps_file = scripts_path / "connect_mcp.ps1"
    with open(ps_file, 'w', encoding='utf-8') as f:
        f.write(ps_content)
    saved_files.append(str(ps_file))
    
    return saved_files

def test_connection(config):
    """测试SSH连接"""
    print(f"\n🔍 测试SSH连接到 {config['server_ip']}...")
    
    test_cmd = f"ssh -o ConnectTimeout=10 -o BatchMode=yes {config['username']}@{config['server_ip']} echo 'SSH连接测试成功'"
    
    try:
        result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            print("✅ SSH连接测试成功！")
            return True
        else:
            print(f"❌ SSH连接测试失败: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ SSH连接超时")
        return False
    except Exception as e:
        print(f"❌ 连接测试出错: {e}")
        return False

def main():
    """主函数"""
    print("🔧 MCP反馈通道SSH配置助手")
    print("=" * 40)
    
    # 获取用户输入
    config = get_user_input()
    if not config:
        return
    
    # 生成命令
    commands = generate_ssh_commands(config)
    
    print(f"\n📋 生成的SSH命令:")
    print("=" * 30)
    print(f"🔗 基本连接:")
    print(f"   {commands['basic']}")
    print(f"📡 端口转发:")
    print(f"   {commands['port_forward']}")
    print(f"⏰ 保持连接:")
    print(f"   {commands['keep_alive']}")
    
    # 询问是否保存脚本
    save_scripts_choice = input("\n💾 是否保存配置脚本? (y/N): ").strip().lower()
    if save_scripts_choice in ['y', 'yes', '是']:
        try:
            saved_files = save_scripts(config)
            print(f"\n✅ 脚本已保存:")
            for file in saved_files:
                print(f"   📄 {file}")
        except Exception as e:
            print(f"❌ 保存脚本失败: {e}")
    
    # 询问是否测试连接
    test_choice = input("\n🔍 是否测试SSH连接? (y/N): ").strip().lower()
    if test_choice in ['y', 'yes', '是']:
        test_connection(config)
    
    print(f"\n🎯 使用说明:")
    print(f"1. 在Windows命令行或PowerShell中执行:")
    print(f"   {commands['port_forward']}")
    print(f"2. 连接成功后，在SSH会话中启动MCP服务:")
    print(f"   cd /path/to/mcp-feedback-pipe")
    print(f"   source .venv/bin/activate")
    print(f"   python scripts/start_server.py")
    print(f"3. 在Windows浏览器中访问:")
    print(f"   http://localhost:{config['local_port']}")
    
    print(f"\n🎉 配置完成！")

if __name__ == "__main__":
    main() 