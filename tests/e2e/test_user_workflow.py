"""
端到端用户工作流程测试
模拟完整的用户交互流程
"""

import pytest
import time
import threading
from unittest.mock import patch, MagicMock

from mcp_feedback_pipe.server_manager import ServerManager
from mcp_feedback_pipe import collect_feedback, pick_image, server_manager


class TestCompleteUserWorkflow:
    """完整用户工作流程测试"""
    
    @patch('mcp_feedback_pipe.server_manager.webbrowser.open')
    @patch('mcp_feedback_pipe.server_manager.threading.Thread')
    def test_collect_feedback_full_workflow(self, mock_thread, mock_webbrowser):
        """测试完整的反馈收集工作流程"""
        
        # 模拟用户提交反馈的函数
        def simulate_user_feedback():
            time.sleep(0.5)  # 模拟用户思考时间
            
            # 模拟用户提交的反馈数据
            feedback_data = {
                'success': True,
                'text_feedback': '这是端到端测试的反馈',
                'images': [],
                'timestamp': '2024-01-01T12:00:00Z',
                'has_text': True,
                'has_images': False,
                'image_count': 0
            }
            
            # 将反馈放入全局server_manager的队列
            server_manager.feedback_handler.put_result(feedback_data)
        
        # 设置模拟
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance
        
        with patch('mcp_feedback_pipe.server_manager.ServerManager.find_free_port', return_value=8080):
            with patch('mcp_feedback_pipe.server_manager.time.sleep'):
                # 启动模拟用户反馈的线程
                user_thread = threading.Thread(target=simulate_user_feedback)
                user_thread.start()
                
                # 调用collect_feedback
                try:
                    result = collect_feedback(
                        work_summary="测试工作汇报",
                        timeout_seconds=5
                    )
                    
                    # 验证结果
                    assert len(result) == 1  # 应该有一个文本反馈
                    
                finally:
                    user_thread.join()
                    # 清理server_manager状态
                    server_manager.stop_server()
    
    @patch('mcp_feedback_pipe.server_manager.webbrowser.open')
    @patch('mcp_feedback_pipe.server_manager.threading.Thread')
    def test_pick_image_workflow(self, mock_thread, mock_webbrowser):
        """测试图片选择工作流程"""
        
        def simulate_image_selection():
            time.sleep(0.5)
            
            # 模拟用户选择图片
            feedback_data = {
                'success': True,
                'has_images': True,
                'images': [{
                    'data': b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde',
                    'source': '测试',
                    'name': 'test.png'
                }]
            }
            
            server_manager.feedback_handler.put_result(feedback_data)
        
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance
        
        with patch('mcp_feedback_pipe.server_manager.ServerManager.find_free_port', return_value=8080):
            with patch('mcp_feedback_pipe.server_manager.time.sleep'):
                user_thread = threading.Thread(target=simulate_image_selection)
                user_thread.start()
                
                try:
                    result = pick_image()
                    
                    # 验证返回了图片数据
                    assert hasattr(result, 'data')
                    assert hasattr(result, 'format')
                    
                finally:
                    user_thread.join()
                    server_manager.stop_server()
    
    def test_timeout_scenario(self):
        """测试超时场景"""
        with patch('mcp_feedback_pipe.server_manager.webbrowser.open'):
            with patch('mcp_feedback_pipe.server_manager.threading.Thread'):
                with patch('mcp_feedback_pipe.server_manager.ServerManager.find_free_port', return_value=8080):
                    with patch('mcp_feedback_pipe.server_manager.time.sleep'):
                        
                        # 不提供任何用户反馈，应该超时
                        with pytest.raises(Exception, match="操作超时"):
                            collect_feedback(
                                work_summary="超时测试",
                                timeout_seconds=1
                            )
    
    @patch('mcp_feedback_pipe.server_manager.webbrowser.open')
    @patch('mcp_feedback_pipe.server_manager.threading.Thread')
    def test_user_cancellation(self, mock_thread, mock_webbrowser):
        """测试用户取消操作"""
        
        def simulate_user_cancellation():
            time.sleep(0.5)
            
            # 模拟用户取消
            feedback_data = {
                'success': False,
                'message': '用户取消了操作'
            }
            
            server_manager.feedback_handler.put_result(feedback_data)
        
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance
        
        with patch('mcp_feedback_pipe.server_manager.ServerManager.find_free_port', return_value=8080):
            with patch('mcp_feedback_pipe.server_manager.time.sleep'):
                user_thread = threading.Thread(target=simulate_user_cancellation)
                user_thread.start()
                
                try:
                    with pytest.raises(Exception, match="用户取消了操作"):
                        collect_feedback(
                            work_summary="取消测试",
                            timeout_seconds=5
                        )
                        
                finally:
                    user_thread.join()
                    server_manager.stop_server()


class TestErrorHandling:
    """错误处理测试"""
    
    def test_missing_flask_dependency(self):
        """测试Flask依赖缺失的情况"""
        # 这个测试需要特殊处理，因为Flask已经导入了
        with patch('mcp_feedback_pipe.app.Flask', side_effect=ImportError("Flask not found")):
            with pytest.raises(Exception, match="依赖缺失"):
                collect_feedback("测试", 5)
    
    @patch('mcp_feedback_pipe.server_manager.ServerManager.start_server', 
           side_effect=Exception("服务器启动失败"))
    def test_server_startup_failure(self, mock_start):
        """测试服务器启动失败"""
        with pytest.raises(Exception, match="启动反馈通道失败"):
            collect_feedback("测试", 5)
    
    def test_invalid_timeout(self):
        """测试无效的超时参数"""
        with patch('mcp_feedback_pipe.server_manager.webbrowser.open'):
            with patch('mcp_feedback_pipe.server_manager.threading.Thread'):
                with patch('mcp_feedback_pipe.server_manager.ServerManager.find_free_port', return_value=8080):
                    with patch('mcp_feedback_pipe.server_manager.time.sleep'):
                        
                        # 超时时间为0应该立即超时
                        with pytest.raises(Exception, match="操作超时"):
                            collect_feedback("测试", 0)


class TestResourceManagement:
    """资源管理测试"""
    
    @patch('mcp_feedback_pipe.server_manager.webbrowser.open')
    @patch('mcp_feedback_pipe.server_manager.threading.Thread')
    def test_proper_cleanup_after_success(self, mock_thread, mock_webbrowser):
        """测试成功完成后的资源清理"""
        
        def simulate_successful_feedback():
            time.sleep(0.5)
            feedback_data = {
                'success': True,
                'text_feedback': '测试反馈',
                'has_text': True,
                'has_images': False,
                'timestamp': '2024-01-01T12:00:00Z'
            }
            server_manager.feedback_handler.put_result(feedback_data)
        
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance
        
        with patch('mcp_feedback_pipe.server_manager.ServerManager.find_free_port', return_value=8080):
            with patch('mcp_feedback_pipe.server_manager.time.sleep'):
                
                user_thread = threading.Thread(target=simulate_successful_feedback)
                user_thread.start()
                
                # 监控stop_server方法的调用
                with patch.object(server_manager, 'stop_server') as mock_stop:
                    try:
                        result = collect_feedback("测试", 5)
                        
                        # 验证资源被正确清理
                        mock_stop.assert_called_once()
                        
                    finally:
                        user_thread.join()
    
    @patch('mcp_feedback_pipe.server_manager.webbrowser.open')
    @patch('mcp_feedback_pipe.server_manager.threading.Thread')
    def test_cleanup_after_exception(self, mock_thread, mock_webbrowser):
        """测试异常情况下的资源清理"""
        
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance
        
        with patch('mcp_feedback_pipe.server_manager.ServerManager.find_free_port', return_value=8080):
            with patch('mcp_feedback_pipe.server_manager.time.sleep'):
                
                # 模拟异常情况
                with patch.object(server_manager, 'wait_for_feedback', 
                                side_effect=Exception("测试异常")):
                    with patch.object(server_manager, 'stop_server') as mock_stop:
                        
                        with pytest.raises(Exception):
                            collect_feedback("测试", 5)
                        
                        # 即使发生异常，也应该调用清理方法
                        mock_stop.assert_called_once() 