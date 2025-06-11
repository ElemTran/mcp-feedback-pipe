#!/usr/bin/env python3
"""
MCP客户端连接测试脚本
模拟MCP客户端连接并调用工具，触发可能的异常
"""

import subprocess
import sys
import time
import json
import os
import signal
import threading
from contextlib import contextmanager

def start_mcp_server():
    """启动MCP服务器进程"""
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONUNBUFFERED'] = '1'
    
    process = subprocess.Popen(
        [sys.executable, 'backend/server.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True,
        env=env
    )
    
    return process

def simulate_mcp_client_interaction(server_process):
    """模拟MCP客户端与服务器的交互"""
    print("📡 开始模拟MCP客户端交互...")
    
    try:
        # 模拟MCP协议初始化消息
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("📨 发送初始化消息...")
        server_process.stdin.write(json.dumps(init_message) + '\n')
        server_process.stdin.flush()
        
        time.sleep(1)
        
        # 模拟调用collect_feedback工具
        tool_call_message = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "collect_feedback",
                "arguments": {
                    "work_summary": "测试异常捕获功能",
                    "timeout_seconds": 10,
                    "suggest": ["测试选项1", "测试选项2"]
                }
            }
        }
        
        print("🔧 发送工具调用消息...")
        server_process.stdin.write(json.dumps(tool_call_message) + '\n')
        server_process.stdin.flush()
        
        time.sleep(2)
        
        return True
        
    except Exception as e:
        print(f"❌ 客户端交互异常: {str(e)}")
        return False

def monitor_server_output(server_process, duration=10):
    """监控服务器输出"""
    print(f"👀 监控服务器输出 {duration} 秒...")
    
    stdout_lines = []
    stderr_lines = []
    
    def read_stdout():
        while True:
            try:
                line = server_process.stdout.readline()
                if line:
                    stdout_lines.append(line.strip())
                    print(f"[STDOUT] {line.strip()}")
                else:
                    break
            except:
                break
    
    def read_stderr():
        while True:
            try:
                line = server_process.stderr.readline()
                if line:
                    stderr_lines.append(line.strip())
                    print(f"[STDERR] {line.strip()}")
                else:
                    break
            except:
                break
    
    # 启动读取线程
    stdout_thread = threading.Thread(target=read_stdout)
    stderr_thread = threading.Thread(target=read_stderr)
    
    stdout_thread.daemon = True
    stderr_thread.daemon = True
    
    stdout_thread.start()
    stderr_thread.start()
    
    # 等待指定时间
    time.sleep(duration)
    
    return stdout_lines, stderr_lines

def main():
    """主函数"""
    print("🚀 MCP客户端连接测试")
    print("=" * 60)
    
    server_process = None
    
    try:
        # 启动MCP服务器
        print("🔄 启动MCP服务器...")
        server_process = start_mcp_server()
        print(f"✅ MCP服务器已启动，PID: {server_process.pid}")
        
        # 等待服务器启动
        time.sleep(2)
        
        # 检查服务器是否正常运行
        if server_process.poll() is not None:
            stdout, stderr = server_process.communicate()
            print("❌ 服务器启动失败或立即退出")
            print(f"退出码: {server_process.returncode}")
            if stdout:
                print(f"STDOUT: {stdout}")
            if stderr:
                print(f"STDERR: {stderr}")
                if "!!! An exception occurred during mcp.run() !!!" in stderr:
                    print("🎯 检测到异常捕获日志!")
                    return
            return
        
        # 开始监控输出
        stdout_lines, stderr_lines = monitor_server_output(server_process, 5)
        
        # 模拟客户端交互
        simulate_mcp_client_interaction(server_process)
        
        # 继续监控一段时间
        print("\n🔄 继续监控服务器响应...")
        additional_stdout, additional_stderr = monitor_server_output(server_process, 8)
        
        stdout_lines.extend(additional_stdout)
        stderr_lines.extend(additional_stderr)
        
        # 分析结果
        print("\n" + "=" * 60)
        print("📊 测试结果分析:")
        
        all_output = '\n'.join(stdout_lines + stderr_lines)
        
        if "!!! An exception occurred during mcp.run() !!!" in all_output:
            print("🎯 ✅ 成功检测到异常捕获日志!")
            print("🔍 异常详情:")
            for line in stderr_lines:
                if "!!!" in line or "Exception" in line or "Traceback" in line:
                    print(f"  {line}")
        else:
            print("⚠️ 未检测到预期的异常捕获日志")
            print("📋 服务器输出摘要:")
            print(f"  - STDOUT行数: {len(stdout_lines)}")
            print(f"  - STDERR行数: {len(stderr_lines)}")
            
            if stdout_lines:
                print("  - STDOUT样本:")
                for line in stdout_lines[:5]:
                    print(f"    {line}")
            
            if stderr_lines:
                print("  - STDERR样本:")
                for line in stderr_lines[:5]:
                    print(f"    {line}")
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断测试")
    except Exception as e:
        print(f"❌ 测试过程异常: {str(e)}")
    finally:
        # 清理进程
        if server_process and server_process.poll() is None:
            print("🛑 正在关闭服务器进程...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
                server_process.wait()
            print("✅ 服务器进程已关闭")

if __name__ == "__main__":
    main()