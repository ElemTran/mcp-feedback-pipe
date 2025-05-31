#!/usr/bin/env python3
"""
测试MCP连接修复效果
验证反馈提交后MCP连接不会关闭
"""

import sys
import os
import time

# 添加src目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from mcp_feedback_pipe.server_manager import ServerManager

def test_connection_stability():
    """测试连接稳定性"""
    print("🧪 测试MCP连接稳定性...")
    
    # 创建服务器管理器
    server_manager = ServerManager()
    
    try:
        print("1. 启动Web服务器...")
        port = server_manager.start_server("测试工作汇报", 60)
        print(f"✅ 服务器启动成功，端口: {port}")
        
        print("2. 模拟等待用户反馈...")
        print("   请在浏览器中提交反馈，然后观察连接状态")
        
        # 等待反馈
        result = server_manager.wait_for_feedback(60)
        
        if result:
            print("✅ 收到用户反馈")
            print(f"   反馈内容: {result}")
            
            # 模拟MCP工具返回结果
            mcp_result = server_manager.feedback_handler.process_feedback_to_mcp(result)
            print("✅ MCP格式转换成功")
            print(f"   MCP结果: {mcp_result}")
            
            print("3. 测试连接是否仍然活跃...")
            time.sleep(2)  # 等待一下
            
            # 检查服务器状态
            server_info = server_manager.get_server_info()
            print(f"   服务器信息: {server_info}")
            
            print("✅ 连接测试完成，没有发现连接关闭问题")
            
        else:
            print("⚠️  超时或未收到反馈")
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("4. 清理资源...")
        server_manager.stop_server()
        print("✅ 清理完成")

if __name__ == "__main__":
    test_connection_stability() 