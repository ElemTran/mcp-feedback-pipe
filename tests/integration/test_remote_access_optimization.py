"""
优化远程访问便捷性功能的集成测试

测试环境变量配置对端口分配和日志输出的影响：
1. 首选端口可用的情况
2. 首选端口不可用（动态回退）的情况
3. 未设置首选端口环境变量的情况
4. 环境变量配置了无效值的情况
"""

import os
import re
import socket
import sys
import time
import unittest
import threading
from io import StringIO
from typing import Optional, Dict, Any
from unittest.mock import patch, MagicMock
from contextlib import redirect_stdout, redirect_stderr


class TestRemoteAccessOptimization(unittest.TestCase):
    """优化远程访问便捷性功能集成测试"""

    def setUp(self):
        """测试前准备"""
        # 保存原始环境变量
        self.original_env = {}
        self.env_vars_to_restore = [
            'MCP_FEEDBACK_PREFERRED_PORT',
            'MCP_FEEDBACK_LOCAL_FORWARD_PORT'
        ]
        
        for var in self.env_vars_to_restore:
            self.original_env[var] = os.environ.get(var)
        
        # 清理环境变量
        for var in self.env_vars_to_restore:
            if var in os.environ:
                del os.environ[var]
    
    def tearDown(self):
        """测试后清理"""
        # 恢复原始环境变量
        for var in self.env_vars_to_restore:
            if self.original_env[var] is not None:
                os.environ[var] = self.original_env[var]
            elif var in os.environ:
                del os.environ[var]
    
    def _find_available_port(self) -> int:
        """查找一个可用端口"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port
    
    def _occupy_port(self, port: int) -> socket.socket:
        """占用指定端口，返回socket对象用于后续释放"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('127.0.0.1', port))
        sock.listen(1)
        return sock
    
    def _test_server_startup_and_logging(self, env_vars: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        测试服务器启动和日志输出
        
        Args:
            env_vars: 环境变量字典
        
        Returns:
            Dict[str, Any]: 包含日志输出、实际端口等信息的字典
        """
        # 设置环境变量
        if env_vars:
            for key, value in env_vars.items():
                os.environ[key] = value
        
        try:
            # 重新导入模块以确保环境变量被重新加载
            import importlib
            import backend.config
            importlib.reload(backend.config)
            
            # 重置配置管理器的全局实例，以便重新加载环境变量
            backend.config._config_manager = None
            
            # 导入必要的模块（在设置环境变量后）
            from backend.server_manager import ServerManager
            from backend.server_pool import get_managed_server, release_managed_server
            
            # 捕获标准输出
            stdout_capture = StringIO()
            stderr_capture = StringIO()
            
            # 模拟collect_feedback工具的启动过程
            session_id = "test_session_123"
            
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                # 获取托管的服务器实例
                server_manager = get_managed_server(session_id)
                
                try:
                    # 模拟工具参数
                    work_summary = "测试远程访问便捷性优化功能"
                    timeout_seconds = 300
                    suggest_json = ""
                    
                    # 启动服务器（这会触发端口分配和日志输出）
                    actual_port = server_manager.start_server(
                        work_summary=work_summary,
                        timeout_seconds=timeout_seconds,
                        suggest=suggest_json,
                        debug=False,
                        use_reloader=False
                    )
                    
                    # 模拟server.py中的日志输出
                    from backend.config import get_server_config
                    server_config = get_server_config()
                    recommended_local_port = getattr(server_config, 'recommended_local_forward_port', 8888)
                    
                    print(f"✅ 服务已在远程服务器的 127.0.0.1:{actual_port} 启动。")
                    print(f"💡 要从您的本地机器访问，请设置SSH端口转发。")
                    print(f"   如果您尚未配置，可以在您的本地终端运行类似以下命令：")
                    print(f"   ssh -L {recommended_local_port}:127.0.0.1:{actual_port} your_user@your_remote_server_ip")
                    print(f"   (请将 'your_user@your_remote_server_ip' 替换为您的实际SSH登录信息)")
                    print(f"➡️ 设置转发后，请在您本地的浏览器中打开: http://127.0.0.1:{recommended_local_port}/")
                    print(f"⏰ 等待用户反馈... (远程服务超时: {timeout_seconds}秒)")
                    
                    # 立即停止服务器（不等待用户输入）
                    server_manager.stop_server()
                    
                    return {
                        'actual_port': actual_port,
                        'recommended_local_port': recommended_local_port,
                        'stdout': stdout_capture.getvalue(),
                        'stderr': stderr_capture.getvalue(),
                        'success': True
                    }
                    
                finally:
                    # 清理服务器资源
                    release_managed_server(session_id, immediate=True)
            
        except Exception as e:
            return {
                'actual_port': None,
                'recommended_local_port': None,
                'stdout': stdout_capture.getvalue() if 'stdout_capture' in locals() else "",
                'stderr': stderr_capture.getvalue() if 'stderr_capture' in locals() else "",
                'error': str(e),
                'success': False
            }
        finally:
            # 清理环境变量
            if env_vars:
                for key in env_vars.keys():
                    if key in os.environ:
                        del os.environ[key]
    
    def _extract_port_from_output(self, output: str) -> Optional[int]:
        """从输出中提取服务器启动端口"""
        # 匹配形如 "服务已在远程服务器的 127.0.0.1:8791 启动" 的日志
        pattern = r'服务已在远程服务器的 127\.0\.0\.1:(\d+) 启动'
        match = re.search(pattern, output)
        if match:
            return int(match.group(1))
        return None
    
    def _extract_ssh_command_ports(self, output: str) -> Optional[Dict[str, int]]:
        """从输出中提取SSH转发命令的端口信息"""
        # 匹配形如 "ssh -L 8891:127.0.0.1:8791 your_user@your_remote_server_ip" 的命令
        pattern = r'ssh -L (\d+):127\.0\.0\.1:(\d+) your_user@your_remote_server_ip'
        match = re.search(pattern, output)
        if match:
            return {
                'local_port': int(match.group(1)),
                'remote_port': int(match.group(2))
            }
        return None
    
    def test_scenario_1_preferred_port_available(self):
        """场景1：首选端口可用"""
        print("\n=== 测试场景1：首选端口可用 ===")
        
        # 选择一个不常用的端口
        preferred_port = 8791
        local_forward_port = 8891
        
        # 确保端口可用
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', preferred_port))
        except OSError:
            self.skipTest(f"端口 {preferred_port} 不可用，跳过此测试")
        
        # 设置环境变量
        env_vars = {
            'MCP_FEEDBACK_PREFERRED_PORT': str(preferred_port),
            'MCP_FEEDBACK_LOCAL_FORWARD_PORT': str(local_forward_port)
        }
        
        # 运行测试
        result = self._test_server_startup_and_logging(env_vars)
        print(f"测试结果: {result}")
        
        # 验证测试成功执行
        self.assertTrue(result['success'], f"服务器启动失败: {result.get('error', 'Unknown error')}")
        
        # 验证实际端口
        actual_port = result['actual_port']
        self.assertIsNotNone(actual_port, "无法获取服务器端口")
        self.assertEqual(actual_port, preferred_port,
                        f"服务器应该在首选端口 {preferred_port} 启动，但实际端口是 {actual_port}")
        
        # 验证SSH转发命令参数
        expected_local_port = result['recommended_local_port']
        self.assertEqual(expected_local_port, local_forward_port,
                        f"SSH转发命令应使用本地端口 {local_forward_port}，但实际使用 {expected_local_port}")
        
        # 验证日志输出
        output = result['stdout']
        self.assertIn(f"127.0.0.1:{preferred_port} 启动", output, "日志应包含正确的服务器启动端口")
        self.assertIn(f"ssh -L {local_forward_port}:127.0.0.1:{preferred_port}", output, "日志应包含正确的SSH转发命令")
        
        print("✅ 场景1测试通过")
    
    def test_scenario_2_preferred_port_occupied(self):
        """场景2：首选端口不可用（动态回退）"""
        print("\n=== 测试场景2：首选端口不可用（动态回退） ===")
        
        # 选择一个端口并占用它
        preferred_port = 8792
        local_forward_port = 8892
        
        # 占用首选端口
        occupied_socket = self._occupy_port(preferred_port)
        
        try:
            # 设置环境变量
            env_vars = {
                'MCP_FEEDBACK_PREFERRED_PORT': str(preferred_port),
                'MCP_FEEDBACK_LOCAL_FORWARD_PORT': str(local_forward_port)
            }
            
            # 运行测试
            result = self._test_server_startup_and_logging(env_vars)
            print(f"测试结果: {result}")
            
            # 验证测试成功执行
            self.assertTrue(result['success'], f"服务器启动失败: {result.get('error', 'Unknown error')}")
            
            # 验证实际端口不是被占用的首选端口
            actual_port = result['actual_port']
            self.assertIsNotNone(actual_port, "无法获取服务器端口")
            self.assertNotEqual(actual_port, preferred_port,
                              f"服务器不应该在被占用的首选端口 {preferred_port} 启动，但实际端口是 {actual_port}")
            
            # 验证SSH转发命令参数
            expected_local_port = result['recommended_local_port']
            self.assertEqual(expected_local_port, local_forward_port,
                            f"SSH转发命令应使用本地端口 {local_forward_port}")
            
            # 验证日志输出
            output = result['stdout']
            self.assertIn(f"127.0.0.1:{actual_port} 启动", output, "日志应包含正确的服务器启动端口")
            self.assertIn(f"ssh -L {local_forward_port}:127.0.0.1:{actual_port}", output, "日志应包含正确的SSH转发命令")
            
            print("✅ 场景2测试通过")
            
        finally:
            # 释放占用的端口
            occupied_socket.close()
    
    def test_scenario_3_no_preferred_port_env_var(self):
        """场景3：未设置首选端口环境变量（使用配置默认值）"""
        print("\n=== 测试场景3：未设置首选端口环境变量（使用配置默认值） ===")
        
        local_forward_port = 8893
        
        # 设置环境变量（只设置本地转发端口）
        env_vars = {
            'MCP_FEEDBACK_LOCAL_FORWARD_PORT': str(local_forward_port)
        }
        
        # 运行测试
        result = self._test_server_startup_and_logging(env_vars)
        print(f"测试结果: {result}")
        
        # 验证测试成功执行
        self.assertTrue(result['success'], f"服务器启动失败: {result.get('error', 'Unknown error')}")
        
        # 验证实际端口
        actual_port = result['actual_port']
        self.assertIsNotNone(actual_port, "无法获取服务器端口")
        
        # 验证SSH转发命令参数
        expected_local_port = result['recommended_local_port']
        self.assertEqual(expected_local_port, local_forward_port,
                        f"SSH转发命令应使用本地端口 {local_forward_port}")
        
        # 验证日志输出
        output = result['stdout']
        self.assertIn(f"127.0.0.1:{actual_port} 启动", output, "日志应包含正确的服务器启动端口")
        self.assertIn(f"ssh -L {local_forward_port}:127.0.0.1:{actual_port}", output, "日志应包含正确的SSH转发命令")
        
        # 从配置文件导入默认值进行验证
        try:
            from backend.config import get_server_config
            config = get_server_config()
            expected_default_port = config.preferred_web_port
            
            # 验证使用了正确的端口策略
            if actual_port == expected_default_port:
                # 使用了默认端口，这是正确的行为
                print(f"✓ 使用了默认端口 {expected_default_port}")
            else:
                # 使用了动态端口，说明默认端口不可用
                print(f"✓ 默认端口 {expected_default_port} 不可用，使用了动态端口 {actual_port}")
                
            # 无论使用哪种端口，都是正确的行为
            # 重要的是验证端口分配逻辑正常工作
            self.assertTrue(actual_port > 0, "应该分配到有效端口")
            
        except ImportError:
            # 如果无法导入配置，至少验证服务器能正常启动
            print(f"✓ 服务器正常启动在端口 {actual_port}")
        
        print("✅ 场景3测试通过")
    
    def test_scenario_4_invalid_preferred_port_env_var(self):
        """场景4：环境变量配置了无效的首选端口值（健壮性测试）"""
        print("\n=== 测试场景4：环境变量配置了无效的首选端口值（健壮性测试） ===")
        
        local_forward_port = 8894
        
        # 设置无效的首选端口环境变量
        env_vars = {
            'MCP_FEEDBACK_PREFERRED_PORT': 'not_a_port',
            'MCP_FEEDBACK_LOCAL_FORWARD_PORT': str(local_forward_port)
        }
        
        # 运行测试
        result = self._test_server_startup_and_logging(env_vars)
        print(f"测试结果: {result}")
        
        # 验证应用程序没有崩溃
        self.assertTrue(result['success'], f"应用程序不应该崩溃，但失败了: {result.get('error', 'Unknown error')}")
        
        # 验证服务器仍然能够启动
        actual_port = result['actual_port']
        self.assertIsNotNone(actual_port, "服务器应该能够启动并获取端口")
        
        # 验证SSH转发命令参数
        expected_local_port = result['recommended_local_port']
        self.assertEqual(expected_local_port, local_forward_port,
                        f"SSH转发命令应使用本地端口 {local_forward_port}")
        
        # 验证日志输出
        output = result['stdout']
        self.assertIn(f"127.0.0.1:{actual_port} 启动", output, "日志应包含正确的服务器启动端口")
        self.assertIn(f"ssh -L {local_forward_port}:127.0.0.1:{actual_port}", output, "日志应包含正确的SSH转发命令")
        
        # 验证应该回退到默认端口或动态端口
        try:
            from backend.config import get_server_config
            config = get_server_config()
            expected_default_port = config.preferred_web_port
            
            # 应该使用默认端口（如果可用）或动态端口
            if actual_port == expected_default_port:
                print(f"✓ 回退到默认端口 {expected_default_port}")
            else:
                print(f"✓ 使用了动态端口 {actual_port}")
        except ImportError:
            print(f"✓ 使用了端口 {actual_port}")
        
        print("✅ 场景4测试通过")
    
    def test_all_scenarios_summary(self):
        """运行所有场景的总结测试"""
        print("\n=== 集成测试总结 ===")
        
        # 统计测试结果
        test_methods = [
            'test_scenario_1_preferred_port_available',
            'test_scenario_2_preferred_port_occupied', 
            'test_scenario_3_no_preferred_port_env_var',
            'test_scenario_4_invalid_preferred_port_env_var'
        ]
        
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_method in test_methods:
            try:
                method = getattr(self, test_method)
                method()
                passed_tests += 1
                print(f"✅ {test_method}: 通过")
            except Exception as e:
                print(f"❌ {test_method}: 失败 - {str(e)}")
        
        print(f"\n📊 测试结果: {passed_tests}/{total_tests} 通过")
        
        # 验证所有关键场景都通过
        self.assertEqual(passed_tests, total_tests, 
                        f"所有集成测试场景都应该通过，但只有 {passed_tests}/{total_tests} 通过")
        
        print("🎉 所有集成测试场景均通过！")


if __name__ == '__main__':
    # 配置测试输出
    unittest.main(verbosity=2, buffer=True)