"""
全局服务器池管理器 v2.0
提供多端口并发的MCP工具资源管理方案
支持服务器池状态查询、端口管理和自动清理
"""

import threading
import time
import logging
import json
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from backend.server_manager import ServerManager
from backend.config import get_server_config

logger = logging.getLogger(__name__)

# 状态文件路径
STATUS_FILE = os.path.join(os.getcwd(), ".mcp_server_pool_status.json")


class ServerStatus(Enum):
    """服务器状态枚举"""
    IDLE = "idle"           # 空闲状态
    STARTING = "starting"   # 启动中  
    RUNNING = "running"     # 运行中
    STOPPING = "stopping"  # 停止中
    ERROR = "error"         # 错误状态


@dataclass
class ServerInfo:
    """服务器实例信息"""
    session_id: str
    port: Optional[int]
    status: ServerStatus
    created_at: float
    last_activity: float
    work_summary: str = ""
    timeout_seconds: int = 300
    error_message: str = ""


class EnhancedServerPool:
    """增强的服务器池管理器"""

    def __init__(self):
        self._servers: Dict[str, ServerManager] = {}
        self._server_info: Dict[str, ServerInfo] = {}
        self._port_map: Dict[int, str] = {}  # 端口到session_id的映射
        self._lock = threading.RLock()
        self._config = get_server_config()
        
        # 启动清理线程
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_worker,
            daemon=True,
            name="ServerPool-Cleanup"
        )
        self._cleanup_running = True
        self._cleanup_thread.start()
        
        logger.info("增强服务器池已启动，支持多端口并发管理")
        
        # 加载持久化状态
        self._load_status_from_file()

    def get_server(self, session_id: str = "default") -> ServerManager:
        """获取或创建服务器实例"""
        with self._lock:
            current_time = time.time()
            
            if session_id not in self._servers:
                # 创建新的服务器实例
                self._servers[session_id] = ServerManager()
                self._server_info[session_id] = ServerInfo(
                    session_id=session_id,
                    port=None,
                    status=ServerStatus.IDLE,
                    created_at=current_time,
                    last_activity=current_time
                )
                logger.info(f"创建新服务器实例: {session_id}")
            else:
                # 更新活动时间
                self._server_info[session_id].last_activity = current_time
            
            return self._servers[session_id]

    def start_server_in_pool(
        self, 
        session_id: str,
        work_summary: str = "",
        timeout_seconds: int = 300,
        suggest: str = ""
    ) -> Tuple[ServerManager, int]:
        """在池中启动服务器并返回实例和端口"""
        with self._lock:
            server = self.get_server(session_id)
            
            # 更新服务器信息
            info = self._server_info[session_id]
            info.status = ServerStatus.STARTING
            info.work_summary = work_summary
            info.timeout_seconds = timeout_seconds
            info.last_activity = time.time()
            
            try:
                # 确定要使用的端口（避免与已占用端口冲突）
                used_ports = set(self._port_map.keys())
                preferred_port = self._config.preferred_web_port
                
                # 如果首选端口已被占用，寻找下一个可用端口
                target_port = preferred_port
                while target_port in used_ports:
                    target_port += 1
                    if target_port > 65535:  # 端口溢出保护
                        # 从1024开始重新查找
                        target_port = 1024
                        break
                
                # 临时修改服务器管理器的首选端口
                original_preferred = server._config.preferred_web_port
                server._config.preferred_web_port = target_port
                
                try:
                    # 启动服务器
                    port = server.start_server(
                        work_summary=work_summary,
                        timeout_seconds=timeout_seconds,
                        suggest=suggest
                    )
                finally:
                    # 恢复原始配置
                    server._config.preferred_web_port = original_preferred
                
                # 验证返回的端口
                if port != target_port:
                    logger.info(f"服务器 {session_id} 分配的端口 {port} 与目标端口 {target_port} 不同")
                
                # 更新端口映射和状态
                info.port = port
                info.status = ServerStatus.RUNNING
                self._port_map[port] = session_id
                
                logger.info(f"服务器 {session_id} 在端口 {port} 启动成功")
                
                # 保存状态到文件
                self._save_status_to_file()
                
                return server, port
                
            except Exception as e:
                info.status = ServerStatus.ERROR
                info.error_message = str(e)
                logger.error(f"服务器 {session_id} 启动失败: {e}")
                raise

    def get_pool_status(self) -> Dict:
        """获取服务器池状态"""
        with self._lock:
            current_time = time.time()
            
            status = {
                "total_servers": len(self._servers),
                "active_servers": 0,
                "ports_in_use": list(self._port_map.keys()),
                "servers": []
            }
            
            for session_id, info in self._server_info.items():
                server_data = {
                    "session_id": session_id,
                    "port": info.port,
                    "status": info.status.value,
                    "work_summary": info.work_summary[:50] + "..." if len(info.work_summary) > 50 else info.work_summary,
                    "timeout_seconds": info.timeout_seconds,
                    "uptime": current_time - info.created_at,
                    "idle_time": current_time - info.last_activity,
                    "url": f"http://127.0.0.1:{info.port}" if info.port else None
                }
                
                if info.status == ServerStatus.RUNNING:
                    status["active_servers"] += 1
                    
                if info.error_message:
                    server_data["error"] = info.error_message
                    
                status["servers"].append(server_data)
            
            return status

    def get_servers_by_status(self, status: ServerStatus) -> List[str]:
        """根据状态获取服务器列表"""
        with self._lock:
            return [
                session_id for session_id, info in self._server_info.items()
                if info.status == status
            ]

    def find_server_by_port(self, port: int) -> Optional[str]:
        """根据端口查找服务器session_id"""
        with self._lock:
            return self._port_map.get(port)

    def release_server(self, session_id: str = "default", immediate: bool = False):
        """释放服务器实例"""
        with self._lock:
            if session_id not in self._servers:
                return
                
            info = self._server_info[session_id]
            
            if immediate:
                # 立即清理
                self._cleanup_server(session_id)
            else:
                # 标记为停止中，由清理线程处理
                info.status = ServerStatus.STOPPING
                logger.info(f"服务器 {session_id} 标记为停止中，将由清理线程处理")

    def _cleanup_server(self, session_id: str):
        """清理指定服务器"""
        try:
            if session_id in self._servers:
                server = self._servers.pop(session_id)
                info = self._server_info.pop(session_id, None)
                
                # 清理端口映射
                if info and info.port:
                    self._port_map.pop(info.port, None)
                
                # 停止服务器
                try:
                    server.stop_server()
                except Exception as e:
                    logger.warning(f"停止服务器 {session_id} 时出错: {e}")
                
                logger.info(f"服务器 {session_id} 已清理")
                
                # 清理后保存状态
                self._save_status_to_file()
                
        except Exception as e:
            logger.error(f"清理服务器 {session_id} 时出错: {e}")

    def _cleanup_worker(self):
        """清理工作线程"""
        while self._cleanup_running:
            try:
                current_time = time.time()
                cleanup_list = []
                
                with self._lock:
                    for session_id, info in self._server_info.items():
                        # 清理条件：
                        # 1. 状态为STOPPING
                        # 2. 空闲时间超过配置阈值
                        # 3. 错误状态超过一定时间
                        should_cleanup = False
                        
                        if info.status == ServerStatus.STOPPING:
                            should_cleanup = True
                        elif info.status == ServerStatus.IDLE:
                            idle_time = current_time - info.last_activity
                            if idle_time > self._config.idle_timeout:
                                should_cleanup = True
                        elif info.status == ServerStatus.ERROR:
                            error_time = current_time - info.last_activity
                            if error_time > 300:  # 错误状态5分钟后清理
                                should_cleanup = True
                        
                        if should_cleanup:
                            cleanup_list.append(session_id)
                
                # 执行清理（在锁外执行避免死锁）
                for session_id in cleanup_list:
                    with self._lock:
                        self._cleanup_server(session_id)
                
                # 休眠
                time.sleep(self._config.cleanup_interval)
                
            except Exception as e:
                logger.error(f"清理工作线程出错: {e}")
                time.sleep(10)  # 出错时等待更长时间

    def shutdown(self):
        """关闭服务器池"""
        logger.info("开始关闭服务器池...")
        
        # 停止清理线程
        self._cleanup_running = False
        if self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=5)
        
        with self._lock:
            # 清理所有服务器
            for session_id in list(self._servers.keys()):
                self._cleanup_server(session_id)
            
            self._servers.clear()
            self._server_info.clear()
            self._port_map.clear()
        
        logger.info("服务器池已关闭")

    def get_recommended_ssh_commands(self) -> List[str]:
        """获取推荐的SSH端口转发命令"""
        with self._lock:
            commands = []
            local_port = self._config.recommended_local_forward_port
            
            for port in sorted(self._port_map.keys()):
                session_id = self._port_map[port]
                info = self._server_info[session_id]
                
                if info.status == ServerStatus.RUNNING:
                    commands.append(
                        f"# {session_id}: {info.work_summary[:30]}...\n"
                        f"ssh -L {local_port}:127.0.0.1:{port} your_user@your_server"
                    )
                    local_port += 1  # 为下一个分配不同的本地端口
            
            return commands

    def _save_status_to_file(self):
        """保存状态到文件"""
        try:
            status = self.get_pool_status()
            # 添加时间戳
            status['last_updated'] = time.time()
            status['last_updated_readable'] = time.strftime('%Y-%m-%d %H:%M:%S')
            
            with open(STATUS_FILE, 'w', encoding='utf-8') as f:
                json.dump(status, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.warning(f"保存状态文件失败: {e}")

    def _load_status_from_file(self):
        """从文件加载状态（仅用于验证服务器是否仍在运行）"""
        try:
            if os.path.exists(STATUS_FILE):
                with open(STATUS_FILE, 'r', encoding='utf-8') as f:
                    saved_status = json.load(f)
                
                # 验证保存的服务器是否仍在运行
                for server_info in saved_status.get('servers', []):
                    port = server_info.get('port')
                    if port:
                        self._verify_server_running(port, server_info['session_id'])
                        
        except Exception as e:
            logger.warning(f"加载状态文件失败: {e}")

    def _verify_server_running(self, port: int, session_id: str):
        """验证服务器是否仍在运行"""
        try:
            import requests
            response = requests.get(f"http://127.0.0.1:{port}/ping", timeout=2)
            if response.status_code == 200:
                logger.info(f"检测到运行中的服务器: {session_id} (端口 {port})")
                # 注意：这里不重新创建ServerManager实例，只是记录发现的服务器
        except:
            # 服务器已不存在，忽略
            pass


def load_server_status_from_file() -> Optional[Dict]:
    """从文件加载服务器状态（独立函数，供外部调用）"""
    try:
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"读取状态文件失败: {e}")
    return None


# 全局服务器池实例
_server_pool: Optional[EnhancedServerPool] = None
_pool_lock = threading.Lock()


def get_server_pool() -> EnhancedServerPool:
    """获取全局服务器池实例"""
    global _server_pool
    if _server_pool is None:
        with _pool_lock:
            if _server_pool is None:
                _server_pool = EnhancedServerPool()
    return _server_pool


def get_managed_server(session_id: str = "default") -> ServerManager:
    """获取托管的服务器实例"""
    return get_server_pool().get_server(session_id)


def release_managed_server(session_id: str = "default", immediate: bool = False):
    """释放托管的服务器实例"""
    get_server_pool().release_server(session_id, immediate)
