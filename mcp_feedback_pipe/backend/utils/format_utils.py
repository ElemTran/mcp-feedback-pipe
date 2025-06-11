"""
格式化工具模块
包含各种数据格式化功能
"""

from typing import Optional


def format_feedback_summary(
    text_feedback: Optional[str], image_count: int, timestamp: str
) -> str:
    """
    格式化反馈摘要

    Args:
        text_feedback: 文字反馈内容
        image_count: 图片数量
        timestamp: 时间戳

    Returns:
        格式化的反馈摘要
    """
    parts = []

    if text_feedback:
        parts.append(
            f"📝 文字反馈: {text_feedback[:100]}{'...' if len(text_feedback) > 100 else ''}"
        )

    if image_count > 0:
        parts.append(f"🖼️ 图片数量: {image_count}张")

    parts.append(f"⏰ 提交时间: {timestamp}")

    return "\n".join(parts)
