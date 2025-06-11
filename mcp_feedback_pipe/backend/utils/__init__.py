"""
工具模块
包含网络、浏览器、图片处理和日志记录等工具功能
"""

from pathlib import Path

from .network_utils import find_free_port
from .browser_utils import open_feedback_browser
from .image_utils import (
    get_image_info,
    validate_image_data,
    is_allowed_file,
    get_image_format_info,
    get_allowed_extensions,
    PIL_AVAILABLE,
)
from .logging_utils import log_message
from .format_utils import format_feedback_summary

# 导入PIL的Image用于测试兼容性
try:
    from PIL import Image
except ImportError:
    Image = None

__all__ = [
    "find_free_port",
    "open_feedback_browser",
    "get_image_info",
    "validate_image_data",
    "is_allowed_file",
    "get_image_format_info",
    "get_allowed_extensions",
    "log_message",
    "format_feedback_summary",
    "PIL_AVAILABLE",
    "Image",
    "Path",
]
