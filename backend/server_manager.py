"""
Web服务器管理模块
处理服务器启动和生命周期管理
"""

import logging
import threading
import time
from typing import Optional, Dict, Any, Union

try:
    import requests
    import requests.exceptions
except ImportError:
    requests = None

from backend.app import FeedbackApp
from backend.feedback_handler import FeedbackHandler
from backend.utils.network_utils import find_free_port
from backend.utils.browser_utils import open_feedback_browser
from backend.config import get_server_config, ServerConfig
from urllib.parse import quote
import webbrowser

# 配置模块级别的logger
logger = logging.getLogger(__name__)


class ServerManager:
    """Web服务器管理器"""

    def __init__(self) -> None:
        self.feedback_handler: FeedbackHandler = FeedbackHandler()
        self.app: Optional["FeedbackApp"] = None
        self.server_thread: Optional[threading.Thread] = None
        self.current_port: Optional[int] = None

        # 从配置加载常量值
        self._config: ServerConfig = get_server_config()

        # 服务器就绪检查相关配置
        self.server_ready_max_attempts = self._config.server_ready_max_attempts
        self.server_ready_check_interval = self._config.server_ready_check_interval
        self.server_ready_fallback_wait = self._config.server_ready_fallback_wait

        # 连接检测相关配置
        self.connection_check_max_retries = self._config.connection_check_max_retries
        self.connection_check_retry_interval = (
            self._config.connection_check_retry_interval
        )
        self.connection_check_timeout = self._config.connection_check_timeout

        # 反馈等待相关配置
        self.feedback_polling_interval = self._config.feedback_polling_interval
        self.feedback_log_interval = self._config.feedback_log_interval
        self.feedback_result_timeout = self._config.feedback_result_timeout

    def start_server(
        self,
        work_summary: str = "",
        timeout_seconds: int = 300,
        suggest: str = "",
        debug: bool = True,
        use_reloader: bool = False,
    ) -> int:
        """启动Web服务器 - TURBO模式（终极性能优化）"""
        # 性能监控: 服务器启动总时间开始计时
        server_startup_start_time = time.perf_counter()
        
        # 添加详细的调试日志
        logger.info("[SERVER_MANAGER_DEBUG] start_server method called")
        logger.info(f"[SERVER_MANAGER_DEBUG] Parameters - work_summary length: {len(work_summary)}, timeout_seconds: {timeout_seconds}, suggest length: {len(suggest)}, debug: {debug}, use_reloader: {use_reloader}")
        
        logger.info("🚀 开始TURBO服务器启动流程")

        # 创建应用实例 - 使用关键字参数确保正确传递
        logger.info("[SERVER_MANAGER_DEBUG] About to create FeedbackApp instance...")
        app_creation_start_time = time.perf_counter()
        
        try:
            self.app = FeedbackApp(
                feedback_handler=self.feedback_handler,
                work_summary=work_summary,
                suggest_json=suggest,
                timeout_seconds=timeout_seconds,
            )
            app_creation_duration = time.perf_counter() - app_creation_start_time
            logger.info(f"[SERVER_MANAGER_DEBUG] FeedbackApp instance created successfully in {app_creation_duration:.3f} seconds")
            logger.info(f"性能监控: 应用实例创建耗时 {app_creation_duration:.3f} 秒")
        except Exception as e:
            app_creation_duration = time.perf_counter() - app_creation_start_time
            logger.error(f"[SERVER_MANAGER_DEBUG] Failed to create FeedbackApp instance after {app_creation_duration:.3f} seconds: {e}")
            raise

        logger.info("[SERVER_MANAGER_DEBUG] About to allocate port...")
        port_allocation_start_time = time.perf_counter()
        
        # 获取首选Web端口
        preferred_port_to_use = getattr(self._config, 'preferred_web_port', None)
        logger.info(f"[SERVER_MANAGER_DEBUG] Preferred port from config: {preferred_port_to_use}")
        logger.info(f"[SERVER_MANAGER_DEBUG] About to call find_free_port with preferred_port: {preferred_port_to_use}")
        
        try:
            self.current_port = find_free_port(preferred_port=preferred_port_to_use)
            port_allocation_duration = time.perf_counter() - port_allocation_start_time
            logger.info(f"[SERVER_MANAGER_DEBUG] find_free_port returned: {self.current_port} in {port_allocation_duration:.3f} seconds")
            logger.info(f"性能监控: 端口分配耗时 {port_allocation_duration:.3f} 秒")
        except Exception as e:
            port_allocation_duration = time.perf_counter() - port_allocation_start_time
            logger.error(f"[SERVER_MANAGER_DEBUG] find_free_port failed after {port_allocation_duration:.3f} seconds: {e}")
            raise

        # 启动服务器线程
        def run_server() -> None:
            try:
                self.app.run(
                    host="127.0.0.1",
                    port=self.current_port,
                    debug=debug,
                    use_reloader=use_reloader,
                )
                # If app.run() returns, it means the server was shut down gracefully (e.g., by a signal)
                # Log this normal shutdown.
                logger.info(f"Flask server on port {self.current_port} shut down gracefully.")
            except OSError as e:
                logger.error(f"服务器启动失败 - 网络或端口错误: {e}")
            except ImportError as e:
                logger.error(f"服务器启动失败 - 缺少依赖模块: {e}")
            except Exception as e:
                logger.error(f"服务器启动失败 - 未知错误: {e}")

        logger.info("[SERVER_MANAGER_DEBUG] About to create and start server thread...")
        thread_creation_start_time = time.perf_counter()
        
        try:
            self.server_thread = threading.Thread(target=run_server, daemon=True)
            logger.info(f"[SERVER_MANAGER_DEBUG] Server thread created successfully")
            
            self.server_thread.start()
            thread_creation_duration = time.perf_counter() - thread_creation_start_time
            logger.info(f"[SERVER_MANAGER_DEBUG] Server thread started successfully in {thread_creation_duration:.3f} seconds")
            logger.info(f"性能监控: 服务器线程创建与启动耗时 {thread_creation_duration:.3f} 秒")
        except Exception as e:
            thread_creation_duration = time.perf_counter() - thread_creation_start_time
            logger.error(f"[SERVER_MANAGER_DEBUG] Failed to create/start server thread after {thread_creation_duration:.3f} seconds: {e}")
            raise

        # TURBO模式：跳过所有检查，信任启动，绝对最速
        parallel_start_time = time.perf_counter()
        logger.info("⚡ TURBO模式启动 - 跳过检查，绝对最速")
        
        # TURBO模式：跳过检查的最小启动流程
        logger.info("[SERVER_MANAGER_DEBUG] About to call _wait_for_server_ready...")
        wait_ready_start = time.perf_counter()
        
        try:
            server_ready_result = self._wait_for_server_ready()
            wait_ready_duration = time.perf_counter() - wait_ready_start
            logger.info(f"[SERVER_MANAGER_DEBUG] _wait_for_server_ready completed in {wait_ready_duration:.3f} seconds")
            logger.info(f"[SERVER_MANAGER_DEBUG] _wait_for_server_ready returned: {server_ready_result}")
        except Exception as e:
            wait_ready_duration = time.perf_counter() - wait_ready_start
            logger.error(f"[SERVER_MANAGER_DEBUG] _wait_for_server_ready failed after {wait_ready_duration:.3f} seconds: {e}")
            raise
        
        # 异步启动浏览器，不等待结果
        try:
            browser_thread = threading.Thread(
                target=open_feedback_browser,
                args=(self.current_port, work_summary, suggest),
                daemon=True
            )
            browser_thread.start()
            logger.debug("TURBO模式：浏览器异步启动完成")
        except Exception as e:
            logger.debug(f"TURBO模式浏览器启动异常: {e}")
        
        parallel_duration = time.perf_counter() - parallel_start_time
        logger.info(f"性能监控: TURBO启动总耗时 {parallel_duration:.3f} 秒")

        # 性能监控: 服务器启动总时间结束计时
        total_startup_duration = time.perf_counter() - server_startup_start_time
        logger.info(f"性能监控: 服务器启动总耗时 {total_startup_duration:.3f} 秒")
        
        logger.info(f"[SERVER_MANAGER_DEBUG] start_server method completed successfully")
        logger.info(f"[SERVER_MANAGER_DEBUG] Returning port: {self.current_port}")

        return self.current_port

    def _wait_for_server_ready(self, skip_check: bool = False) -> bool:
        """等待服务器就绪 - 增加了基本的端口检查"""
        logger.info(f"[WAIT_SERVER_READY_DEBUG] _wait_for_server_ready method called with skip_check: {skip_check}")
        
        if skip_check:  # Still allow explicit skipping if ever needed
            logger.info("[WAIT_SERVER_READY_DEBUG] 服务器就绪检查被跳过 (skip_check=True)")
            logger.info("服务器就绪检查被跳过 (skip_check=True)")
            time.sleep(0.01)
            return True

        if not self.current_port:
            logger.error("[WAIT_SERVER_READY_DEBUG] 无法检查服务器就绪状态：当前端口未设置。")
            logger.error("无法检查服务器就绪状态：当前端口未设置。")
            return False

        logger.info(f"[WAIT_SERVER_READY_DEBUG] 开始检查服务器端口 {self.current_port} 是否就绪...")
        logger.info(f"[WAIT_SERVER_READY_DEBUG] Configuration - max_attempts: {self.server_ready_max_attempts}, check_interval: {self.server_ready_check_interval}")
        logger.info(f"开始检查服务器端口 {self.current_port} 是否就绪...")
        logger.info(f"[WAIT_SERVER_READY_DEBUG] About to enter attempt loop...")
        
        for attempt in range(self.server_ready_max_attempts):
            logger.info(f"[WAIT_SERVER_READY_DEBUG] Attempt {attempt + 1}/{self.server_ready_max_attempts} - trying socket connection to 127.0.0.1:{self.current_port}")
            try:
                # 尝试创建一个到服务器端口的套接字连接
                import socket
                connection_start = time.time()
                logger.debug(f"[WAIT_SERVER_READY_DEBUG] Creating socket connection to 127.0.0.1:{self.current_port} with 0.5s timeout...")
                
                with socket.create_connection(("127.0.0.1", self.current_port), timeout=0.5):
                    connection_duration = time.time() - connection_start
                    logger.info(f"[WAIT_SERVER_READY_DEBUG] 服务器端口 {self.current_port} 已成功连接 (尝试 {attempt + 1})，连接耗时 {connection_duration:.3f}秒")
                    logger.info(f"服务器端口 {self.current_port} 已成功连接 (尝试 {attempt + 1})。")
                    return True
                    
            except (socket.error, socket.timeout) as e:
                connection_duration = time.time() - connection_start
                logger.info(f"[WAIT_SERVER_READY_DEBUG] Socket connection failed on attempt {attempt + 1}, duration: {connection_duration:.3f}s, error: {type(e).__name__}: {e}")
                logger.debug(
                    f"等待服务器端口 {self.current_port} 就绪... "
                    f"(尝试 {attempt + 1}/{self.server_ready_max_attempts}) - 错误: {e}"
                )
                
                if attempt < self.server_ready_max_attempts - 1:
                    logger.debug(f"[WAIT_SERVER_READY_DEBUG] Sleeping {self.server_ready_check_interval}s before next attempt...")
                    time.sleep(self.server_ready_check_interval)
                else:  # Last attempt
                    logger.error(f"[WAIT_SERVER_READY_DEBUG] All {self.server_ready_max_attempts} attempts failed")
                    logger.error(
                        f"服务器端口 {self.current_port} 在 "
                        f"{self.server_ready_max_attempts} 次尝试后仍未就绪。"
                    )
                    # Fallback: wait a bit longer as a last resort, then assume failure.
                    # This matches original fallback logic if requests was None.
                    logger.info(f"[WAIT_SERVER_READY_DEBUG] 执行最后的回退等待 {self.server_ready_fallback_wait} 秒...")
                    logger.info(f"执行最后的等待 {self.server_ready_fallback_wait} 秒...")
                    
                    fallback_start = time.time()
                    time.sleep(self.server_ready_fallback_wait)
                    fallback_duration = time.time() - fallback_start
                    logger.info(f"[WAIT_SERVER_READY_DEBUG] 回退等待完成，实际耗时 {fallback_duration:.3f}秒")
                    
                    # Re-check one last time after fallback wait
                    logger.info(f"[WAIT_SERVER_READY_DEBUG] 执行回退等待后的最终连接尝试...")
                    try:
                        final_connection_start = time.time()
                        with socket.create_connection(("127.0.0.1", self.current_port), timeout=1.0):
                            final_connection_duration = time.time() - final_connection_start
                            logger.info(f"[WAIT_SERVER_READY_DEBUG] 服务器端口 {self.current_port} 在回退等待后成功连接，连接耗时 {final_connection_duration:.3f}秒")
                            logger.info(f"服务器端口 {self.current_port} 在回退等待后成功连接。")
                            return True
                    except (socket.error, socket.timeout) as final_e:
                        final_connection_duration = time.time() - final_connection_start
                        logger.error(f"[WAIT_SERVER_READY_DEBUG] 回退等待后的最终连接尝试失败，耗时 {final_connection_duration:.3f}秒, 错误: {type(final_e).__name__}: {final_e}")
                        logger.error(f"服务器端口 {self.current_port} 在回退等待后仍然无法连接。")
                        return False
        
        logger.error(f"[WAIT_SERVER_READY_DEBUG] _wait_for_server_ready returning False - should not reach this point")
        return False  # Should not be reached if logic is correct

    def wait_for_feedback(
        self, timeout_seconds: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        简化版超时控制：宽容期 + 连接依赖模式
        1. 60秒宽容期：等待WebSocket连接
        2. 连接依赖模式：持续等待直到WebSocket断开或收到结果

        Args:
            timeout_seconds: 最大等待时间（秒），如果未指定则使用默认值

        Returns:
            Optional[dict]: 前端提交的结果或超时结果
        """
        logger.info(f"[WAIT_FEEDBACK_DEBUG] wait_for_feedback method called with timeout_seconds: {timeout_seconds}")
        
        # 设置超时时间
        if timeout_seconds is None:
            timeout_seconds = self._config.default_timeout
            logger.info(f"[WAIT_FEEDBACK_DEBUG] Using default timeout from config: {timeout_seconds}")
        else:
            logger.info(f"[WAIT_FEEDBACK_DEBUG] Using provided timeout_seconds: {timeout_seconds}")
        
        # 阶段1：60秒宽容期 - 等待WebSocket连接
        grace_period = 60
        logger.info(f"[WAIT_FEEDBACK_DEBUG] 开始等待反馈：{grace_period}秒宽容期，总超时 {timeout_seconds} 秒")
        logger.info(f"开始等待反馈：{grace_period}秒宽容期，总超时 {timeout_seconds} 秒")
        
        logger.info(f"[WAIT_FEEDBACK_DEBUG] About to call _wait_for_websocket_connection with grace_period: {grace_period}")
        websocket_wait_start = time.time()
        
        if not self._wait_for_websocket_connection(grace_period):
            websocket_wait_duration = time.time() - websocket_wait_start
            logger.warning(f"[WAIT_FEEDBACK_DEBUG] _wait_for_websocket_connection failed after {websocket_wait_duration:.3f} seconds")
            logger.warning(f"[WAIT_FEEDBACK_DEBUG] Returning connection_timeout result")
            return self._create_timeout_result("connection_timeout")
        
        websocket_wait_duration = time.time() - websocket_wait_start
        logger.info(f"[WAIT_FEEDBACK_DEBUG] _wait_for_websocket_connection succeeded in {websocket_wait_duration:.3f} seconds")
        
        # 阶段2：连接依赖模式 - 纯粹等待结果
        logger.info("[WAIT_FEEDBACK_DEBUG] WebSocket连接已建立，进入连接依赖模式")
        logger.info("WebSocket连接已建立，进入连接依赖模式")
        start_time = time.time()
        logger.info(f"[WAIT_FEEDBACK_DEBUG] Starting feedback polling loop at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        loop_iteration = 0
        while True:
            loop_iteration += 1
            logger.debug(f"[WAIT_FEEDBACK_DEBUG] Loop iteration {loop_iteration} at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.debug(f"[DEBUG wait_for_feedback] {time.strftime('%Y-%m-%d %H:%M:%S')} - has_active_clients: {self.app.has_active_clients()}")
            current_time = time.time()
            elapsed_time = current_time - start_time
            
            # 检查总超时
            if elapsed_time >= timeout_seconds:
                logger.warning(f"[WAIT_FEEDBACK_DEBUG] 总超时触发，已等待 {elapsed_time:.1f} 秒")
                logger.warning(f"总超时触发，已等待 {elapsed_time:.1f} 秒")
                return self._create_timeout_result("total_timeout")
            
            # 尝试获取结果
            logger.debug(f"[WAIT_FEEDBACK_DEBUG] Attempting to get result from feedback_handler (timeout=1)...")
            get_result_start = time.time()
            result = self.feedback_handler.get_result(timeout=1)
            get_result_duration = time.time() - get_result_start
            logger.debug(f"[WAIT_FEEDBACK_DEBUG] feedback_handler.get_result took {get_result_duration:.3f}s, result: {result is not None}")
            
            if result is not None:
                logger.info(f"[WAIT_FEEDBACK_DEBUG] 收到反馈结果，总等待时间 {elapsed_time:.1f} 秒")
                logger.info(f"收到反馈结果，总等待时间 {elapsed_time:.1f} 秒")
                logger.info(f"[WAIT_FEEDBACK_DEBUG] Result type: {type(result)}, keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
                return result
            
            # 检查WebSocket连接状态
            has_active_clients = self.app.has_active_clients() if self.app else False
            logger.debug(f"[WAIT_FEEDBACK_DEBUG] has_active_clients: {has_active_clients}")
            
            if not has_active_clients:
                logger.debug(f"[DEBUG wait_for_feedback] {time.strftime('%Y-%m-%d %H:%M:%S')} - active_clients: {self.app.active_clients if self.app else 'No app'}")
                logger.info(f"[WAIT_FEEDBACK_DEBUG] WebSocket连接已断开")
                logger.info("WebSocket连接已断开")
                return self._create_timeout_result("websocket_disconnected")

    def _wait_for_websocket_connection(self, grace_period: int) -> bool:
        """等待WebSocket连接建立"""
        start_time = time.time()
        
        while time.time() - start_time < grace_period:
            if self.app and self.app.has_active_clients():
                return True
            time.sleep(1)
        
        logger.warning(f"WebSocket连接未在{grace_period}秒内建立")
        return False
    
    def _create_timeout_result(self, reason: str) -> Dict[str, Any]:
        """创建统一格式的超时结果"""
        from datetime import datetime
        
        return {
            'text': '',
            'images': [],
            'is_timeout': True,
            'timeout_reason': reason,
            'timestamp': datetime.now().isoformat()
        }

    def stop_server(self) -> None:
        """停止服务器"""
        try:
            # 不再发送关闭请求，让Flask服务器自然结束
            # 因为服务器线程是daemon线程，会在主程序结束时自动清理

            # 清理资源
            self.feedback_handler.clear_queue()
            self.current_port = None
            self.app = None

        except (AttributeError, TypeError) as e:
            logger.warning(f"服务器停止过程中出现状态错误: {e}")
            # 强制清理
            self.current_port = None
            self.app = None
        except Exception as e:
            logger.error(f"服务器停止过程中出现未知错误: {e}")
            # 强制清理
            self.current_port = None
            self.app = None

    def get_server_info(self) -> Dict[str, Union[int, str, bool, None]]:
        """获取服务器信息"""
        return {
            "port": self.current_port,
            "url": (
                f"http://127.0.0.1:{self.current_port}" if self.current_port else None
            ),
            "is_running": (
                self.server_thread.is_alive() if self.server_thread else False
            ),
        }

    def _check_client_disconnection(self) -> bool:
        """检测客户端连接状态（带重试机制）"""
        # 性能监控: 客户端连接检测开始计时
        connection_check_start_time = time.perf_counter()

        if requests is None:
            # requests模块不可用，跳过连接检测
            check_duration = time.perf_counter() - connection_check_start_time
            logger.debug(
                f"性能监控: 客户端连接检测(requests不可用)耗时 {check_duration:.4f} 秒"
            )
            return False

        total_ping_duration = 0.0
        successful_pings = 0

        for attempt in range(self.connection_check_max_retries + 1):
            try:
                # 尝试ping服务器自身，检查网络状况
                ping_start_time = time.perf_counter()
                response = requests.get(
                    f"http://127.0.0.1:{self.current_port}/ping",
                    timeout=self.connection_check_timeout,
                )
                ping_duration = time.perf_counter() - ping_start_time
                total_ping_duration += ping_duration

                if response.status_code == 200:
                    successful_pings += 1
                    total_check_duration = (
                        time.perf_counter() - connection_check_start_time
                    )
                    logger.debug(
                        f"性能监控: 客户端连接检测成功，总耗时 {total_check_duration:.4f} 秒，ping耗时 {ping_duration:.4f} 秒"
                    )
                    return False  # 连接正常
                else:
                    logger.debug(
                        f"连接检测ping失败，状态码: {response.status_code}，耗时 {ping_duration:.4f} 秒"
                    )

            except requests.exceptions.ConnectionError as e:
                # 记录连接错误重试日志
                if attempt < self.connection_check_max_retries:
                    logger.debug(
                        f"连接检测失败 - 连接错误 (尝试 {attempt + 1}/{self.connection_check_max_retries + 1}): {e}"
                    )
                    time.sleep(self.connection_check_retry_interval)
                else:
                    logger.warning(f"连接检测最终失败 - 连接错误: {e}")
            except requests.exceptions.Timeout as e:
                # 记录超时错误重试日志
                if attempt < self.connection_check_max_retries:
                    logger.debug(
                        f"连接检测失败 - 超时 (尝试 {attempt + 1}/{self.connection_check_max_retries + 1}): {e}"
                    )
                    time.sleep(self.connection_check_retry_interval)
                else:
                    logger.warning(f"连接检测最终失败 - 超时: {e}")
            except requests.exceptions.RequestException as e:
                # 记录其他请求错误重试日志
                if attempt < self.connection_check_max_retries:
                    logger.debug(
                        f"连接检测失败 - 请求错误 (尝试 {attempt + 1}/{self.connection_check_max_retries + 1}): {e}"
                    )
                    time.sleep(self.connection_check_retry_interval)
                else:
                    logger.warning(f"连接检测最终失败 - 请求错误: {e}")
            except Exception as e:
                # 记录未预期错误重试日志
                if attempt < self.connection_check_max_retries:
                    logger.debug(
                        f"连接检测失败 - 未预期错误 (尝试 {attempt + 1}/{self.connection_check_max_retries + 1}): {e}"
                    )
                    time.sleep(self.connection_check_retry_interval)
                else:
                    logger.error(f"连接检测最终失败 - 未预期错误: {e}")

        # 所有重试都失败，认为连接断开
        total_check_duration = time.perf_counter() - connection_check_start_time
        avg_ping_duration = (
            total_ping_duration / successful_pings if successful_pings > 0 else 0
        )
        logger.warning(
            f"性能监控: 客户端连接检测失败，总耗时 {total_check_duration:.3f} 秒，成功ping次数 {successful_pings}，平均ping耗时 {avg_ping_duration:.4f} 秒"
        )
        return True

    def _is_server_healthy(self) -> bool:
        """检查服务器健康状态"""
        if not self.current_port:
            return False
        if not self.server_thread or not self.server_thread.is_alive():
            return False
        return True

    def _cleanup_on_disconnection(self) -> None:
        """连接断开时的资源清理"""
        logger.info("执行连接断开清理...")
        self.feedback_handler.clear_queue()
        # 不重置端口和应用，让自然清理处理

    def find_free_port(self, preferred_port: Optional[int] = None) -> int:
        """查找空闲端口（兼容性方法）"""
        return find_free_port(preferred_port=preferred_port)

    def _open_browser(self, work_summary: str) -> None:
        """打开浏览器（兼容性方法）"""
        try:
            encoded_summary = quote(work_summary)
            url = f"http://127.0.0.1:{self.current_port}/?work_summary={encoded_summary}"
            webbrowser.open(url)
        except Exception as e:
            print(f"无法自动打开浏览器: {e}")
            print(f"请手动访问: http://127.0.0.1:{self.current_port}/?work_summary={quote(work_summary)}")

    def update_user_activity_status(self, is_active: bool, remaining_seconds: int) -> None:
        """更新用户活动状态（兼容性方法）"""
        # TODO: 实现用户活动状态更新逻辑
        # 这个方法目前是为了测试兼容性而添加的占位符
        logger.debug(f"用户活动状态更新: active={is_active}, remaining={remaining_seconds}秒")
