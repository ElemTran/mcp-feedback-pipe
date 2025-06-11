"""
浏览器工具模块
处理浏览器操作相关功能
"""

import logging
import webbrowser
from urllib.parse import quote

# 配置模块级别的logger
logger = logging.getLogger(__name__)


def open_feedback_browser(port: int, work_summary: str, suggest: str = "") -> None:
    """
    在浏览器中打开反馈页面

    Args:
        port: 服务器端口号
        work_summary: 工作摘要
        suggest: 建议内容，默认为空字符串
    """
    try:
        encoded_summary = quote(work_summary)
        encoded_suggest = quote(suggest) if suggest else ""
        url = f"http://127.0.0.1:{port}/?work_summary={encoded_summary}"
        if encoded_suggest:
            url += f"&suggest={encoded_suggest}"
        webbrowser.open(url)
    except (OSError, webbrowser.Error) as e:
        logger.warning(f"无法自动打开浏览器 - 系统或浏览器错误: {e}")
        logger.info(f"请手动访问: http://127.0.0.1:{port}")
    except Exception as e:
        logger.error(f"无法自动打开浏览器 - 未知错误: {e}")
        logger.info(f"请手动访问: http://127.0.0.1:{port}")
