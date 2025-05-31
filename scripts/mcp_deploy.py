#!/usr/bin/env python3
"""
MCP反馈通道部署脚本 v3.0
支持Web架构和SSH环境
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def setup_environment():
    """设置环境"""
    # 添加src目录到Python路径
    current_dir = Path(__file__).parent.parent
    src_dir = current_dir / 'src'
    sys.path.insert(0, str(src_dir))
    
    # 激活虚拟环境
    venv_activate = current_dir / '.venv' / 'bin' / 'activate'
    if venv_activate.exists():
        print("✅ 虚拟环境已找到")
    else:
        print("❌ 找不到虚拟环境，请先运行: python -m venv .venv")
        return False
    return True

def start_web_service():
    """启动Web服务"""
    print("🌐 启动Web服务...")
    
    from mcp_feedback_pipe.server_manager import ServerManager
    
    sm = ServerManager()
    port = sm.start_server("MCP反馈通道Web服务已启动", timeout_seconds=60)
    
    print(f"✅ Web服务已启动在端口: {port}")
    print(f"📱 本地访问: http://127.0.0.1:{port}")
    
    # 检查SSH环境
    ssh_indicators = [
        os.getenv('SSH_CLIENT'),
        os.getenv('SSH_CONNECTION'), 
        os.getenv('SSH_TTY')
    ]
    
    if any(ssh_indicators):
        print("🔒 检测到SSH环境")
        print(f"💡 在本地建立SSH隧道: ssh -L {port}:localhost:{port} user@server")
        print(f"🌐 然后访问: http://localhost:{port}")
    
    return port, sm

def start_mcp_server():
    """启动MCP服务器"""
    print("🚀 启动MCP服务器...")
    
    try:
        from mcp_feedback_pipe.server import main
        main()
    except Exception as e:
        print(f"❌ MCP服务器启动失败: {e}")
        return False
    return True

def main():
    """主函数"""
    print("🔧 MCP反馈通道 v3.0 部署")
    print("=" * 40)
    
    # 设置环境
    if not setup_environment():
        return
    
    # 选择部署模式
    print("\n📋 选择部署模式:")
    print("1. Web服务模式 (用于测试Web界面)")
    print("2. MCP服务模式 (用于Claude Desktop)")
    print("3. 混合模式 (同时启动Web和MCP)")
    
    choice = input("\n请选择 (1-3): ").strip()
    
    if choice == "1":
        # Web服务模式
        port, sm = start_web_service()
        print(f"\n💡 Web服务运行中，按Ctrl+C停止")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Web服务已停止")
            sm.stop_server()
            
    elif choice == "2":
        # MCP服务模式
        print("\n🔧 MCP服务模式启动...")
        print("📝 请确保Claude Desktop配置中包含此服务")
        start_mcp_server()
        
    elif choice == "3":
        # 混合模式
        print("\n🔄 混合模式启动...")
        
        # 先启动Web服务
        port, sm = start_web_service()
        
        print(f"\n🚀 Web服务已启动，现在启动MCP服务...")
        print("💡 您可以同时使用Web界面和Claude Desktop")
        
        # 启动MCP服务
        try:
            start_mcp_server()
        except KeyboardInterrupt:
            print("\n👋 服务已停止")
            sm.stop_server()
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main() 