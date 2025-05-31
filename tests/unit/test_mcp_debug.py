#!/usr/bin/env python3
"""
Debug MCP工具调用错误
"""

import sys
import os
import traceback

# 添加src目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

def debug_mcp_collect_feedback():
    """详细调试MCP collect_feedback调用"""
    print("=== MCP工具调用详细调试 ===")
    
    try:
        # 1. 测试模块导入
        print("1. 测试模块导入...")
        from mcp_feedback_pipe.server import collect_feedback
        print("✓ collect_feedback导入成功")
        
        # 2. 测试ServerManager
        print("2. 测试ServerManager...")
        from mcp_feedback_pipe.server_manager import ServerManager
        server_manager = ServerManager()
        print("✓ ServerManager创建成功")
        
        # 3. 测试服务器启动
        print("3. 测试服务器启动...")
        port = server_manager.start_server("Debug测试", 10, "")
        print(f"✓ 服务器启动成功，端口: {port}")
        
        # 4. 测试等待反馈
        print("4. 测试等待反馈...")
        result = server_manager.wait_for_feedback(10)
        print(f"等待结果: {result}")
        
        # 5. 测试process_feedback_to_mcp方法
        if result:
            print("5. 测试process_feedback_to_mcp方法...")
            try:
                mcp_result = server_manager.feedback_handler.process_feedback_to_mcp(result)
                print(f"✓ process_feedback_to_mcp成功")
                print(f"MCP结果类型: {type(mcp_result)}")
                print(f"MCP结果长度: {len(mcp_result) if isinstance(mcp_result, list) else 'N/A'}")
                print(f"MCP结果内容: {mcp_result}")
            except Exception as e:
                print(f"✗ process_feedback_to_mcp失败: {e}")
                traceback.print_exc()
        
        # 6. 停止服务器
        print("6. 停止服务器...")
        server_manager.stop_server()
        print("✓ 服务器停止成功")
        
        # 7. 现在测试完整的collect_feedback调用
        print("7. 测试完整的collect_feedback调用...")
        
        # 捕获所有可能的异常
        try:
            result = collect_feedback(
                work_summary="完整测试 - 请提交任何反馈", 
                timeout_seconds=10,
                suggest=["成功", "失败"]
            )
            
            print(f"✓ collect_feedback调用成功！")
            print(f"结果类型: {type(result)}")
            print(f"结果内容: {result}")
            
            if result is None:
                print("⚠️ 结果为None - 可能超时或用户未提交")
            elif isinstance(result, list) and len(result) == 0:
                print("⚠️ 结果为空列表")
            else:
                print("✓ 收到有效反馈")
                
        except Exception as e:
            print(f"✗ collect_feedback调用失败: {e}")
            print(f"异常类型: {type(e)}")
            traceback.print_exc()
            
            # 检查是否是特定的异常
            if "No module named" in str(e):
                print("🔍 这是模块导入问题")
            elif "timeout" in str(e).lower():
                print("🔍 这是超时问题")
            elif "port" in str(e).lower():
                print("🔍 这是端口问题")
            else:
                print("🔍 这是其他类型的问题")
        
        return True
        
    except Exception as e:
        print(f"✗ 调试过程失败: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_mcp_collect_feedback()
    print(f"\n=== 调试结果: {'成功' if success else '失败'} ===") 