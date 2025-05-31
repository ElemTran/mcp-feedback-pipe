#!/usr/bin/env python3
"""
测试运行脚本
支持不同类型的测试执行
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """运行命令并处理结果"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=False, capture_output=True, text=True)
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
            
        if result.returncode == 0:
            print(f"✅ {description} - 成功")
        else:
            print(f"❌ {description} - 失败 (退出码: {result.returncode})")
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ {description} - 执行失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="MCP反馈通道测试运行器")
    parser.add_argument('--type', choices=['unit', 'integration', 'e2e', 'all'], 
                       default='all', help='测试类型')
    parser.add_argument('--coverage', action='store_true', help='生成覆盖率报告')
    parser.add_argument('--parallel', action='store_true', help='并行运行测试')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    # 基础pytest命令
    pytest_cmd = "python -m pytest"
    
    # 添加选项
    if args.verbose:
        pytest_cmd += " -v"
    
    if args.coverage:
        pytest_cmd += " --cov=src/mcp_feedback_pipe --cov-report=term-missing --cov-report=html"
    
    if args.parallel:
        pytest_cmd += " -n auto"
    
    # 根据测试类型选择
    test_commands = []
    
    if args.type == 'unit':
        test_commands.append((f"{pytest_cmd} tests/unit/", "单元测试"))
    elif args.type == 'integration':
        test_commands.append((f"{pytest_cmd} tests/integration/", "集成测试"))
    elif args.type == 'e2e':
        test_commands.append((f"{pytest_cmd} tests/e2e/", "端到端测试"))
    else:  # all
        test_commands.extend([
            (f"{pytest_cmd} tests/unit/", "单元测试"),
            (f"{pytest_cmd} tests/integration/", "集成测试"),
            (f"{pytest_cmd} tests/e2e/", "端到端测试")
        ])
    
    # 执行测试
    print("🎯 MCP反馈通道 v3.0 测试运行器")
    print(f"📊 测试类型: {args.type}")
    print(f"📈 覆盖率报告: {'是' if args.coverage else '否'}")
    print(f"⚡ 并行运行: {'是' if args.parallel else '否'}")
    
    all_passed = True
    for cmd, description in test_commands:
        success = run_command(cmd, description)
        all_passed = all_passed and success
    
    # 生成测试报告
    if args.coverage:
        print(f"\n📊 覆盖率报告已生成到 htmlcov/ 目录")
    
    # 总结
    print(f"\n{'='*60}")
    if all_passed:
        print("🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("❌ 部分测试失败")
        sys.exit(1)


if __name__ == "__main__":
    main() 