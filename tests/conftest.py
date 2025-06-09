"""
MCP反馈通道测试配置
"""
import os
import sys
from pathlib import Path

import pytest

# 移除src目录路径添加
project_root = Path(__file__).parent.parent

@pytest.fixture
def project_root_path():
    """项目根目录路径"""
    return project_root

@pytest.fixture 
def src_path():
    """源代码目录路径"""
    return project_root / 'backend'

@pytest.fixture
def feedback_handler():
    """创建反馈处理器实例"""
    from backend.feedback_handler import FeedbackHandler
    return FeedbackHandler()

@pytest.fixture
def mock_flask_app():
    """创建模拟Flask应用"""
    from backend.app import FeedbackApp
    from backend.feedback_handler import FeedbackHandler
    
    handler = FeedbackHandler()
    app = FeedbackApp(handler)
    app.app.config['TESTING'] = True
    return app.app

@pytest.fixture
def test_image_data():
    """测试用的图片数据"""
    return {
        'data': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==',
        'source': 'test',
        'name': 'test.png'
    }
