#!/usr/bin/env python3
"""
测试脚本：验证 collect_feedback 工具的超时逻辑修复
用于验证超时时间是否精确按照 timeout_seconds 参数执行
"""

import time
import json
from backend.server import collect_feedback

def test_timeout_precision():
    """测试超时精度"""
    print("🧪 开始测试超时逻辑修复...")
    
    # 测试不同的超时时间
    test_cases = [
        {"timeout": 10, "description": "短超时测试（10秒）"},
        {"timeout": 30, "description": "中等超时测试（30秒）"},
        {"timeout": 60, "description": "长超时测试（60秒）"},
    ]
    
    for test_case in test_cases:
        timeout_seconds = test_case["timeout"]
        description = test_case["description"]
        
        print(f"\n📋 {description}")
        print(f"⏱️  配置超时时间: {timeout_seconds} 秒")
        
        # 记录开始时间
        start_time = time.time()
        
        try:
            # 调用 collect_feedback，不提供任何用户交互
            result = collect_feedback(
                work_summary=f"测试超时精度 - {description}",
                timeout_seconds=timeout_seconds,
                suggest=[]
            )
            
            # 记录结束时间
            end_time = time.time()
            actual_duration = end_time - start_time
            
            print(f"✅ 测试完成")
            print(f"📊 实际等待时间: {actual_duration:.2f} 秒")
            print(f"📊 配置超时时间: {timeout_seconds} 秒")
            print(f"📊 时间差异: {abs(actual_duration - timeout_seconds):.2f} 秒")
            
            # 验证结果
            if result is None or result == []:
                print("✅ 正确返回超时结果")
            else:
                print(f"⚠️  意外的结果: {result}")
            
            # 验证时间精度（允许2秒误差）
            time_diff = abs(actual_duration - timeout_seconds)
            if time_diff <= 2.0:
                print("✅ 超时时间精度正常")
            else:
                print(f"❌ 超时时间精度异常，差异 {time_diff:.2f} 秒")
            
        except Exception as e:
            end_time = time.time()
            actual_duration = end_time - start_time
            print(f"❌ 测试异常: {e}")
            print(f"📊 异常前等待时间: {actual_duration:.2f} 秒")
        
        print("-" * 50)

def test_quick_timeout():
    """测试快速超时（5秒）"""
    print("\n🚀 快速超时测试（5秒）")
    
    start_time = time.time()
    
    try:
        result = collect_feedback(
            work_summary="快速超时测试",
            timeout_seconds=5,
            suggest=["确认", "取消"]
        )
        
        end_time = time.time()
        actual_duration = end_time - start_time
        
        print(f"⏱️  实际等待: {actual_duration:.2f} 秒（期望 ~5 秒）")
        
        if 4 <= actual_duration <= 7:  # 允许2秒误差
            print("✅ 快速超时测试通过")
        else:
            print("❌ 快速超时测试失败")
            
    except Exception as e:
        end_time = time.time()
        actual_duration = end_time - start_time
        print(f"❌ 快速超时测试异常: {e}")
        print(f"⏱️  异常前等待: {actual_duration:.2f} 秒")

if __name__ == "__main__":
    print("🔧 超时逻辑修复验证测试")
    print("=" * 60)
    
    # 运行快速测试
    test_quick_timeout()
    
    # 询问是否运行完整测试
    print("\n" + "=" * 60)
    choice = input("是否运行完整超时测试？(包含较长等待时间) [y/N]: ").strip().lower()
    
    if choice in ['y', 'yes']:
        test_timeout_precision()
    else:
        print("⏭️  跳过完整测试")
    
    print("\n🎯 测试完成！")
    print("\n📋 验证要点：")
    print("1. 实际等待时间应该接近配置的 timeout_seconds")
    print("2. 不应该因为客户端未连接而提前超时")
    print("3. 主超时逻辑应该具有最高优先级")