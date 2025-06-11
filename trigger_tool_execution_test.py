#!/usr/bin/env python3
"""
MCP工具执行深度测试
专门测试collect_feedback工具的完整执行流程，捕获可能的异常
"""

import subprocess
import sys
import time
import json
import os
import threading
import signal

def create_mcp_client_script():
    """创建一个使用mcp库的客户端脚本"""
    client_script = '''
import asyncio
import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_client():
    server_params = StdioServerParameters(
        command="python",
        args=["backend/server.py"],
        env=None
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                print("🔗 MCP客户端连接成功")
                
                # 初始化
                await session.initialize()
                print("✅ MCP会话初始化完成")
                
                # 列出可用工具
                tools = await session.list_tools()
                print(f"📋 可用工具: {[tool.name for tool in tools.tools]}")
                
                # 调用collect_feedback工具
                print("🔧 开始调用collect_feedback工具...")
                result = await session.call_tool(
                    "collect_feedback",
                    {
                        "work_summary": "深度测试MCP工具执行流程",
                        "timeout_seconds": 5,  # 短超时，避免长时间等待
                        "suggest": ["测试成功", "发现问题", "需要调试"]
                    }
                )
                print(f"✅ 工具调用结果: {result}")
                
    except Exception as e:
        print(f"❌ MCP客户端异常: {str(e)}")
        import traceback
        print("🔍 完整异常信息:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_client())
'''
    
    with open('mcp_client_test.py', 'w', encoding='utf-8') as f:
        f.write(client_script)
    
    return 'mcp_client_test.py'

def run_direct_tool_test():
    """直接调用工具函数进行测试"""
    print("🧪 直接工具函数测试...")
    
    try:
        # 添加backend到路径
        sys.path.insert(0, 'backend')
        
        # 尝试导入并直接调用collect_feedback
        print("📦 导入backend.server模块...")
        from backend.server import collect_feedback
        
        print("🔧 直接调用collect_feedback函数...")
        result = collect_feedback(
            work_summary="直接函数调用测试",
            timeout_seconds=3,
            suggest=["测试1", "测试2"]
        )
        print(f"✅ 直接调用结果: {result}")
        return True, "直接调用成功"
        
    except Exception as e:
        print(f"❌ 直接调用异常: {str(e)}")
        import traceback
        error_info = traceback.format_exc()
        print("🔍 完整异常信息:")
        print(error_info)
        return False, error_info

def run_mcp_client_test():
    """运行MCP客户端测试"""
    print("🚀 MCP客户端工具调用测试...")
    
    # 创建客户端脚本
    client_script_path = create_mcp_client_script()
    
    try:
        # 运行客户端脚本
        result = subprocess.run(
            [sys.executable, client_script_path],
            capture_output=True,
            text=True,
            timeout=30,
            env=dict(os.environ, PYTHONUNBUFFERED='1')
        )
        
        print(f"🔍 客户端退出码: {result.returncode}")
        if result.stdout:
            print("📄 客户端输出:")
            print(result.stdout)
        
        if result.stderr:
            print("❌ 客户端错误:")
            print(result.stderr)
            
        return result.returncode == 0, result.stdout + result.stderr
        
    except subprocess.TimeoutExpired:
        print("⏰ 客户端测试超时")
        return False, "测试超时"
    except Exception as e:
        print(f"❌ 客户端测试异常: {str(e)}")
        return False, str(e)
    finally:
        # 清理脚本文件
        if os.path.exists(client_script_path):
            os.remove(client_script_path)

def main():
    """主函数"""
    print("🚀 MCP工具执行深度测试")
    print("=" * 60)
    
    results = []
    
    # 测试1: 直接函数调用
    print("\n📋 测试1: 直接函数调用")
    print("-" * 40)
    success1, output1 = run_direct_tool_test()
    results.append(("直接函数调用", success1, output1))
    
    # 测试2: MCP客户端调用
    print("\n📋 测试2: MCP客户端调用")
    print("-" * 40)
    success2, output2 = run_mcp_client_test()
    results.append(("MCP客户端调用", success2, output2))
    
    # 结果汇总
    print("\n" + "=" * 60)
    print("📊 测试结果汇总:")
    print("=" * 60)
    
    exception_found = False
    
    for test_name, success, output in results:
        print(f"\n🧪 {test_name}:")
        print(f"  状态: {'✅ 成功' if success else '❌ 失败'}")
        
        # 检查是否有异常捕获日志
        if "!!! An exception occurred during mcp.run() !!!" in output:
            print("  🎯 发现异常捕获日志!")
            exception_found = True
            # 提取异常详情
            lines = output.split('\n')
            for i, line in enumerate(lines):
                if "!!! An exception occurred during mcp.run() !!!" in line:
                    print("  🔍 异常详情:")
                    # 打印异常相关的行
                    for j in range(max(0, i-1), min(len(lines), i+10)):
                        if lines[j].strip():
                            print(f"    {lines[j]}")
                    break
        
        # 检查其他异常信息
        if "Exception" in output or "Traceback" in output or "Error" in output:
            print("  ⚠️ 发现异常信息")
            exception_lines = [line for line in output.split('\n') 
                             if any(keyword in line for keyword in ['Exception', 'Traceback', 'Error:', 'ImportError', 'ModuleNotFoundError'])]
            if exception_lines:
                print("  🔍 异常摘要:")
                for line in exception_lines[:5]:  # 只显示前5行
                    print(f"    {line}")
        
        if not success:
            print(f"  📝 输出摘要: {output[:200]}...")
    
    # 最终结论
    print("\n" + "=" * 60)
    print("🎯 最终诊断结论:")
    
    if exception_found:
        print("✅ 成功捕获到目标异常日志!")
        print("🎉 异常捕获功能验证成功")
    else:
        print("⚠️ 未捕获到预期的 '!!! An exception occurred during mcp.run() !!!' 日志")
        print("💡 可能的情况:")
        print("  1. MCP服务器工作正常，没有在mcp.run()层面发生异常")
        print("  2. 异常发生在工具执行的更深层次")
        print("  3. 之前报告的问题可能不是启动异常，而是执行过程异常")
        
        # 根据测试结果提供建议
        if results[0][1]:  # 直接调用成功
            print("  4. 直接函数调用成功，说明业务逻辑基本正常")
        if results[1][1]:  # MCP客户端调用成功
            print("  5. MCP协议通信正常，服务器响应正常")

if __name__ == "__main__":
    main()