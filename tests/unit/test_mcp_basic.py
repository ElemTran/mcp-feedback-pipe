#!/usr/bin/env python3
"""
Debug脚本：测试MCP collect_feedback功能
"""

import sys
import os

def test_collect_feedback():
    """测试collect_feedback功能"""
    try:
        print("开始测试collect_feedback...")
        
        # 导入模块
        from backend.server_manager import ServerManager
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
        
        # 测试成功，不返回任何值
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"测试失败: {e}"

if __name__ == "__main__":
    try:
        test_collect_feedback()
        # 如果没有抛出异常，说明测试成功
        sys.exit(0)
    except Exception:
        # 如果抛出异常，说明测试失败
        sys.exit(1)
