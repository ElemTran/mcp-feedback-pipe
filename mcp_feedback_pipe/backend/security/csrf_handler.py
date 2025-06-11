"""
CSRF保护模块
提供线程安全的CSRF令牌生成和验证功能
"""

import secrets
import time
import threading
from typing import Dict, List


class SecurityConfig:
    """安全配置管理"""

    # CSRF保护
    CSRF_TOKEN_BYTES = 32
    CSRF_TOKEN_LIFETIME = 3600  # 1小时

    # 文件上传限制
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp", "webp"}

    # 内存限制
    MAX_MEMORY_PER_REQUEST = 50 * 1024 * 1024  # 50MB


class CSRFProtection:
    """线程安全的CSRF保护实现"""

    def __init__(self) -> None:
        self._tokens: Dict[str, float] = {}
        self._lock = threading.Lock()

    def generate_token(self) -> str:
        """
        生成CSRF令牌并清理过期令牌

        Returns:
            str: 新生成的CSRF令牌
        """
        token = secrets.token_urlsafe(SecurityConfig.CSRF_TOKEN_BYTES)
        current_time = time.time()

        with self._lock:
            # 添加新令牌
            self._tokens[token] = current_time

            # 线程安全的过期令牌清理
            # 使用list()创建副本避免在迭代时修改字典
            expired_tokens: List[str] = []
            for token_key, timestamp in list(self._tokens.items()):
                if current_time - timestamp > SecurityConfig.CSRF_TOKEN_LIFETIME:
                    expired_tokens.append(token_key)

            # 批量删除过期令牌
            for expired_token in expired_tokens:
                self._tokens.pop(expired_token, None)

        return token

    def validate_token(self, token: str) -> bool:
        """
        验证CSRF令牌

        Args:
            token: 要验证的CSRF令牌

        Returns:
            bool: 令牌是否有效
        """
        if not token:
            return False

        with self._lock:
            # 检查令牌是否存在
            if token not in self._tokens:
                return False

            # 检查令牌是否过期
            timestamp = self._tokens[token]
            if time.time() - timestamp > SecurityConfig.CSRF_TOKEN_LIFETIME:
                # 删除过期令牌
                self._tokens.pop(token, None)
                return False

            # 一次性令牌，验证成功后立即删除
            self._tokens.pop(token, None)
            return True

    def cleanup_expired_tokens(self) -> int:
        """
        手动清理所有过期令牌（可选的维护方法）

        Returns:
            int: 清理的过期令牌数量
        """
        current_time = time.time()
        expired_count = 0

        with self._lock:
            # 使用list()创建副本避免并发修改
            expired_tokens: List[str] = []
            for token_key, timestamp in list(self._tokens.items()):
                if current_time - timestamp > SecurityConfig.CSRF_TOKEN_LIFETIME:
                    expired_tokens.append(token_key)

            # 批量删除过期令牌
            for expired_token in expired_tokens:
                if self._tokens.pop(expired_token, None) is not None:
                    expired_count += 1

        return expired_count

    def get_active_token_count(self) -> int:
        """
        获取当前活跃令牌数量（用于监控和调试）

        Returns:
            int: 活跃令牌数量
        """
        with self._lock:
            return len(self._tokens)
