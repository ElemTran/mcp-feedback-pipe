"""
自定义异常类
定义项目特定的异常类型，提供更精确的错误处理
"""


class FeedbackTimeoutError(Exception):
    """
    反馈超时异常
    
    当用户在指定时间内未提供反馈时抛出此异常
    """
    
    def __init__(self, timeout_seconds: int, message: str = None):
        if message is None:
            message = f"操作超时（{timeout_seconds}秒），请重试"
        super().__init__(message)
        self.timeout_seconds = timeout_seconds


class ImageSelectionError(Exception):
    """
    图片选择异常
    
    当图片选择过程中出现错误或用户取消操作时抛出此异常
    """
    
    def __init__(self, message: str = "未选择图片或操作被取消"):
        super().__init__(message)