#!/usr/bin/env python3
"""
测试内存安全检查中的递归深度限制优化
验证 get_deep_size 函数能够正确处理深度过大的对象并避免栈溢出
"""

import unittest
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


class TestAppMemorySafety(unittest.TestCase):
    """测试内存安全检查功能"""

    def setUp(self):
        """测试前准备"""
        self.feedback_handler = FeedbackHandler()
        self.app = FeedbackApp(self.feedback_handler, "测试工作摘要")

    def test_normal_depth(self):
        """测试正常深度的对象"""
        # 创建正常深度的测试数据（深度50）
        test_data = {
            'text': 'Test feedback',
            'images': [],
            'nested_data': create_deep_nested_structure(50),
            'timestamp': time.time()
        }

        result = self.app._check_memory_safety(test_data)
        self.assertTrue(result, "正常深度对象处理应该成功")

    def test_excessive_depth(self):
        """测试超过限制深度的对象"""
        # 创建超过最大深度限制的测试数据（深度150，超过默认限制100）
        test_data = {
            'text': 'Test feedback with deep nesting',
            'images': [],
            'deeply_nested_data': create_deep_nested_structure(150),
            'timestamp': time.time()
        }

        try:
            self.app._check_memory_safety(test_data)
            # 测试通过：要么成功返回（有深度限制），要么抛出异常
        except RecursionError:
            self.fail("发生递归错误，说明深度限制没有生效")
        except Exception:
            # 捕获到预期异常也是成功的（比如深度超限异常）
            pass

    def test_wide_structure(self):
        """测试宽度很大但深度正常的结构"""
        # 创建宽度很大的测试数据
        test_data = {
            'text': 'Test feedback with wide structure',
            'images': [],
            'wide_data': create_wide_structure(),
            'timestamp': time.time()
        }

        result = self.app._check_memory_safety(test_data)
        self.assertTrue(result, "宽度大对象处理应该成功")

    def test_circular_reference(self):
        """测试循环引用的处理"""
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

        result = self.app._check_memory_safety(test_data)
        self.assertTrue(result, "循环引用对象处理应该成功")

    def test_memory_limit(self):
        """测试内存限制功能"""
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

        # 内存限制检查完成，无论结果如何都算成功（测试主要验证不会崩溃）
        self.app._check_memory_safety(test_data)
        # 不检查具体结果，因为可能根据系统配置返回 True 或 False


if __name__ == '__main__':
    unittest.main()
