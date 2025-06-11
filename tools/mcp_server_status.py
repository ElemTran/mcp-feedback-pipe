#!/usr/bin/env python3
"""
MCP反馈服务器状态查看器
独立工具，不会影响现有服务器运行
"""

import json
import os
import subprocess
import re
import time
from backend.server_pool import load_server_status_from_file, STATUS_FILE
from backend.config import get_server_config

def get_running_servers_by_lsof():
    """通过lsof命令检测运行中的服务器"""
    try:
        result = subprocess.run(['lsof', '-i', '-P', '-n'], 
                              capture_output=True, text=True, timeout=10)
        
        lines = result.stdout.split('\n')
        running_servers = []
        
        for line in lines:
            if 'python' in line and 'LISTEN' in line and '127.0.0.1:' in line:
                # 提取端口号
                port_match = re.search(r'127\.0\.0\.1:(\d+)', line)
                if port_match:
                    port = int(port_match.group(1))
                    # 检查是否是我们的服务
                    try:
                        import requests
                        response = requests.get(f"http://127.0.0.1:{port}/ping", timeout=2)
                        if response.status_code == 200:
                            running_servers.append(port)
                    except:
                        continue
        
        return running_servers
        
    except Exception as e:
        print(f"⚠️ 检测服务器失败: {e}")
        return []

def format_server_status():
    """格式化显示服务器状态"""
    print("🔍 MCP反馈服务器状态查看器")
    print("=" * 50)
    
    # 1. 从状态文件读取信息
    saved_status = load_server_status_from_file()
    
    # 2. 检测实际运行的服务器
    running_ports = get_running_servers_by_lsof()
    
    if not saved_status and not running_ports:
        print("❌ 没有找到任何MCP反馈服务器")
        print("\n💡 提示:")
        print("  - 使用 collect_feedback 工具启动反馈服务器")
        print("  - 使用 create_server_pool 工具创建多个服务器")
        return
    
    current_time = time.time()
    
    # 显示从状态文件读取的信息
    if saved_status:
        print(f"📊 上次记录状态 ({saved_status.get('last_updated_readable', '未知时间')}):")
        print(f"   总服务器数: {saved_status.get('total_servers', 0)}")
        print(f"   活跃服务器: {saved_status.get('active_servers', 0)}")
        print(f"   记录端口: {', '.join(map(str, saved_status.get('ports_in_use', [])))}")
        
        if saved_status.get('servers'):
            print("\n📋 记录的服务器详情:")
            for server in saved_status['servers']:
                status_emoji = {
                    "idle": "⚪",
                    "starting": "🟡", 
                    "running": "🟢",
                    "stopping": "🟠",
                    "error": "🔴"
                }.get(server.get("status"), "❓")
                
                port = server.get('port')
                is_running = port in running_ports if port else False
                status_text = "运行中" if is_running else "已停止"
                status_emoji = "🟢" if is_running else "🔴"
                
                print(f"   {status_emoji} {server.get('session_id', '未知')}")
                print(f"      端口: {port or 'N/A'}")
                print(f"      状态: {status_text}")
                print(f"      任务: {server.get('work_summary', '无描述')}")
                if server.get('timeout_seconds'):
                    print(f"      超时: {server['timeout_seconds']}秒")
                if port and is_running:
                    print(f"      远程地址: http://127.0.0.1:{port}")
                print()
    
    # 显示当前实际运行的服务器
    if running_ports:
        print("🔍 当前实际运行的服务器:")
        for port in sorted(running_ports):
            print(f"   🟢 端口 {port}: http://127.0.0.1:{port}")
        print()
        
        # 生成SSH转发命令
        server_config = get_server_config()
        base_local_port = getattr(server_config, 'recommended_local_forward_port', 8888)
        
        print("🔗 SSH端口转发命令:")
        for i, port in enumerate(sorted(running_ports)):
            local_port = base_local_port + i
            print(f"   ssh -L {local_port}:127.0.0.1:{port} your_user@your_server")
            print(f"   # 然后访问: http://127.0.0.1:{local_port}/")
            print()
        
        print("💡 使用说明:")
        print("   1. 复制上述SSH转发命令在本地终端执行")
        print("   2. 每个命令会创建一个独立的端口转发")
        print("   3. 可以同时在多个浏览器标签页中访问不同的反馈界面")
    else:
        print("⚠️ 当前没有检测到运行中的服务器")
        if saved_status:
            print("   (可能服务器已停止，但状态文件仍存在)")

    # 状态文件信息
    if os.path.exists(STATUS_FILE):
        file_stat = os.stat(STATUS_FILE)
        file_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_stat.st_mtime))
        print(f"\n📄 状态文件: {STATUS_FILE}")
        print(f"   最后修改: {file_time}")

def main():
    """主入口"""
    try:
        format_server_status()
    except KeyboardInterrupt:
        print("\n👋 状态查看已中断")
    except Exception as e:
        print(f"❌ 发生错误: {e}")

if __name__ == "__main__":
    main() 