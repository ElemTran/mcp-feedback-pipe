"""
全局服务器池管理器
提供简化的MCP工具资源管理方案
"""

import threading
from typing import Dict
from backend.server_manager import ServerManager


class ServerPool:
    """全局服务器池管理器"""

    def __init__(self):
        self._servers: Dict[str, ServerManager] = {}
        self._lock = threading.RLock()

    def get_server(self, session_id: str = "default") -> ServerManager:
        """获取或创建服务器实例"""
        with self._lock:
            if session_id not in self._servers:
                self._servers[session_id] = ServerManager()
            return self._servers[session_id]

    def release_server(self, session_id: str = "default", immediate: bool = False):
        """释放服务器实例"""
        with self._lock:
            if immediate and session_id in self._servers:
                server = self._servers.pop(session_id)
                try:
                    server.stop_server()
                except Exception as e:
                    print(f"停止服务器 {session_id} 时出错: {e}")

    def shutdown(self):
        """关闭服务器池"""
        with self._lock:
            for server in self._servers.values():
                try:
                    server.stop_server()
                except Exception:
                    pass
            self._servers.clear()


# 全局服务器池实例
_server_pool = None
_pool_lock = threading.Lock()


def get_server_pool() -> ServerPool:
    """获取全局服务器池实例"""
    global _server_pool
    if _server_pool is None:
        with _pool_lock:
            if _server_pool is None:
                _server_pool = ServerPool()
    return _server_pool


def get_managed_server(session_id: str = "default") -> ServerManager:
    """获取托管的服务器实例"""
    return get_server_pool().get_server(session_id)


def release_managed_server(session_id: str = "default", immediate: bool = False):
    """释放托管的服务器实例"""
    get_server_pool().release_server(session_id, immediate)
