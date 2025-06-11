"""
config模块单元测试
测试配置管理和环境变量加载逻辑
"""

import unittest
import os
import logging
from unittest.mock import patch, MagicMock

from backend.config import (
    ConfigManager, ServerConfig, SecurityConfig, WebConfig, FeedbackConfig,
    get_config, get_server_config, get_security_config, get_web_config, get_feedback_config
)


class TestServerConfig(unittest.TestCase):
    """测试ServerConfig dataclass"""

    def test_server_config_default_values(self):
        """测试ServerConfig的默认值"""
        config = ServerConfig()
        
        # 验证新添加的属性的默认值
        self.assertEqual(config.preferred_web_port, 8765)
        self.assertEqual(config.recommended_local_forward_port, 8888)
        
        # 验证其他一些关键默认值
        self.assertEqual(config.port_range_start, 8000)
        self.assertEqual(config.port_range_end, 65535)
        self.assertEqual(config.default_timeout, 300)


class TestConfigManager(unittest.TestCase):
    """测试ConfigManager类"""

    def setUp(self):
        """测试前准备"""
        # 清除全局配置实例，确保每个测试独立
        import backend.config
        backend.config._config_manager = None
        
        # 清除日志处理器以避免测试间干扰
        logging.getLogger().handlers.clear()

    def test_config_manager_initialization(self):
        """测试ConfigManager初始化"""
        config_manager = ConfigManager()
        
        # 验证所有配置对象都被正确创建
        self.assertIsInstance(config_manager.security, SecurityConfig)
        self.assertIsInstance(config_manager.server, ServerConfig)
        self.assertIsInstance(config_manager.web, WebConfig)
        self.assertIsInstance(config_manager.feedback, FeedbackConfig)
        
        # 验证默认值
        self.assertEqual(config_manager.server.preferred_web_port, 8765)
        self.assertEqual(config_manager.server.recommended_local_forward_port, 8888)

    @patch('os.getenv')
    def test_load_from_env_preferred_port_valid(self, mock_getenv):
        """测试场景1：MCP_FEEDBACK_PREFERRED_PORT设置了有效的整数值"""
        # 设置模拟环境变量
        def mock_env_side_effect(key, default=None):
            env_vars = {
                'MCP_FEEDBACK_PREFERRED_PORT': '9000',
                'MCP_FEEDBACK_LOCAL_FORWARD_PORT': '9001'
            }
            return env_vars.get(key, default)
        
        mock_getenv.side_effect = mock_env_side_effect
        
        config_manager = ConfigManager()
        
        # 验证配置被正确更新
        self.assertEqual(config_manager.server.preferred_web_port, 9000)
        self.assertEqual(config_manager.server.recommended_local_forward_port, 9001)

    @patch('os.getenv')
    @patch('logging.warning')
    def test_load_from_env_preferred_port_invalid(self, mock_logging_warning, mock_getenv):
        """测试场景2：MCP_FEEDBACK_PREFERRED_PORT设置了无效值"""
        # 设置模拟环境变量
        def mock_env_side_effect(key, default=None):
            env_vars = {
                'MCP_FEEDBACK_PREFERRED_PORT': 'invalid_port',
                'MCP_FEEDBACK_LOCAL_FORWARD_PORT': 'also_invalid'
            }
            return env_vars.get(key, default)
        
        mock_getenv.side_effect = mock_env_side_effect
        
        config_manager = ConfigManager()
        
        # 验证配置保持默认值
        self.assertEqual(config_manager.server.preferred_web_port, 8765)
        self.assertEqual(config_manager.server.recommended_local_forward_port, 8888)
        
        # 验证记录了警告日志
        expected_calls = [
            unittest.mock.call(
                "环境变量 MCP_FEEDBACK_PREFERRED_PORT 的值 'invalid_port' 不是有效整数，"
                "将使用默认值 8765。"
            ),
            unittest.mock.call(
                "环境变量 MCP_FEEDBACK_LOCAL_FORWARD_PORT 的值 'also_invalid' 不是有效整数，"
                "将使用默认值 8888。"
            )
        ]
        mock_logging_warning.assert_has_calls(expected_calls)

    @patch('os.getenv')
    def test_load_from_env_ports_not_set(self, mock_getenv):
        """测试场景3：环境变量未设置"""
        # 模拟环境变量未设置
        mock_getenv.return_value = None
        
        config_manager = ConfigManager()
        
        # 验证配置保持默认值
        self.assertEqual(config_manager.server.preferred_web_port, 8765)
        self.assertEqual(config_manager.server.recommended_local_forward_port, 8888)

    @patch('os.getenv')
    def test_load_from_env_other_configs(self, mock_getenv):
        """测试其他配置项的环境变量加载"""
        # 设置模拟环境变量
        def mock_env_side_effect(key, default=None):
            env_vars = {
                'MCP_MAX_CONTENT_LENGTH': '32000000',  # 32MB
                'MCP_PORT_START': '9000',
                'MCP_DEFAULT_TIMEOUT': '600',
                'MCP_DEBUG': 'true'
            }
            return env_vars.get(key, default)
        
        mock_getenv.side_effect = mock_env_side_effect
        
        config_manager = ConfigManager()
        
        # 验证各种配置都被正确加载
        self.assertEqual(config_manager.security.max_content_length, 32000000)
        self.assertEqual(config_manager.server.port_range_start, 9000)
        self.assertEqual(config_manager.server.default_timeout, 600)
        self.assertTrue(config_manager.web.debug_mode)

    @patch('os.getenv')
    @patch('logging.warning')
    def test_load_from_env_mixed_valid_invalid(self, mock_logging_warning, mock_getenv):
        """测试混合的有效和无效环境变量"""
        # 设置模拟环境变量：一个有效，一个无效
        def mock_env_side_effect(key, default=None):
            env_vars = {
                'MCP_FEEDBACK_PREFERRED_PORT': '9000',  # 有效
                'MCP_FEEDBACK_LOCAL_FORWARD_PORT': 'invalid'  # 无效
            }
            return env_vars.get(key, default)
        
        mock_getenv.side_effect = mock_env_side_effect
        
        config_manager = ConfigManager()
        
        # 验证有效的被设置，无效的保持默认值
        self.assertEqual(config_manager.server.preferred_web_port, 9000)
        self.assertEqual(config_manager.server.recommended_local_forward_port, 8888)
        
        # 验证只记录了无效值的警告
        mock_logging_warning.assert_called_once_with(
            "环境变量 MCP_FEEDBACK_LOCAL_FORWARD_PORT 的值 'invalid' 不是有效整数，"
            "将使用默认值 8888。"
        )

    def test_validate_config_success(self):
        """测试配置验证成功"""
        config_manager = ConfigManager()
        
        result = config_manager.validate_config()
        
        self.assertTrue(result)

    def test_validate_config_invalid_port_range(self):
        """测试无效端口范围"""
        config_manager = ConfigManager()
        config_manager.server.port_range_start = 9000
        config_manager.server.port_range_end = 8000  # 结束值小于开始值
        
        with patch('builtins.print') as mock_print:
            result = config_manager.validate_config()
        
        self.assertFalse(result)
        mock_print.assert_called_with("配置验证失败: 端口范围配置无效")

    def test_to_dict(self):
        """测试配置转换为字典"""
        config_manager = ConfigManager()
        
        config_dict = config_manager.to_dict()
        
        # 验证字典结构
        self.assertIn('server', config_dict)
        self.assertIn('security', config_dict)
        self.assertIn('web', config_dict)
        self.assertIn('feedback', config_dict)
        
        # 验证新属性在字典中
        server_config = config_dict['server']
        self.assertEqual(server_config['preferred_web_port'], 8765)
        self.assertEqual(server_config['recommended_local_forward_port'], 8888)


class TestGlobalConfigFunctions(unittest.TestCase):
    """测试全局配置访问函数"""

    def setUp(self):
        """测试前准备"""
        # 清除全局配置实例
        import backend.config
        backend.config._config_manager = None

    def test_get_config(self):
        """测试获取全局配置管理器"""
        config = get_config()
        
        self.assertIsInstance(config, ConfigManager)
        
        # 验证单例模式
        config2 = get_config()
        self.assertIs(config, config2)

    def test_get_server_config(self):
        """测试获取服务器配置"""
        server_config = get_server_config()
        
        self.assertIsInstance(server_config, ServerConfig)
        self.assertEqual(server_config.preferred_web_port, 8765)
        self.assertEqual(server_config.recommended_local_forward_port, 8888)

    def test_get_security_config(self):
        """测试获取安全配置"""
        security_config = get_security_config()
        
        self.assertIsInstance(security_config, SecurityConfig)

    def test_get_web_config(self):
        """测试获取Web配置"""
        web_config = get_web_config()
        
        self.assertIsInstance(web_config, WebConfig)

    def test_get_feedback_config(self):
        """测试获取反馈配置"""
        feedback_config = get_feedback_config()
        
        self.assertIsInstance(feedback_config, FeedbackConfig)

    @patch.object(ConfigManager, 'validate_config', return_value=False)
    def test_get_config_validation_failure(self, mock_validate):
        """测试配置验证失败时抛出异常"""
        with self.assertRaises(RuntimeError) as context:
            get_config()
        
        self.assertIn("配置验证失败，请检查配置项", str(context.exception))


class TestConfigIntegration(unittest.TestCase):
    """配置管理集成测试"""

    def setUp(self):
        """测试前准备"""
        # 清除全局配置实例
        import backend.config
        backend.config._config_manager = None

    @patch.dict(os.environ, {
        'MCP_FEEDBACK_PREFERRED_PORT': '9999',
        'MCP_FEEDBACK_LOCAL_FORWARD_PORT': '8888',
        'MCP_DEBUG': 'true'
    })
    def test_full_config_loading_cycle(self):
        """测试完整的配置加载周期"""
        # 获取配置
        config = get_config()
        
        # 验证环境变量被正确加载
        self.assertEqual(config.server.preferred_web_port, 9999)
        self.assertEqual(config.server.recommended_local_forward_port, 8888)
        self.assertTrue(config.web.debug_mode)
        
        # 验证配置有效
        self.assertTrue(config.validate_config())
        
        # 验证配置可以转换为字典
        config_dict = config.to_dict()
        self.assertEqual(config_dict['server']['preferred_web_port'], 9999)


if __name__ == '__main__':
    unittest.main()