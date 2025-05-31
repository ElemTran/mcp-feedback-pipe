"""
版本配置文件
统一管理mcp-feedback-pipe的版本信息
"""

__version__ = "3.0.5"
__version_info__ = (3, 0, 5)

# 版本历史（按时间倒序）
VERSION_HISTORY = {
    "3.0.5": "版本更新 - 2025-05-31",
    "3.0.6": "版本更新 - 2025-05-31",
    "3.0.5": "版本更新 - 2025-05-31",
    "3.0.4": "版本同步更新 - 2025-05-31",
    "3.0.3": "安全性增强和架构优化 - 2025-05-31",
    "3.0.2": "修复复制按钮功能，添加命令行支持，版本号配置化",
    "3.0.1": "修复版本显示问题",
    "3.0.0": "Web版本正式发布，支持SSH环境",
    "2.x.x": "GUI版本（已废弃）"
}

def get_version():
    """获取当前版本号"""
    return __version__

def get_version_info():
    """获取版本信息元组"""
    return __version_info__

def get_version_history():
    """获取版本历史"""
    return VERSION_HISTORY 