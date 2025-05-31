"""
统一配置管理系统
集中管理所有配置项，避免硬编码分散
"""

import os
from typing import Set, Dict, Any
from dataclasses import dataclass


@dataclass
class SecurityConfig:
    """安全相关配置"""
    # CSRF保护
    csrf_token_bytes: int = 32
    csrf_token_lifetime: int = 3600  # 1小时
    
    # 文件上传限制
    max_content_length: int = 16 * 1024 * 1024  # 16MB
    allowed_extensions: Set[str] = None
    
    # 内存限制
    max_memory_per_request: int = 50 * 1024 * 1024  # 50MB
    max_queue_size: int = 100
    
    def __post_init__(self):
        if self.allowed_extensions is None:
            self.allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}


@dataclass
class ServerConfig:
    """服务器相关配置"""
    # 端口配置
    port_range_start: int = 8000
    port_range_end: int = 65535
    max_port_attempts: int = 100
    
    # 超时配置
    default_timeout: int = 300  # 5分钟
    server_startup_timeout: int = 10
    shutdown_timeout: int = 5
    
    # 线程配置
    daemon_threads: bool = True
    
    # 清理配置
    cleanup_interval: int = 5  # 秒
    idle_timeout: int = 30  # 30秒无活动后清理


@dataclass
class WebConfig:
    """Web界面相关配置"""
    # 模板配置
    template_folder: str = "templates"
    static_folder: str = "static"
    
    # 调试配置
    debug_mode: bool = False
    use_reloader: bool = False
    threaded: bool = True
    
    # 主机配置
    default_host: str = "127.0.0.1"
    allowed_hosts: Set[str] = None
    
    def __post_init__(self):
        if self.allowed_hosts is None:
            self.allowed_hosts = {'127.0.0.1', '::1', 'localhost'}


@dataclass
class FeedbackConfig:
    """反馈处理相关配置"""
    # 文本限制
    max_text_length: int = 50000  # 50KB
    
    # 图片限制
    max_images_count: int = 10
    max_image_size: int = 5 * 1024 * 1024  # 5MB
    
    # 处理配置
    include_metadata: bool = True
    include_timestamp: bool = True


class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self.security = SecurityConfig()
        self.server = ServerConfig()
        self.web = WebConfig()
        self.feedback = FeedbackConfig()
        
        # 从环境变量加载配置
        self._load_from_env()
    
    def _load_from_env(self):
        """从环境变量加载配置"""
        # 安全配置
        if os.getenv('MCP_MAX_CONTENT_LENGTH'):
            self.security.max_content_length = int(os.getenv('MCP_MAX_CONTENT_LENGTH'))
        
        if os.getenv('MCP_MAX_MEMORY'):
            self.security.max_memory_per_request = int(os.getenv('MCP_MAX_MEMORY'))
        
        # 服务器配置
        if os.getenv('MCP_PORT_START'):
            self.server.port_range_start = int(os.getenv('MCP_PORT_START'))
        
        if os.getenv('MCP_PORT_END'):
            self.server.port_range_end = int(os.getenv('MCP_PORT_END'))
        
        if os.getenv('MCP_DEFAULT_TIMEOUT'):
            self.server.default_timeout = int(os.getenv('MCP_DEFAULT_TIMEOUT'))
        
        # Web配置
        if os.getenv('MCP_DEBUG'):
            self.web.debug_mode = os.getenv('MCP_DEBUG').lower() in ('true', '1', 'yes')
        
        # 反馈配置
        if os.getenv('MCP_MAX_TEXT_LENGTH'):
            self.feedback.max_text_length = int(os.getenv('MCP_MAX_TEXT_LENGTH'))
        
        if os.getenv('MCP_MAX_IMAGES'):
            self.feedback.max_images_count = int(os.getenv('MCP_MAX_IMAGES'))
    
    def get_flask_config(self) -> Dict[str, Any]:
        """获取Flask应用配置"""
        return {
            'SECRET_KEY': os.urandom(32),
            'MAX_CONTENT_LENGTH': self.security.max_content_length,
            'DEBUG': self.web.debug_mode,
            'TESTING': False,
            'PROPAGATE_EXCEPTIONS': None,
            'PRESERVE_CONTEXT_ON_EXCEPTION': None,
            'TRAP_HTTP_EXCEPTIONS': False,
            'TRAP_BAD_REQUEST_ERRORS': None,
        }
    
    def validate_config(self) -> bool:
        """验证配置的有效性"""
        try:
            # 验证端口范围
            if self.server.port_range_start >= self.server.port_range_end:
                raise ValueError("端口范围配置无效")
            
            # 验证内存限制
            if self.security.max_memory_per_request <= 0:
                raise ValueError("内存限制必须大于0")
            
            # 验证超时配置
            if self.server.default_timeout <= 0:
                raise ValueError("超时时间必须大于0")
            
            return True
            
        except Exception as e:
            print(f"配置验证失败: {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """将配置转换为字典"""
        return {
            'security': {
                'csrf_token_bytes': self.security.csrf_token_bytes,
                'csrf_token_lifetime': self.security.csrf_token_lifetime,
                'max_content_length': self.security.max_content_length,
                'allowed_extensions': list(self.security.allowed_extensions),
                'max_memory_per_request': self.security.max_memory_per_request,
                'max_queue_size': self.security.max_queue_size,
            },
            'server': {
                'port_range_start': self.server.port_range_start,
                'port_range_end': self.server.port_range_end,
                'max_port_attempts': self.server.max_port_attempts,
                'default_timeout': self.server.default_timeout,
                'server_startup_timeout': self.server.server_startup_timeout,
                'shutdown_timeout': self.server.shutdown_timeout,
                'daemon_threads': self.server.daemon_threads,
                'cleanup_interval': self.server.cleanup_interval,
                'idle_timeout': self.server.idle_timeout,
            },
            'web': {
                'template_folder': self.web.template_folder,
                'static_folder': self.web.static_folder,
                'debug_mode': self.web.debug_mode,
                'use_reloader': self.web.use_reloader,
                'threaded': self.web.threaded,
                'default_host': self.web.default_host,
                'allowed_hosts': list(self.web.allowed_hosts),
            },
            'feedback': {
                'max_text_length': self.feedback.max_text_length,
                'max_images_count': self.feedback.max_images_count,
                'max_image_size': self.feedback.max_image_size,
                'include_metadata': self.feedback.include_metadata,
                'include_timestamp': self.feedback.include_timestamp,
            }
        }


# 全局配置实例
_config_manager = None


def get_config() -> ConfigManager:
    """获取全局配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
        if not _config_manager.validate_config():
            raise RuntimeError("配置验证失败，请检查配置项")
    return _config_manager


# 便捷访问函数
def get_security_config() -> SecurityConfig:
    """获取安全配置"""
    return get_config().security


def get_server_config() -> ServerConfig:
    """获取服务器配置"""
    return get_config().server


def get_web_config() -> WebConfig:
    """获取Web配置"""
    return get_config().web


def get_feedback_config() -> FeedbackConfig:
    """获取反馈配置"""
    return get_config().feedback 