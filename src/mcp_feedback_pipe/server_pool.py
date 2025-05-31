"""
全局服务器池管理器
提供更优雅的MCP工具资源管理方案
"""

import threading
import time
import weakref
from typing import Dict, Optional
from .server_manager import ServerManager


class ServerPool:
    """全局服务器池管理器"""
    
    def __init__(self):
        self._servers: Dict[str, ServerManager] = {}
        self._lock = threading.RLock()
        self._cleanup_thread = None
        self._running = True
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self):
        """启动清理线程"""
        def cleanup_worker():
            while self._running:
                try:
                    time.sleep(5)  # 每5秒检查一次
                    self._cleanup_idle_servers()
                except Exception as e:
                    print(f"清理线程错误: {e}")
        
        self._cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        self._cleanup_thread.start()
    
    def _cleanup_idle_servers(self):
        """清理空闲的服务器"""
        with self._lock:
            to_remove = []
            for session_id, server in self._servers.items():
                # 检查服务器是否空闲（可以根据需要添加更复杂的逻辑）
                if hasattr(server, '_last_activity'):
                    if time.time() - server._last_activity > 30:  # 30秒无活动
                        to_remove.append(session_id)
            
            for session_id in to_remove:
                server = self._servers.pop(session_id, None)
                if server:
                    try:
                        server.stop_server()
                    except Exception as e:
                        print(f"清理服务器 {session_id} 时出错: {e}")
    
    def get_server(self, session_id: str = "default") -> ServerManager:
        """获取或创建服务器实例"""
        with self._lock:
            if session_id not in self._servers:
                self._servers[session_id] = ServerManager()
            
            server = self._servers[session_id]
            server._last_activity = time.time()  # 更新活动时间
            return server
    
    def release_server(self, session_id: str = "default", immediate: bool = False):
        """释放服务器实例"""
        with self._lock:
            if immediate and session_id in self._servers:
                server = self._servers.pop(session_id)
                try:
                    server.stop_server()
                except Exception as e:
                    print(f"立即清理服务器 {session_id} 时出错: {e}")
            elif session_id in self._servers:
                # 标记为可清理，但不立即清理
                self._servers[session_id]._last_activity = time.time() - 25  # 5秒后会被清理
    
    def shutdown(self):
        """关闭服务器池"""
        self._running = False
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