"""
MCP反馈通道 v3.0 - Web版本
支持SSH环境的现代化反馈收集工具

主要功能：
- collect_feedback(): 收集用户反馈（Web界面）
- pick_image(): 快速图片选择（Web界面）  
- get_image_info_tool(): 获取图片信息
"""

import logging
import sys

# 从版本配置文件导入版本信息
from .version import __version__, __version_info__, get_version, get_version_info

__author__ = "MCP Feedback Collector Team"
__description__ = "现代化MCP反馈通道 - Web版本，完美支持SSH环境"

# 配置日志系统
def setup_logging(level=logging.INFO):
    """设置日志系统"""
    logger = logging.getLogger('mcp_feedback_pipe')
    
    if not logger.handlers:  # 避免重复添加处理器
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
    
    return logger

# 初始化日志
logger = setup_logging()

# 导入主要功能
from .server import mcp, collect_feedback, pick_image, get_image_info_tool

# 导出的公共API
__all__ = [
    "mcp", 
    "collect_feedback", 
    "pick_image", 
    "get_image_info_tool"
] 