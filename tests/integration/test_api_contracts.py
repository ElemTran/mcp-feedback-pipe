#!/usr/bin/env python3
"""
API契约测试 - 验证API端点的存在性和不存在性
从 test_stage3_frontend_optimization.py 迁移的API不存在性检查逻辑
"""

import pytest
import requests
import time
from backend.server_manager import ServerManager

class TestAPIContracts:
    """API契约验证测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        self.server_manager = ServerManager()
        self.port = None
        self.base_url = None
    
    def teardown_method(self):
        """测试后置清理"""
        if self.server_manager:
            try:
                self.server_manager.stop_server()
            except:
                pass
    
    def test_removed_apis_return_404(self):
        """验证已移除的API端点返回404状态码"""
        # 启动测试服务器
        self.port = self.server_manager.start_server("API契约测试", timeout_seconds=30)
        self.base_url = f'http://127.0.0.1:{self.port}'
        
        # 等待服务器完全启动
        time.sleep(3)
        
        # 验证已移除的API不存在
        removed_apis = [
            ('/api/update_timeout', 'POST'),
            ('/api/user_activity', 'POST')
        ]
        
        for api_path, method in removed_apis:
            try:
                if method == 'POST':
                    response = requests.post(f'{self.base_url}{api_path}', json={})
                else:
                    response = requests.get(f'{self.base_url}{api_path}')
                
                # 验证返回404状态码
                assert response.status_code == 404, f"{method} {api_path} 应该返回404，实际返回 {response.status_code}"
                
            except requests.exceptions.ConnectionError:
                # 连接错误也表示API不存在，这是正确的
                pass
            except Exception as e:
                pytest.fail(f"验证 {method} {api_path} 时出现意外错误: {e}")
    
    def test_core_endpoints_availability(self):
        """验证核心API端点的可用性"""
        # 启动测试服务器
        self.port = self.server_manager.start_server("核心API测试", timeout_seconds=30)
        self.base_url = f'http://127.0.0.1:{self.port}'
        
        # 等待服务器完全启动
        time.sleep(3)
        
        # 验证核心端点正常工作
        core_endpoints = [
            ('/', 'GET', '主页'),
            ('/ping', 'GET', '健康检查'),
            ('/static/js/modules/timeout-handler.js', 'GET', '超时处理模块')
        ]
        
        for endpoint, method, name in core_endpoints:
            try:
                if method == 'GET':
                    response = requests.get(f'{self.base_url}{endpoint}')
                
                # 验证返回200状态码
                assert response.status_code == 200, f"{name} ({method} {endpoint}) 应该返回200，实际返回 {response.status_code}"
                
            except Exception as e:
                pytest.fail(f"验证 {name} ({method} {endpoint}) 时出现错误: {e}")
    
    def test_frontend_optimization_artifacts(self):
        """验证前端优化相关的文件和内容"""
        # 启动测试服务器
        self.port = self.server_manager.start_server("前端优化验证", timeout_seconds=30)
        self.base_url = f'http://127.0.0.1:{self.port}'
        
        # 等待服务器完全启动
        time.sleep(3)
        
        try:
            # 验证主页加载并包含必要的JavaScript模块
            response = requests.get(f'{self.base_url}/')
            assert response.status_code == 200, "主页应该正常加载"
            
            content = response.text
            
            # 检查页面内容包含必要的JavaScript模块引用
            assert 'timeout-handler.js' in content, "页面应该包含timeout-handler.js模块引用"
            assert 'timeoutData' in content, "页面应该包含超时数据元素"
            
        except Exception as e:
            pytest.fail(f"验证前端优化内容时出现错误: {e}")

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
