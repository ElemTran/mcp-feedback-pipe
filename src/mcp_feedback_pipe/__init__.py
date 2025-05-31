"""
MCP反馈通道 v3.0 - Web版本
支持SSH环境的现代化反馈收集工具

主要功能：
- collect_feedback(): 收集用户反馈（Web界面）
- pick_image(): 快速图片选择（Web界面）  
- get_image_info_tool(): 获取图片信息
"""

__version__ = "3.0.0"
__author__ = "MCP Feedback Collector Team"
__description__ = "现代化MCP反馈通道 - Web版本，完美支持SSH环境"

# 导入主要功能
from .server import mcp, collect_feedback, pick_image, get_image_info_tool

# 导出的公共API
__all__ = [
    "mcp", 
    "collect_feedback", 
    "pick_image", 
    "get_image_info_tool"
] 