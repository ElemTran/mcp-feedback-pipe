"""
MCP Feedback Pipe - 现代化Web反馈收集工具

这是一个基于Model Context Protocol (MCP) 的反馈收集系统，
专为SSH远程环境设计，提供直观的Web界面进行用户反馈收集。
"""

__version__ = "3.0.15"
__author__ = "ElemTran"
__email__ = "your.email@example.com"

from .server import main

__all__ = ["main", "__version__"] 