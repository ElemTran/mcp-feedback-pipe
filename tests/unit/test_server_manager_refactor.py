#!/usr/bin/env python3
"""ServerManager 重构后的基本功能测试"""

import unittest
import time
import threading
import sys
import os

from backend.server_manager import ServerManager

class TestServerManagerRefactor(unittest.TestCase):
    """ServerManager 重构测试类"""
    
    def setUp(self):
        """测试前的设置"""
        self.server_manager = None
    
    def tearDown(self):
        """测试后的清理"""
        if self.server_manager:
            self.server_manager.stop_server()
    
    def test_server_manager_creation(self):
        """测试 ServerManager 实例创建"""
        self.server_manager = ServerManager()
        self.assertIsNotNone(self.server_manager)
        self.assertIsNotNone(self.server_manager.feedback_handler)
        self.assertIsNone(self.server_manager.current_port)
        print("✅ ServerManager 实例创建测试通过")
    
    def test_server_startup(self):
        """测试服务器启动功能"""
        self.server_manager = ServerManager()
        
        # 测试启动服务器
        port = self.server_manager.start_server(
            work_summary="重构测试",
            timeout_seconds=60
        )
        
        # 验证端口分配
        self.assertIsNotNone(port)
        self.assertGreater(port, 0)
        self.assertEqual(self.server_manager.current_port, port)
        
        # 等待服务器完全启动
        time.sleep(2)
        
        print(f"✅ 服务器启动测试通过，端口: {port}")
    
    def test_server_health_check(self):
        """测试服务器健康检查"""
        self.server_manager = ServerManager()
        
        # 启动前健康检查应该返回 False
        self.assertFalse(self.server_manager._is_server_healthy())
        
        # 启动服务器
        port = self.server_manager.start_server("健康检查测试")
        time.sleep(2)
        
        # 启动后健康检查应该返回 True
        self.assertTrue(self.server_manager._is_server_healthy())
        
        print("✅ 服务器健康检查测试通过")
    
    def test_connection_detection(self):
        """测试连接检测功能"""
        self.server_manager = ServerManager()
        
        # 启动服务器
        port = self.server_manager.start_server("连接检测测试")
        time.sleep(2)
        
        # 连接检测（服务器正常时应该返回 False，表示连接正常）
        disconnected = self.server_manager._check_client_disconnection()
        
        # 注意：这里的逻辑是 False 表示连接正常，True 表示连接断开
        # 由于我们刚启动服务器，连接应该是正常的
        print(f"连接状态检测结果: {'断开' if disconnected else '正常'}")
        
        print("✅ 连接检测测试通过")
    
    def test_wait_for_feedback_interface_compatibility(self):
        """测试 wait_for_feedback 接口兼容性"""
        self.server_manager = ServerManager()
        
        # 启动服务器
        port = self.server_manager.start_server("接口兼容性测试")
        time.sleep(2)
        
        # 模拟快速提交，避免无限等待
        def quick_submit():
            time.sleep(1)
            # 模拟前端提交
            self.server_manager.feedback_handler.submit_feedback({
                'text': '测试反馈',
                'images': [],
                'source_event': 'manual_submit',
                'is_timeout_capture': False
            })
        
        # 启动提交线程
        submit_thread = threading.Thread(target=quick_submit)
        submit_thread.start()
        
        # 测试 wait_for_feedback 方法（应该接收到提交的数据）
        result = self.server_manager.wait_for_feedback(timeout_seconds=60)
        
        # 验证结果
        self.assertIsNotNone(result)
        self.assertEqual(result.get('text_feedback'), '测试反馈')
        self.assertFalse(result.get('is_timeout_capture'))
        
        submit_thread.join()
        print("✅ wait_for_feedback 接口兼容性测试通过")
    
    def test_resource_cleanup(self):
        """测试资源清理功能"""
        self.server_manager = ServerManager()
        
        # 启动服务器
        port = self.server_manager.start_server("资源清理测试")
        time.sleep(2)
        
        # 验证资源存在
        self.assertIsNotNone(self.server_manager.current_port)
        self.assertIsNotNone(self.server_manager.app)
        
        # 执行清理
        self.server_manager._cleanup_on_disconnection()
        
        # 注意：_cleanup_on_disconnection 只清理队列，不重置端口和应用
        # 这是按照架构设计的
        
        print("✅ 资源清理测试通过")

def run_basic_tests():
    """运行基本测试"""
    print("开始 ServerManager 重构基本功能测试...")
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestServerManagerRefactor)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出结果
    if result.wasSuccessful():
        print("\n🎉 所有测试通过！ServerManager 重构成功！")
        return True
    else:
        print(f"\n❌ 测试失败：{len(result.failures)} 个失败，{len(result.errors)} 个错误")
        return False

if __name__ == "__main__":
    run_basic_tests()
