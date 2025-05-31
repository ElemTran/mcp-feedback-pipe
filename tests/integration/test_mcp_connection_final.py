#!/usr/bin/env python3
"""
最终MCP连接测试
模拟真实的MCP工具调用流程，验证延迟清理修复效果
"""

import sys
import os
import time
import threading

# 添加src目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

def test_mcp_tool_simulation():
    """模拟MCP工具调用流程"""
    print("🧪 模拟MCP工具调用流程...")
    
    try:
        # 导入MCP工具函数
        from mcp_feedback_pipe.server import collect_feedback
        
        print("1. 调用collect_feedback工具...")
        
        # 在后台线程中调用工具，模拟MCP服务器的行为
        result_container = {'result': None, 'error': None}
        
        def call_tool():
            try:
                result = collect_feedback(
                    work_summary="测试MCP连接稳定性修复",
                    timeout_seconds=60,
                    suggest=["修复成功", "还有问题", "需要进一步测试"]
                )
                result_container['result'] = result
                print("✅ MCP工具调用成功完成")
                print(f"   返回结果类型: {type(result)}")
                print(f"   结果数量: {len(result) if result else 0}")
            except Exception as e:
                result_container['error'] = e
                print(f"❌ MCP工具调用失败: {e}")
        
        tool_thread = threading.Thread(target=call_tool, daemon=True)
        tool_thread.start()
        
        print("2. 等待用户在浏览器中提交反馈...")
        print("   请提交反馈后观察是否出现连接中断")
        
        # 等待工具完成
        tool_thread.join(timeout=70)
        
        if tool_thread.is_alive():
            print("⚠️  工具调用超时")
        elif result_container['error']:
            print(f"❌ 工具调用出错: {result_container['error']}")
        elif result_container['result']:
            print("✅ 工具调用成功，连接保持稳定")
            print("3. 等待延迟清理完成...")
            time.sleep(3)  # 等待延迟清理
            print("✅ 延迟清理完成，测试结束")
        else:
            print("⚠️  未收到结果")
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mcp_tool_simulation() 