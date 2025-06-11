#!/usr/bin/env python3
"""
MCP服务器启动触发测试脚本
用于测试mcp-feedback-pipe服务启动并收集错误日志
"""

import subprocess
import sys
import time
import json
import os

def trigger_mcp_server():
    """触发MCP服务器启动并尝试调用工具"""
    print("🔍 开始触发MCP服务器启动...")
    
    # 方法1: 直接通过subprocess启动MCP服务器
    print("\n📋 方法1: 直接启动backend/server.py")
    try:
        # 设置环境变量以确保编码正确
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['PYTHONUNBUFFERED'] = '1'
        
        # 启动MCP服务器进程
        process = subprocess.Popen(
            [sys.executable, 'backend/server.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
            env=env
        )
        
        print(f"✅ MCP服务器进程已启动，PID: {process.pid}")
        print("⏰ 等待5秒以观察启动日志...")
        
        # 等待一段时间收集输出
        time.sleep(5)
        
        # 检查进程是否还在运行
        if process.poll() is None:
            print("🟢 MCP服务器仍在运行")
            # 尝试正常终止进程
            process.terminate()
            try:
                stdout, stderr = process.communicate(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
        else:
            # 进程已结束，获取输出
            stdout, stderr = process.communicate()
            print(f"🔴 MCP服务器进程已结束，返回码: {process.returncode}")
        
        # 输出日志信息
        if stdout:
            print("\n📄 标准输出:")
            print(stdout)
        
        if stderr:
            print("\n❌ 错误输出:")
            print(stderr)
            
            # 检查是否包含我们添加的异常捕获标识
            if "!!! An exception occurred during mcp.run() !!!" in stderr:
                print("\n🎯 检测到异常捕获日志!")
                return True, stderr
        
        return True, f"stdout: {stdout}\nstderr: {stderr}"
        
    except Exception as e:
        error_msg = f"启动MCP服务器时发生异常: {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg

def main():
    """主函数"""
    print("🚀 MCP服务器启动触发测试")
    print("=" * 50)
    
    success, output = trigger_mcp_server()
    
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    print(f"✅ 成功触发启动: {success}")
    print("\n📋 完整输出:")
    print(output)
    
    if "!!! An exception occurred during mcp.run() !!!" in output:
        print("\n🎯 成功捕获到异常日志!")
        print("🔍 异常信息已记录，任务完成")
    else:
        print("\n⚠️ 未检测到预期的异常捕获日志")
        print("💡 可能的原因:")
        print("   1. MCP服务器成功启动，没有异常")
        print("   2. 异常发生在其他位置")
        print("   3. 日志输出被重定向或缓冲")

if __name__ == "__main__":
    main()