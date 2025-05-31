#!/usr/bin/env python3
"""
Debug脚本：测试MCP collect_feedback功能
"""

import sys
import os

# 添加src目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

def test_collect_feedback():
    """测试collect_feedback功能"""
    try:
        print("开始测试collect_feedback...")
        
        # 导入模块
        from mcp_feedback_pipe.server_manager import ServerManager
        print("✓ ServerManager导入成功")
        
        # 创建服务器管理器
        server_manager = ServerManager()
        print("✓ ServerManager创建成功")
        
        # 测试启动服务器
        print("正在启动服务器...")
        port = server_manager.start_server("测试工作摘要", 10, "")
        print(f"✓ 服务器启动成功，端口: {port}")
        
        # 等待一小段时间
        import time
        time.sleep(2)
        
        # 停止服务器
        server_manager.stop_server()
        print("✓ 服务器停止成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_collect_feedback()
    sys.exit(0 if success else 1) 