"""
路由模块
包含所有路由相关的功能
"""

from .feedback_routes import feedback_bp, init_feedback_routes

__all__ = ["feedback_bp", "init_feedback_routes"]
