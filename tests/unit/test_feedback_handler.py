"""
feedback_handler模块单元测试
测试反馈数据处理和队列管理
"""

import pytest
import queue
import threading
import time
from unittest.mock import MagicMock, patch

from mcp_feedback_pipe.feedback_handler import FeedbackHandler


class TestFeedbackHandler:
    """测试FeedbackHandler类"""
    
    def test_init(self):
        """测试初始化"""
        handler = FeedbackHandler()
        assert hasattr(handler, 'result_queue')
        assert hasattr(handler, '_lock')
        assert isinstance(handler.result_queue, queue.Queue)
        assert isinstance(handler._lock, type(threading.Lock()))
    
    def test_put_result(self):
        """测试放入结果"""
        handler = FeedbackHandler()
        test_data = {'test': 'data'}
        
        handler.put_result(test_data)
        
        # 验证数据已放入队列
        result = handler.result_queue.get_nowait()
        assert result == test_data
    
    def test_get_result_success(self):
        """测试成功获取结果"""
        handler = FeedbackHandler()
        test_data = {'success': True, 'message': 'test'}
        
        # 放入数据
        handler.put_result(test_data)
        
        # 获取数据
        result = handler.get_result(timeout=1)
        assert result == test_data
    
    def test_get_result_timeout(self):
        """测试获取结果超时"""
        handler = FeedbackHandler()
        
        # 不放入任何数据，应该超时
        result = handler.get_result(timeout=1)
        assert result is None
    
    def test_get_result_concurrent(self):
        """测试并发访问"""
        handler = FeedbackHandler()
        
        def put_data():
            time.sleep(0.5)  # 延迟放入数据
            handler.put_result({'delayed': 'data'})
        
        # 启动线程放入数据
        thread = threading.Thread(target=put_data)
        thread.start()
        
        # 等待数据
        result = handler.get_result(timeout=2)
        thread.join()
        
        assert result == {'delayed': 'data'}
    
    def test_clear_queue(self):
        """测试清空队列"""
        handler = FeedbackHandler()
        
        # 放入多个数据
        handler.put_result({'data1': 'test'})
        handler.put_result({'data2': 'test'})
        handler.put_result({'data3': 'test'})
        
        # 清空队列
        handler.clear_queue()
        
        # 验证队列为空
        assert handler.result_queue.empty()


class TestProcessFeedbackToMcp:
    """测试process_feedback_to_mcp方法"""
    
    def test_process_feedback_empty_result(self):
        """测试空结果"""
        handler = FeedbackHandler()
        
        with pytest.raises(Exception, match="获取反馈失败"):
            handler.process_feedback_to_mcp(None)
    
    def test_process_feedback_failed_result(self):
        """测试失败结果"""
        handler = FeedbackHandler()
        failed_result = {'success': False, 'message': '用户取消'}
        
        with pytest.raises(Exception, match="用户取消"):
            handler.process_feedback_to_mcp(failed_result)
    
    @patch('mcp_feedback_pipe.feedback_handler.TextContent')
    def test_process_feedback_text_only(self, mock_text_content):
        """测试仅文字反馈"""
        handler = FeedbackHandler()
        result = {
            'success': True,
            'has_text': True,
            'text_feedback': '测试反馈',
            'timestamp': '2024-01-01T12:00:00Z',
            'has_images': False
        }
        
        mock_text_instance = MagicMock()
        mock_text_content.return_value = mock_text_instance
        
        feedback_items = handler.process_feedback_to_mcp(result)
        
        assert len(feedback_items) == 1
        assert feedback_items[0] == mock_text_instance
        mock_text_content.assert_called_once()
    
    @patch('mcp_feedback_pipe.feedback_handler.MCPImage')
    def test_process_feedback_images_only(self, mock_mcp_image):
        """测试仅图片反馈"""
        handler = FeedbackHandler()
        result = {
            'success': True,
            'has_text': False,
            'has_images': True,
            'images': [
                {'data': b'image1_data'},
                {'data': b'image2_data'}
            ]
        }
        
        mock_image_instance = MagicMock()
        mock_mcp_image.return_value = mock_image_instance
        
        feedback_items = handler.process_feedback_to_mcp(result)
        
        assert len(feedback_items) == 2
        assert mock_mcp_image.call_count == 2
        mock_mcp_image.assert_any_call(data=b'image1_data', format='png')
        mock_mcp_image.assert_any_call(data=b'image2_data', format='png')
    
    @patch('mcp_feedback_pipe.feedback_handler.TextContent')
    @patch('mcp_feedback_pipe.feedback_handler.MCPImage')
    def test_process_feedback_complete(self, mock_mcp_image, mock_text_content):
        """测试完整反馈（文字+图片）"""
        handler = FeedbackHandler()
        result = {
            'success': True,
            'has_text': True,
            'text_feedback': '测试反馈',
            'timestamp': '2024-01-01T12:00:00Z',
            'has_images': True,
            'images': [{'data': b'image_data'}]
        }
        
        mock_text_instance = MagicMock()
        mock_image_instance = MagicMock()
        mock_text_content.return_value = mock_text_instance
        mock_mcp_image.return_value = mock_image_instance
        
        feedback_items = handler.process_feedback_to_mcp(result)
        
        assert len(feedback_items) == 2
        assert feedback_items[0] == mock_text_instance
        assert feedback_items[1] == mock_image_instance 