"""
server_manager模块单元测试
测试Web服务器管理功能
"""

import pytest
import socket
from unittest.mock import MagicMock, patch, Mock

from mcp_feedback_pipe.server_manager import ServerManager


class TestServerManager:
    """测试ServerManager类"""
    
    def test_init(self):
        """测试初始化"""
        manager = ServerManager()
        assert hasattr(manager, 'feedback_handler')
        assert manager.app is None
        assert manager.server_thread is None
        assert manager.current_port is None
    
    @patch('socket.socket')
    def test_find_free_port(self, mock_socket):
        """测试查找空闲端口"""
        manager = ServerManager()
        
        # 模拟socket行为
        mock_sock = MagicMock()
        mock_sock.getsockname.return_value = ('127.0.0.1', 8080)
        mock_socket.return_value.__enter__.return_value = mock_sock
        
        port = manager.find_free_port()
        
        assert port == 8080
        mock_sock.bind.assert_called_once_with(('', 0))
        mock_sock.listen.assert_called_once_with(1)
    
    def test_get_server_info_not_running(self):
        """测试获取未运行服务器的信息"""
        manager = ServerManager()
        
        info = manager.get_server_info()
        
        assert info['port'] is None
        assert info['url'] is None
        assert info['is_running'] is False
    
    def test_get_server_info_running(self):
        """测试获取运行中服务器的信息"""
        manager = ServerManager()
        manager.current_port = 8080
        manager.server_thread = MagicMock()
        manager.server_thread.is_alive.return_value = True
        
        info = manager.get_server_info()
        
        assert info['port'] == 8080
        assert info['url'] == "http://127.0.0.1:8080"
        assert info['is_running'] is True
    
    @patch('mcp_feedback_pipe.server_manager.FeedbackApp')
    @patch('threading.Thread')
    @patch('time.sleep')
    def test_start_server(self, mock_sleep, mock_thread, mock_feedback_app):
        """测试启动服务器"""
        manager = ServerManager()
        
        # 模拟查找端口
        with patch.object(manager, 'find_free_port', return_value=8080):
            # 模拟浏览器打开
            with patch.object(manager, '_open_browser') as mock_open_browser:
                port = manager.start_server("测试工作汇报", 300)
        
        assert port == 8080
        assert manager.current_port == 8080
        mock_feedback_app.assert_called_once_with(manager.feedback_handler)
        mock_thread.assert_called_once()
        mock_open_browser.assert_called_once_with("测试工作汇报")
    
    @patch('mcp_feedback_pipe.server_manager.webbrowser.open')
    @patch('mcp_feedback_pipe.server_manager.quote')
    def test_open_browser_success(self, mock_quote, mock_webbrowser):
        """测试成功打开浏览器"""
        manager = ServerManager()
        manager.current_port = 8080
        mock_quote.return_value = "encoded_summary"
        
        manager._open_browser("测试汇报")
        
        mock_quote.assert_called_once_with("测试汇报")
        mock_webbrowser.assert_called_once_with(
            "http://127.0.0.1:8080/?work_summary=encoded_summary"
        )
    
    @patch('mcp_feedback_pipe.server_manager.webbrowser.open', side_effect=Exception("浏览器错误"))
    @patch('mcp_feedback_pipe.server_manager.quote')
    @patch('builtins.print')
    def test_open_browser_failure(self, mock_print, mock_quote, mock_webbrowser):
        """测试浏览器打开失败"""
        manager = ServerManager()
        manager.current_port = 8080
        mock_quote.return_value = "encoded_summary"
        
        manager._open_browser("测试汇报")
        
        # 验证错误处理
        assert mock_print.call_count >= 2  # 应该打印错误和备用地址
    
    def test_wait_for_feedback(self):
        """测试等待反馈"""
        manager = ServerManager()
        expected_result = {'test': 'feedback'}
        
        # 模拟feedback_handler返回结果
        manager.feedback_handler.get_result = MagicMock(return_value=expected_result)
        
        result = manager.wait_for_feedback(300)
        
        assert result == expected_result
        manager.feedback_handler.get_result.assert_called_once_with(300)
    
    def test_stop_server_with_thread(self):
        """测试停止运行中的服务器"""
        manager = ServerManager()
        manager.current_port = 8080
        manager.server_thread = MagicMock()
        manager.server_thread.is_alive.return_value = True
        manager.feedback_handler.clear_queue = MagicMock()
        
        manager.stop_server()
        
        manager.feedback_handler.clear_queue.assert_called_once()
        assert manager.current_port is None
    
    def test_stop_server_no_thread(self):
        """测试停止未运行的服务器"""
        manager = ServerManager()
        
        # 应该不会出错，但由于没有运行的线程，不会调用clear_queue
        manager.stop_server()
        
        # 验证没有异常抛出，这个测试主要检查不会崩溃


class TestServerManagerIntegration:
    """服务器管理器集成测试"""
    
    @patch('mcp_feedback_pipe.server_manager.FeedbackApp')
    @patch('threading.Thread')
    @patch('time.sleep')
    @patch('mcp_feedback_pipe.server_manager.webbrowser.open')
    def test_full_server_lifecycle(self, mock_webbrowser, mock_sleep, 
                                  mock_thread, mock_feedback_app):
        """测试完整的服务器生命周期"""
        manager = ServerManager()
        
        # 启动服务器
        with patch.object(manager, 'find_free_port', return_value=8080):
            port = manager.start_server("测试", 300)
        
        assert port == 8080
        assert manager.current_port == 8080
        
        # 停止服务器
        manager.stop_server()
        assert manager.current_port is None 