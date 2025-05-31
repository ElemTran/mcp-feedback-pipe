"""
Web界面集成测试
测试Flask应用和前端的集成功能
"""

import pytest
import json
import base64
from unittest.mock import patch, MagicMock

from mcp_feedback_pipe.app import FeedbackApp
from mcp_feedback_pipe.feedback_handler import FeedbackHandler


class TestWebInterfaceIntegration:
    """Web界面集成测试"""
    
    @pytest.fixture
    def app(self):
        """创建测试用的Flask应用"""
        handler = FeedbackHandler()
        feedback_app = FeedbackApp(handler)
        app = feedback_app.app
        app.config['TESTING'] = True
        return app.test_client(), handler
    
    def test_index_route(self, app):
        """测试主页路由"""
        client, handler = app
        
        response = client.get('/')
        assert response.status_code == 200
        assert '反馈通道' in response.data.decode('utf-8')
    
    def test_index_with_work_summary(self, app):
        """测试带工作汇报的主页"""
        client, handler = app
        
        work_summary = "测试工作汇报内容"
        response = client.get(f'/?work_summary={work_summary}')
        
        assert response.status_code == 200
        html_content = response.data.decode('utf-8')
        assert work_summary in html_content
    
    def test_ping_route(self, app):
        """测试ping路由"""
        client, handler = app
        
        response = client.get('/ping')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'ok'
    
    def test_submit_feedback_text_only(self, app):
        """测试提交仅文字反馈"""
        client, handler = app
        
        feedback_data = {
            'textFeedback': '这是测试反馈',
            'images': [],
            'timestamp': '2024-01-01T12:00:00Z'
        }
        
        response = client.post('/submit_feedback',
                             data=json.dumps(feedback_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        
        # 验证数据被正确处理
        result = handler.get_result(timeout=1)
        assert result is not None
        assert result['text_feedback'] == '这是测试反馈'
        assert result['has_text'] is True
        assert result['has_images'] is False
    
    def test_submit_feedback_with_images(self, app):
        """测试提交带图片的反馈"""
        client, handler = app
        
        # 创建测试图片数据（base64编码）
        test_image_data = base64.b64encode(b'fake_image_data').decode('utf-8')
        
        feedback_data = {
            'textFeedback': '带图片的反馈',
            'images': [{
                'data': f'data:image/png;base64,{test_image_data}',
                'source': '测试',
                'name': 'test.png'
            }],
            'timestamp': '2024-01-01T12:00:00Z'
        }
        
        response = client.post('/submit_feedback',
                             data=json.dumps(feedback_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        
        # 验证数据被正确处理
        result = handler.get_result(timeout=1)
        assert result is not None
        assert result['has_images'] is True
        assert result['image_count'] == 1
        assert len(result['images']) == 1
        assert result['images'][0]['data'] == b'fake_image_data'
    
    def test_submit_feedback_invalid_json(self, app):
        """测试提交无效JSON"""
        client, handler = app
        
        response = client.post('/submit_feedback',
                             data='invalid json',
                             content_type='application/json')
        
        assert response.status_code == 400
    
    def test_submit_feedback_empty_data(self, app):
        """测试提交空数据"""
        client, handler = app
        
        feedback_data = {
            'textFeedback': '',
            'images': [],
            'timestamp': '2024-01-01T12:00:00Z'
        }
        
        response = client.post('/submit_feedback',
                             data=json.dumps(feedback_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        
        # 验证空数据被正确处理
        result = handler.get_result(timeout=1)
        assert result is not None
        assert result['has_text'] is False
        assert result['has_images'] is False
    
    @patch('threading.Timer')
    def test_close_route(self, mock_timer, app):
        """测试关闭路由"""
        client, handler = app
        
        response = client.get('/close')
        assert response.status_code == 200
        
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        
        # 验证定时器被正确设置
        mock_timer.assert_called_once()
    
    def test_static_files_accessible(self, app):
        """测试静态文件可访问性"""
        client, handler = app
        
        # 测试CSS文件
        response = client.get('/static/css/styles.css')
        assert response.status_code == 200
        assert 'text/css' in response.content_type
        
        # 测试JS文件
        response = client.get('/static/js/feedback.js')
        assert response.status_code == 200
        assert 'javascript' in response.content_type or 'text/plain' in response.content_type


class TestDataProcessing:
    """数据处理集成测试"""
    
    def test_image_data_processing(self):
        """测试图片数据处理"""
        handler = FeedbackHandler()
        app = FeedbackApp(handler)
        
        # 测试base64图片数据处理
        test_data = base64.b64encode(b'test_image_bytes').decode('utf-8')
        data_url = f'data:image/png;base64,{test_data}'
        
        image_data = {
            'data': data_url,
            'source': '测试',
            'name': 'test.png'
        }
        
        request_data = {
            'textFeedback': '测试',
            'images': [image_data],
            'timestamp': '2024-01-01T12:00:00Z'
        }
        
        result = app._process_feedback_data(request_data)
        
        assert result['success'] is True
        assert result['has_images'] is True
        assert result['image_count'] == 1
        assert result['images'][0]['data'] == b'test_image_bytes'
        assert result['images'][0]['name'] == 'test.png'
    
    def test_multiple_images_processing(self):
        """测试多图片处理"""
        handler = FeedbackHandler()
        app = FeedbackApp(handler)
        
        # 创建多个测试图片
        images = []
        for i in range(3):
            test_data = base64.b64encode(f'image_{i}_data'.encode()).decode('utf-8')
            images.append({
                'data': f'data:image/png;base64,{test_data}',
                'source': '测试',
                'name': f'test_{i}.png'
            })
        
        request_data = {
            'textFeedback': '多图片测试',
            'images': images,
            'timestamp': '2024-01-01T12:00:00Z'
        }
        
        result = app._process_feedback_data(request_data)
        
        assert result['success'] is True
        assert result['image_count'] == 3
        assert len(result['images']) == 3
        
        # 验证每个图片都被正确处理
        for i, img in enumerate(result['images']):
            assert img['data'] == f'image_{i}_data'.encode()
            assert img['name'] == f'test_{i}.png' 