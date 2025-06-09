"""
CSRFProtection类的线程安全性测试
测试并发场景下的令牌生成、验证和清理操作
"""

import threading
import time
import unittest
from backend.app import CSRFProtection

class TestCSRFThreadSafety(unittest.TestCase):
    """CSRF保护的线程安全性测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.csrf_protection = CSRFProtection()
        self.results = []
        self.errors = []
    
    def test_concurrent_token_generation(self):
        """测试并发令牌生成的线程安全性"""
        tokens = []
        token_lock = threading.Lock()
        
        def generate_tokens():
            """生成令牌的工作函数"""
            try:
                for _ in range(10):
                    token = self.csrf_protection.generate_token()
                    with token_lock:
                        tokens.append(token)
                    time.sleep(0.001)  # 模拟实际使用中的延迟
            except Exception as e:
                self.errors.append(f"Token generation error: {e}")
        
        # 创建多个线程同时生成令牌
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=generate_tokens)
            threads.append(thread)
        
        # 启动所有线程
        for thread in threads:
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证结果
        self.assertEqual(len(self.errors), 0, f"Errors occurred: {self.errors}")
        self.assertEqual(len(tokens), 50, "Should generate 50 tokens (5 threads × 10 tokens)")
        
        # 验证所有令牌都是唯一的
        unique_tokens = set(tokens)
        self.assertEqual(len(unique_tokens), len(tokens), "All tokens should be unique")
    
    def test_concurrent_token_validation(self):
        """测试并发令牌验证的线程安全性"""
        # 预先生成一些令牌
        valid_tokens = [self.csrf_protection.generate_token() for _ in range(10)]
        validation_results = []
        result_lock = threading.Lock()
        
        def validate_tokens():
            """验证令牌的工作函数"""
            try:
                for token in valid_tokens[:5]:  # 每个线程验证前5个令牌
                    result = self.csrf_protection.validate_token(token)
                    with result_lock:
                        validation_results.append((token, result))
                    time.sleep(0.001)
            except Exception as e:
                self.errors.append(f"Token validation error: {e}")
        
        # 创建多个线程同时验证令牌
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=validate_tokens)
            threads.append(thread)
        
        # 启动所有线程
        for thread in threads:
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证结果
        self.assertEqual(len(self.errors), 0, f"Errors occurred: {self.errors}")
        
        # 由于令牌是一次性的，每个令牌只能被验证成功一次
        successful_validations = [result for _, result in validation_results if result]
        self.assertLessEqual(len(successful_validations), 5, 
                           "Each token should only be validated successfully once")
    
    def test_concurrent_generation_and_validation(self):
        """测试同时进行令牌生成和验证的线程安全性"""
        generated_tokens = []
        validation_results = []
        token_lock = threading.Lock()
        result_lock = threading.Lock()
        
        def generate_tokens():
            """生成令牌的工作函数"""
            try:
                for _ in range(20):
                    token = self.csrf_protection.generate_token()
                    with token_lock:
                        generated_tokens.append(token)
                    time.sleep(0.002)
            except Exception as e:
                self.errors.append(f"Generation error: {e}")
        
        def validate_tokens():
            """验证令牌的工作函数"""
            try:
                for _ in range(15):
                    time.sleep(0.003)  # 稍微延迟以确保有令牌可验证
                    with token_lock:
                        if generated_tokens:
                            token = generated_tokens.pop(0)
                        else:
                            continue
                    
                    result = self.csrf_protection.validate_token(token)
                    with result_lock:
                        validation_results.append(result)
            except Exception as e:
                self.errors.append(f"Validation error: {e}")
        
        # 创建生成和验证线程
        generator_thread = threading.Thread(target=generate_tokens)
        validator_thread = threading.Thread(target=validate_tokens)
        
        # 启动线程
        generator_thread.start()
        validator_thread.start()
        
        # 等待完成
        generator_thread.join()
        validator_thread.join()
        
        # 验证结果
        self.assertEqual(len(self.errors), 0, f"Errors occurred: {self.errors}")
        self.assertGreater(len(validation_results), 0, "Should have some validation results")
    
    def test_cleanup_expired_tokens_thread_safety(self):
        """测试过期令牌清理的线程安全性"""
        # 生成一些令牌
        tokens = [self.csrf_protection.generate_token() for _ in range(10)]
        
        cleanup_results = []
        result_lock = threading.Lock()
        
        def cleanup_tokens():
            """清理过期令牌的工作函数"""
            try:
                result = self.csrf_protection.cleanup_expired_tokens()
                with result_lock:
                    cleanup_results.append(result)
            except Exception as e:
                self.errors.append(f"Cleanup error: {e}")
        
        def generate_more_tokens():
            """在清理过程中生成更多令牌"""
            try:
                for _ in range(5):
                    self.csrf_protection.generate_token()
                    time.sleep(0.001)
            except Exception as e:
                self.errors.append(f"Generation during cleanup error: {e}")
        
        # 同时进行清理和生成操作
        cleanup_thread = threading.Thread(target=cleanup_tokens)
        generator_thread = threading.Thread(target=generate_more_tokens)
        
        cleanup_thread.start()
        generator_thread.start()
        
        cleanup_thread.join()
        generator_thread.join()
        
        # 验证结果
        self.assertEqual(len(self.errors), 0, f"Errors occurred: {self.errors}")
        self.assertEqual(len(cleanup_results), 1, "Should have one cleanup result")
    
    def test_get_active_token_count_thread_safety(self):
        """测试获取活跃令牌数量的线程安全性"""
        counts = []
        count_lock = threading.Lock()
        
        def monitor_token_count():
            """监控令牌数量的工作函数"""
            try:
                for _ in range(10):
                    count = self.csrf_protection.get_active_token_count()
                    with count_lock:
                        counts.append(count)
                    time.sleep(0.001)
            except Exception as e:
                self.errors.append(f"Count monitoring error: {e}")
        
        def modify_tokens():
            """修改令牌的工作函数"""
            try:
                for _ in range(5):
                    token = self.csrf_protection.generate_token()
                    time.sleep(0.001)
                    self.csrf_protection.validate_token(token)
                    time.sleep(0.001)
            except Exception as e:
                self.errors.append(f"Token modification error: {e}")
        
        # 同时监控和修改令牌
        monitor_thread = threading.Thread(target=monitor_token_count)
        modify_thread = threading.Thread(target=modify_tokens)
        
        monitor_thread.start()
        modify_thread.start()
        
        monitor_thread.join()
        modify_thread.join()
        
        # 验证结果
        self.assertEqual(len(self.errors), 0, f"Errors occurred: {self.errors}")
        self.assertEqual(len(counts), 10, "Should have 10 count measurements")
        
        # 所有计数应该是非负数
        for count in counts:
            self.assertGreaterEqual(count, 0, "Token count should never be negative")

if __name__ == '__main__':
    unittest.main()
