"""
轻量级端口信息查询模块
专门用于快速获取MCP服务器端口信息，不影响现有服务器运行
"""

import subprocess
import re
import json
import os
from typing import List, Dict, Optional

def get_mcp_server_ports() -> List[int]:
    """快速获取当前运行的MCP服务器端口列表"""
    try:
        result = subprocess.run(['lsof', '-i', '-P', '-n'], 
                              capture_output=True, text=True, timeout=5)
        
        lines = result.stdout.split('\n')
        ports = []
        
        for line in lines:
            if 'python' in line and 'LISTEN' in line and '127.0.0.1:' in line:
                # 提取端口号
                port_match = re.search(r'127\.0\.0\.1:(\d+)', line)
                if port_match:
                    port = int(port_match.group(1))
                    # 快速检查是否是我们的服务（不等待太久）
                    try:
                        import requests
                        response = requests.get(f"http://127.0.0.1:{port}/ping", timeout=1)
                        if response.status_code == 200:
                            ports.append(port)
                    except:
                        continue
        
        return sorted(ports)
        
    except Exception:
        return []

def get_port_info_summary() -> str:
    """获取端口信息摘要，适合在MCP对话中显示"""
    ports = get_mcp_server_ports()
    
    if not ports:
        return "❌ 当前没有运行中的MCP反馈服务器"
    
    lines = [
        f"🟢 检测到 {len(ports)} 个运行中的MCP反馈服务器:",
        ""
    ]
    
    # 生成SSH转发命令
    base_local_port = 8888  # 默认本地端口
    
    for i, port in enumerate(ports):
        local_port = base_local_port + i
        lines.extend([
            f"🔌 端口 {port}:",
            f"   远程地址: http://127.0.0.1:{port}",
            f"   SSH转发: ssh -L {local_port}:127.0.0.1:{port} your_user@your_server",
            f"   本地访问: http://127.0.0.1:{local_port}/",
            ""
        ])
    
    lines.extend([
        "💡 快速使用:",
        "   1. 复制SSH转发命令在本地终端执行",
        "   2. 在浏览器中访问对应的本地地址",
        "   3. 每个端口都是独立的反馈服务器"
    ])
    
    return "\n".join(lines)

def get_detailed_port_info() -> Dict:
    """获取详细的端口信息，包含状态文件数据"""
    # 快速获取运行中的端口
    running_ports = get_mcp_server_ports()
    
    # 尝试读取状态文件
    status_file = os.path.join(os.getcwd(), ".mcp_server_pool_status.json")
    saved_info = None
    
    try:
        if os.path.exists(status_file):
            with open(status_file, 'r', encoding='utf-8') as f:
                saved_info = json.load(f)
    except:
        pass
    
    return {
        'running_ports': running_ports,
        'saved_status': saved_info,
        'has_servers': len(running_ports) > 0
    }

def format_ssh_commands(ports: List[int], base_local_port: int = 8888) -> List[str]:
    """格式化SSH转发命令"""
    commands = []
    for i, port in enumerate(ports):
        local_port = base_local_port + i
        commands.append(f"ssh -L {local_port}:127.0.0.1:{port} your_user@your_server")
    return commands 