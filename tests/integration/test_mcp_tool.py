#!/usr/bin/env python3
"""
测试MCP工具调用
"""

import sys
import os

# 添加src目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

def simulate_mcp_tool_call():
    """模拟MCP工具调用"""
    try:
        print("模拟MCP工具调用...")
        
        # 导入MCP服务器模块
        from mcp_feedback_pipe.server import collect_feedback
        print("✓ collect_feedback函数导入成功")
        
        # 调用collect_feedback函数
        print("正在调用collect_feedback...")
        print("请在浏览器中提交反馈...")
        
        result = collect_feedback(
            work_summary="测试工作摘要 - 请在浏览器中提交任何反馈来测试功能", 
            timeout_seconds=30,  # 给用户足够时间
            suggest=["测试成功", "测试失败", "需要更多时间"]
        )
        
        print(f"✓ collect_feedback调用成功！")
        print(f"返回结果类型: {type(result)}")
        print(f"返回结果内容: {result}")
        
        if result:
            print("✓ 成功收到用户反馈")
        else:
            print("⚠️ 未收到用户反馈（可能超时）")
            
        return True
        
    except Exception as e:
        print(f"✗ MCP工具调用失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = simulate_mcp_tool_call()
    print(f"测试结果: {'成功' if success else '失败'}") 