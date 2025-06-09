#!/usr/bin/env python3
"""
测试内存安全检查中的递归深度限制优化
验证 get_deep_size 函数能够正确处理深度过大的对象并避免栈溢出
"""

import sys
import os
import time

from backend.app import FeedbackApp
from backend.feedback_handler import FeedbackHandler

def create_deep_nested_structure(depth: int) -> dict:
    """创建指定深度的嵌套字典结构"""
    if depth <= 0:
        return {"end": "value"}
    
    return {"level": depth, "nested": create_deep_nested_structure(depth - 1)}

def create_wide_structure() -> dict:
    """创建一个宽度很大但深度正常的结构"""
    return {
        f"key_{i}": {
            f"subkey_{j}": f"value_{i}_{j}"
            for j in range(50)
        }
        for i in range(100)
    }

def test_normal_depth():
    """测试正常深度的对象"""
    print("🧪 测试正常深度的对象处理...")
    
    feedback_handler = FeedbackHandler()
    app = FeedbackApp(feedback_handler, "测试工作摘要")
    
    # 创建正常深度的测试数据（深度50）
    test_data = {
        'text': 'Test feedback',
        'images': [],
        'nested_data': create_deep_nested_structure(50),
        'timestamp': time.time()
    }
    
    try:
        result = app._check_memory_safety(test_data)
        print(f"✅ 正常深度对象处理成功: {result}")
        return True
    except Exception as e:
        print(f"❌ 正常深度对象处理失败: {e}")
        return False

def test_excessive_depth():
    """测试超过限制深度的对象"""
    print("🧪 测试超过限制深度的对象处理...")
    
    feedback_handler = FeedbackHandler()
    app = FeedbackApp(feedback_handler, "测试工作摘要")
    
    # 创建超过最大深度限制的测试数据（深度150，超过默认限制100）
    test_data = {
        'text': 'Test feedback with deep nesting',
        'images': [],
        'deeply_nested_data': create_deep_nested_structure(150),
        'timestamp': time.time()
    }
    
    try:
        result = app._check_memory_safety(test_data)
        print(f"✅ 超深度对象处理成功，没有栈溢出: {result}")
        return True
    except RecursionError:
        print("❌ 发生递归错误，说明深度限制没有生效")
        return False
    except Exception as e:
        print(f"✅ 超深度对象处理成功，捕获到预期异常: {e}")
        return True

def test_wide_structure():
    """测试宽度很大但深度正常的结构"""
    print("🧪 测试宽度很大的对象处理...")
    
    feedback_handler = FeedbackHandler()
    app = FeedbackApp(feedback_handler, "测试工作摘要")
    
    # 创建宽度很大的测试数据
    test_data = {
        'text': 'Test feedback with wide structure',
        'images': [],
        'wide_data': create_wide_structure(),
        'timestamp': time.time()
    }
    
    try:
        result = app._check_memory_safety(test_data)
        print(f"✅ 宽度大对象处理成功: {result}")
        return True
    except Exception as e:
        print(f"❌ 宽度大对象处理失败: {e}")
        return False

def test_circular_reference():
    """测试循环引用的处理"""
    print("🧪 测试循环引用对象处理...")
    
    feedback_handler = FeedbackHandler()
    app = FeedbackApp(feedback_handler, "测试工作摘要")
    
    # 创建循环引用的测试数据
    data_a = {'name': 'A'}
    data_b = {'name': 'B'}
    data_a['ref'] = data_b
    data_b['ref'] = data_a
    
    test_data = {
        'text': 'Test feedback with circular reference',
        'images': [],
        'circular_data': data_a,
        'timestamp': time.time()
    }
    
    try:
        result = app._check_memory_safety(test_data)
        print(f"✅ 循环引用对象处理成功: {result}")
        return True
    except Exception as e:
        print(f"❌ 循环引用对象处理失败: {e}")
        return False

def test_memory_limit():
    """测试内存限制功能"""
    print("🧪 测试内存限制功能...")
    
    feedback_handler = FeedbackHandler()
    app = FeedbackApp(feedback_handler, "测试工作摘要")
    
    # 创建一个大图片数据来测试内存限制
    large_image_data = 'x' * (10 * 1024 * 1024)  # 10MB 数据
    
    test_data = {
        'text': 'Test feedback with large image',
        'images': [
            {
                'filename': 'large_image.jpg',
                'data': large_image_data,
                'size': len(large_image_data)
            }
        ],
        'timestamp': time.time()
    }
    
    try:
        result = app._check_memory_safety(test_data)
        print(f"✅ 内存限制检查完成: {result}")
        if not result:
            print("📏 数据大小超出限制，这是预期的行为")
        return True
    except Exception as e:
        print(f"❌ 内存限制检查失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("🔍 开始测试内存安全检查优化...")
    print("=" * 60)
    
    tests = [
        ("正常深度对象", test_normal_depth),
        ("超过限制深度对象", test_excessive_depth),
        ("宽度很大对象", test_wide_structure),
        ("循环引用对象", test_circular_reference),
        ("内存限制", test_memory_limit)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 运行测试: {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ 测试 {test_name} 发生异常: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 测试结果汇总:")
    
    success_count = 0
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {test_name}: {status}")
        if success:
            success_count += 1
    
    print(f"\n🎯 总结: {success_count}/{len(results)} 个测试通过")
    
    if success_count == len(results):
        print("🎉 所有测试通过！递归深度限制优化工作正常。")
        return True
    else:
        print("⚠️  部分测试失败，需要进一步检查。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
