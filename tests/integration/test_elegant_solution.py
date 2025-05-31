#!/usr/bin/env python3
"""
测试服务器池的优雅解决方案
验证资源管理和连接稳定性
"""

import sys
import os
import time

# 添加src目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

def test_server_pool():
    """测试服务器池功能"""
    print("🧪 测试服务器池优雅解决方案...")
    
    try:
        from mcp_feedback_pipe.server_pool import get_server_pool, get_managed_server, release_managed_server
        
        print("1. 获取服务器池实例...")
        pool = get_server_pool()
        print(f"✅ 服务器池创建成功: {pool}")
        
        print("2. 测试服务器获取和释放...")
        server1 = get_managed_server("test_session_1")
        server2 = get_managed_server("test_session_2")
        server3 = get_managed_server("test_session_1")  # 应该返回同一个实例
        
        print(f"✅ 服务器1: {id(server1)}")
        print(f"✅ 服务器2: {id(server2)}")
        print(f"✅ 服务器3: {id(server3)}")
        print(f"✅ 服务器1和3是同一实例: {server1 is server3}")
        
        print("3. 测试资源清理...")
        release_managed_server("test_session_1", immediate=False)
        release_managed_server("test_session_2", immediate=True)
        
        print("4. 等待自动清理...")
        time.sleep(6)  # 等待清理线程工作
        
        print("✅ 服务器池测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_mcp_tool_with_pool():
    """测试使用服务器池的MCP工具"""
    print("\n🧪 测试MCP工具与服务器池集成...")
    
    try:
        from mcp_feedback_pipe.server import collect_feedback
        
        print("1. 模拟MCP工具调用...")
        
        # 模拟快速连续调用
        def simulate_call(call_id):
            try:
                print(f"   调用 {call_id}: 启动...")
                # 这里不实际等待用户输入，只测试服务器启动
                result = collect_feedback(
                    work_summary=f"测试调用 {call_id}",
                    timeout_seconds=5  # 短超时用于测试
                )
                print(f"   调用 {call_id}: 完成")
                return True
            except Exception as e:
                if "操作超时" in str(e):
                    print(f"   调用 {call_id}: 超时（预期行为）")
                    return True
                else:
                    print(f"   调用 {call_id}: 错误 - {e}")
                    return False
        
        # 测试多个并发调用
        import threading
        results = []
        threads = []
        
        for i in range(3):
            thread = threading.Thread(target=lambda i=i: results.append(simulate_call(i+1)))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        success_count = sum(results)
        print(f"✅ 并发测试完成: {success_count}/3 成功")
        
    except Exception as e:
        print(f"❌ MCP工具测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_server_pool()
    test_mcp_tool_with_pool()
    print("\n🎉 所有测试完成！") 