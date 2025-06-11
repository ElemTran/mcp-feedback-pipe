"""
network_utils模块单元测试
测试网络相关工具函数
"""

import unittest
import socket
import logging
from unittest.mock import patch, MagicMock, call

from backend.utils.network_utils import find_free_port, _test_port_availability


class TestFindFreePort(unittest.TestCase):
    """测试find_free_port函数"""

    def setUp(self):
        """测试前准备"""
        # 清除日志处理器以避免测试间干扰
        logging.getLogger('backend.utils.network_utils').handlers.clear()

    @patch('backend.utils.network_utils._test_port_availability')
    def test_find_free_port_with_available_preferred_port(self, mock_test_port):
        """测试场景1：提供可用的preferred_port时，应返回该端口"""
        # 设置模拟：首选端口可用
        mock_test_port.return_value = True
        
        # 使用info级别的日志来验证日志记录
        with patch('backend.utils.network_utils.logger') as mock_logger:
            result = find_free_port(preferred_port=8080)
        
        # 验证返回结果
        self.assertEqual(result, 8080)
        
        # 验证调用了端口可用性测试
        mock_test_port.assert_called_once_with(8080, 0.1)
        
        # 验证记录了正确的日志
        mock_logger.info.assert_has_calls([
            call("尝试使用首选端口: 8080"),
            call("首选端口 8080 可用。")
        ])

    @patch('backend.utils.network_utils._test_port_availability')
    @patch('backend.utils.network_utils.socket.socket')
    @patch('backend.utils.network_utils.time.sleep')
    def test_find_free_port_with_unavailable_preferred_port(self, mock_sleep, mock_socket, mock_test_port):
        """测试场景2：提供不可用的preferred_port时，应记录警告并回退到动态查找"""
        # 设置模拟：首选端口不可用，但动态查找的端口可用
        mock_test_port.side_effect = [False, True]  # 第一次False（首选端口），第二次True（动态端口）
        
        # 模拟socket行为
        mock_sock = MagicMock()
        mock_sock.getsockname.return_value = ('127.0.0.1', 9090)
        mock_socket.return_value.__enter__.return_value = mock_sock
        
        with patch('backend.utils.network_utils.logger') as mock_logger:
            result = find_free_port(preferred_port=8080)
        
        # 验证返回动态查找的端口
        self.assertEqual(result, 9090)
        
        # 验证调用了端口可用性测试
        self.assertEqual(mock_test_port.call_count, 2)
        mock_test_port.assert_any_call(8080, 0.1)  # 首选端口测试
        mock_test_port.assert_any_call(9090, 0.1)  # 动态端口测试
        
        # 验证记录了警告日志
        mock_logger.warning.assert_called_with(
            "首选端口 8080 当前不可用或已被占用，将尝试动态查找其他端口..."
        )

    @patch('backend.utils.network_utils._test_port_availability')
    @patch('backend.utils.network_utils.socket.socket')
    def test_find_free_port_without_preferred_port(self, mock_socket, mock_test_port):
        """测试场景3：不提供preferred_port时，应执行动态端口查找逻辑"""
        # 设置模拟：动态查找的端口可用
        mock_test_port.return_value = True
        
        # 模拟socket行为
        mock_sock = MagicMock()
        mock_sock.getsockname.return_value = ('127.0.0.1', 7777)
        mock_socket.return_value.__enter__.return_value = mock_sock
        
        result = find_free_port()
        
        # 验证返回动态查找的端口
        self.assertEqual(result, 7777)
        
        # 验证调用了端口可用性测试（只测试动态端口）
        mock_test_port.assert_called_once_with(7777, 0.1)
        
        # 验证socket操作
        mock_sock.bind.assert_called_once_with(("", 0))
        mock_sock.listen.assert_called_once_with(1)

    @patch('backend.utils.network_utils._test_port_availability')
    @patch('backend.utils.network_utils.socket.socket')
    @patch('backend.utils.network_utils.time.sleep')
    def test_find_free_port_multiple_retries(self, mock_sleep, mock_socket, mock_test_port):
        """测试多次重试机制"""
        # 设置模拟：前两次端口可用性测试失败，第三次成功
        mock_test_port.side_effect = [False, False, True]
        
        # 模拟socket行为
        mock_sock = MagicMock()
        mock_sock.getsockname.side_effect = [
            ('127.0.0.1', 5555),
            ('127.0.0.1', 6666),
            ('127.0.0.1', 7777)
        ]
        mock_socket.return_value.__enter__.return_value = mock_sock
        
        with patch('backend.utils.network_utils.logger') as mock_logger:
            result = find_free_port(max_retries=3)
        
        # 验证返回最后成功的端口
        self.assertEqual(result, 7777)
        
        # 验证重试了正确的次数
        self.assertEqual(mock_test_port.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)  # 前两次失败后睡眠
        
        # 验证记录了警告日志
        mock_logger.warning.assert_has_calls([
            call("端口 5555 可用性测试失败，重试 (尝试 1/3)"),
            call("端口 6666 可用性测试失败，重试 (尝试 2/3)")
        ])

    @patch('backend.utils.network_utils._test_port_availability')
    @patch('backend.utils.network_utils.socket.socket')
    @patch('backend.utils.network_utils.time.sleep')
    def test_find_free_port_all_retries_failed(self, mock_sleep, mock_socket, mock_test_port):
        """测试所有重试都失败的情况"""
        # 设置模拟：所有端口可用性测试都失败
        mock_test_port.return_value = False
        
        # 模拟socket行为
        mock_sock = MagicMock()
        mock_sock.getsockname.return_value = ('127.0.0.1', 5555)
        mock_socket.return_value.__enter__.return_value = mock_sock
        
        # 验证抛出RuntimeError
        with self.assertRaises(RuntimeError) as context:
            find_free_port(max_retries=2)
        
        self.assertIn("无法找到可用端口，已重试 2 次", str(context.exception))

    @patch('backend.utils.network_utils.socket.socket')
    @patch('backend.utils.network_utils.time.sleep')
    def test_find_free_port_socket_error(self, mock_sleep, mock_socket):
        """测试socket错误处理"""
        # 设置模拟：socket操作抛出异常
        mock_socket.return_value.__enter__.side_effect = [
            socket.error("Socket error"),
            MagicMock()
        ]
        
        # 第二次尝试成功
        mock_sock = MagicMock()
        mock_sock.getsockname.return_value = ('127.0.0.1', 8888)
        mock_socket.return_value.__enter__.side_effect = [
            socket.error("Socket error"),
            mock_sock
        ]
        
        with patch('backend.utils.network_utils._test_port_availability', return_value=True):
            with patch('backend.utils.network_utils.logger') as mock_logger:
                result = find_free_port(max_retries=2)
        
        # 验证最终成功获取端口
        self.assertEqual(result, 8888)
        
        # 验证记录了错误日志
        mock_logger.warning.assert_called_with(
            "查找端口时出错，重试 (尝试 1/2): Socket error"
        )


class TestTestPortAvailability(unittest.TestCase):
    """测试_test_port_availability函数"""

    def setUp(self):
        """测试前准备"""
        # 清除日志处理器以避免测试间干扰
        logging.getLogger('backend.utils.network_utils').handlers.clear()

    @patch('backend.utils.network_utils.socket.socket')
    def test_port_available(self, mock_socket):
        """测试端口可用的情况"""
        # 模拟socket成功绑定
        mock_sock = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock
        
        result = _test_port_availability(8080)
        
        # 验证返回True
        self.assertTrue(result)
        
        # 验证socket操作
        mock_sock.setsockopt.assert_called_once_with(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        mock_sock.bind.assert_called_once_with(("", 8080))
        mock_sock.listen.assert_called_once_with(1)
        mock_sock.settimeout.assert_called_once_with(0.1)

    @patch('backend.utils.network_utils.socket.socket')
    def test_port_unavailable_address_in_use(self, mock_socket):
        """测试端口被占用的情况"""
        # 模拟地址已被使用错误
        mock_sock = MagicMock()
        error = socket.error()
        error.errno = 98  # Linux EADDRINUSE
        mock_sock.bind.side_effect = error
        mock_socket.return_value.__enter__.return_value = mock_sock
        
        result = _test_port_availability(8080)
        
        # 验证返回False
        self.assertFalse(result)

    @patch('backend.utils.network_utils.socket.socket')
    def test_port_unavailable_windows_address_in_use(self, mock_socket):
        """测试Windows下端口被占用的情况"""
        # 模拟Windows地址已被使用错误
        mock_sock = MagicMock()
        error = socket.error()
        error.errno = 10048  # Windows WSAEADDRINUSE
        mock_sock.bind.side_effect = error
        mock_socket.return_value.__enter__.return_value = mock_sock
        
        result = _test_port_availability(8080)
        
        # 验证返回False
        self.assertFalse(result)

    @patch('backend.utils.network_utils.socket.socket')
    def test_port_other_socket_error(self, mock_socket):
        """测试其他socket错误"""
        # 模拟其他socket错误
        mock_sock = MagicMock()
        error = socket.error("Other socket error")
        error.errno = 99  # 其他错误码
        mock_sock.bind.side_effect = error
        mock_socket.return_value.__enter__.return_value = mock_sock
        
        with patch('backend.utils.network_utils.logger') as mock_logger:
            result = _test_port_availability(8080)
        
        # 验证返回False
        self.assertFalse(result)
        
        # 验证记录了警告日志
        mock_logger.warning.assert_called_with(
            "测试端口 8080 可用性时发生意外的 socket 错误: Other socket error"
        )

    @patch('backend.utils.network_utils.socket.socket')
    def test_port_unexpected_exception(self, mock_socket):
        """测试未预期异常"""
        # 模拟未预期异常
        mock_sock = MagicMock()
        mock_sock.bind.side_effect = ValueError("Unexpected error")
        mock_socket.return_value.__enter__.return_value = mock_sock
        
        with patch('backend.utils.network_utils.logger') as mock_logger:
            result = _test_port_availability(8080)
        
        # 验证返回False
        self.assertFalse(result)
        
        # 验证记录了错误日志
        mock_logger.error.assert_called_with(
            "测试端口 8080 可用性时发生未预期错误: Unexpected error"
        )


if __name__ == '__main__':
    unittest.main()