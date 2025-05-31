"""
类型定义模块
为MCP反馈通道提供类型安全支持
"""

from typing import TypedDict, List, Optional, Union
from typing_extensions import NotRequired


class ImageData(TypedDict):
    """图片数据类型定义"""
    data: bytes
    source: str
    name: str


class FeedbackResult(TypedDict):
    """反馈结果类型定义"""
    success: bool
    text_feedback: Optional[str]
    images: List[ImageData]
    timestamp: Optional[str]
    has_text: bool
    has_images: bool
    image_count: int


class ServerInfo(TypedDict):
    """服务器信息类型定义"""
    port: Optional[int]
    url: Optional[str]
    is_running: bool


class VersionInfo(TypedDict):
    """版本信息类型定义"""
    current_version: str
    current_version_info: tuple[int, int, int]
    next_patch: str
    next_minor: str
    next_major: str


class RequestImageData(TypedDict):
    """前端请求图片数据类型定义"""
    data: str  # base64 data URL
    source: NotRequired[str]
    name: NotRequired[str]


class FeedbackRequest(TypedDict):
    """前端反馈请求类型定义"""
    textFeedback: NotRequired[str]
    images: NotRequired[List[RequestImageData]]
    timestamp: NotRequired[str]


# 常用类型别名
PortNumber = int
TimeoutSeconds = int
VersionString = str
Base64String = str 