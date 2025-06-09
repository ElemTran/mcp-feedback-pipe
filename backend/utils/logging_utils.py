"""
日志工具模块
提供统一的日志记录功能
"""

import datetime

# 日志配置
LOG_FILE = "debug_mcp_feedback.log"


def log_message(message: str):
    """将日志消息打印到控制台并写入日志文件"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    full_message = f"[{timestamp}] {message}"
    print(full_message)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(full_message + "\n")
    except Exception as e:
        print(
            f"[{timestamp}] [LOGGING_ERROR] Failed to write to log file {LOG_FILE}: {e}"
        )
