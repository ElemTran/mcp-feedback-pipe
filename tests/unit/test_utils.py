"""
utils模块单元测试
测试图片处理和工具函数
"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from mcp_feedback_pipe.utils import (
    get_image_info,
    validate_image_data,
    format_feedback_summary
)


class TestGetImageInfo:
    """测试get_image_info函数"""
    
    def test_get_image_info_file_not_exists(self):
        """测试文件不存在的情况"""
        result = get_image_info("/nonexistent/path.jpg")
        assert "文件不存在" in result
    
    @patch('mcp_feedback_pipe.utils.PIL_AVAILABLE', False)
    def test_get_image_info_no_pil(self):
        """测试PIL不可用的情况"""
        result = get_image_info("test.jpg")
        assert "Pillow库未安装" in result
    
    @patch('mcp_feedback_pipe.utils.PIL_AVAILABLE', True)
    @patch('mcp_feedback_pipe.utils.Image.open')
    @patch('mcp_feedback_pipe.utils.Path.exists', return_value=True)
    @patch('mcp_feedback_pipe.utils.Path.stat')
    def test_get_image_info_success(self, mock_stat, mock_exists, mock_open):
        """测试成功获取图片信息"""
        # 设置模拟数据
        mock_img = MagicMock()
        mock_img.format = 'PNG'
        mock_img.width = 100
        mock_img.height = 200
        mock_img.mode = 'RGB'
        mock_open.return_value.__enter__.return_value = mock_img
        
        mock_stat_result = MagicMock()
        mock_stat_result.st_size = 2048
        mock_stat.return_value = mock_stat_result
        
        result = get_image_info("test.png")
        
        assert "格式: PNG" in result
        assert "尺寸: 100 x 200" in result
        assert "模式: RGB" in result
        assert "2.0 KB" in result


class TestValidateImageData:
    """测试validate_image_data函数"""
    
    @patch('mcp_feedback_pipe.utils.PIL_AVAILABLE', False)
    def test_validate_image_data_no_pil(self):
        """测试PIL不可用的情况"""
        result = validate_image_data(b"fake_data")
        assert result is False
    
    @patch('mcp_feedback_pipe.utils.PIL_AVAILABLE', True)
    @patch('mcp_feedback_pipe.utils.Image.open')
    def test_validate_image_data_valid(self, mock_open):
        """测试有效图片数据"""
        mock_img = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_img
        
        result = validate_image_data(b"valid_image_data")
        assert result is True
    
    @patch('mcp_feedback_pipe.utils.PIL_AVAILABLE', True)
    @patch('mcp_feedback_pipe.utils.Image.open', side_effect=Exception("Invalid"))
    def test_validate_image_data_invalid(self, mock_open):
        """测试无效图片数据"""
        result = validate_image_data(b"invalid_data")
        assert result is False


class TestFormatFeedbackSummary:
    """测试format_feedback_summary函数"""
    
    def test_format_feedback_summary_text_only(self):
        """测试仅有文字反馈的情况"""
        result = format_feedback_summary("这是测试反馈", 0, "2024-01-01T12:00:00Z")
        assert "📝 文字反馈: 这是测试反馈" in result
        assert "🖼️ 图片数量" not in result
        assert "⏰ 提交时间: 2024-01-01T12:00:00Z" in result
    
    def test_format_feedback_summary_images_only(self):
        """测试仅有图片反馈的情况"""
        result = format_feedback_summary(None, 3, "2024-01-01T12:00:00Z")
        assert "📝 文字反馈" not in result
        assert "🖼️ 图片数量: 3张" in result
        assert "⏰ 提交时间: 2024-01-01T12:00:00Z" in result
    
    def test_format_feedback_summary_long_text(self):
        """测试长文本截断"""
        long_text = "这是一个非常长的反馈" * 15  # 确保超过100字符
        result = format_feedback_summary(long_text, 0, "2024-01-01T12:00:00Z")
        assert "..." in result
        # 检查文本被正确截断
        lines = result.split('\n')
        feedback_line = [line for line in lines if line.startswith('📝 文字反馈:')][0]
        assert len(feedback_line) <= 120  # 100字符+前缀+省略号
    
    def test_format_feedback_summary_complete(self):
        """测试完整反馈的情况"""
        result = format_feedback_summary("测试反馈", 2, "2024-01-01T12:00:00Z")
        assert "📝 文字反馈: 测试反馈" in result
        assert "🖼️ 图片数量: 2张" in result
        assert "⏰ 提交时间: 2024-01-01T12:00:00Z" in result 