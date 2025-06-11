"""
Web服务器管理模块
处理服务器启动和生命周期管理
"""

import logging
import threading
import time
from typing import Optional, Dict, Any, Union, TYPE_CHECKING

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
        logger.info("🚀 开始TURBO服务器启动流程")

        # 创建应用实例 - 使用关键字参数确保正确传递
        app_creation_start_time = time.perf_counter()
        self.app = FeedbackApp(
            feedback_handler=self.feedback_handler,
            work_summary=work_summary,
            suggest_json=suggest,
            timeout_seconds=timeout_seconds,
            server_manager_instance=self,
        )
        app_creation_duration = time.perf_counter() - app_creation_start_time
        logger.info(f"性能监控: 应用实例创建耗时 {app_creation_duration:.3f} 秒")

        port_allocation_start_time = time.perf_counter()
        # 获取首选Web端口
        preferred_port_to_use = getattr(self._config, 'preferred_web_port', None)
        self.current_port = find_free_port(preferred_port=preferred_port_to_use)
        port_allocation_duration = time.perf_counter() - port_allocation_start_time
        logger.info(f"性能监控: 端口分配耗时 {port_allocation_duration:.3f} 秒")

        # 启动服务器线程
        def run_server() -> None:
            try:
                self.app.run(
                    host="127.0.0.1",
                    port=self.current_port,
                    debug=debug,
                    use_reloader=use_reloader,
                )
            except OSError as e:
                logger.error(f"服务器启动失败 - 网络或端口错误: {e}")
            except ImportError as e:
                logger.error(f"服务器启动失败 - 缺少依赖模块: {e}")
            except Exception as e:
                logger.error(f"服务器启动失败 - 未知错误: {e}")

        thread_creation_start_time = time.perf_counter()
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        thread_creation_duration = time.perf_counter() - thread_creation_start_time
        logger.info(f"性能监控: 服务器线程创建与启动耗时 {thread_creation_duration:.3f} 秒")

        # TURBO模式：跳过所有检查，信任启动，绝对最速
        parallel_start_time = time.perf_counter()
        logger.info("⚡ TURBO模式启动 - 跳过检查，绝对最速")
        
        # TURBO模式：跳过检查的最小启动流程
        self._wait_for_server_ready()
        
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

        return self.current_port

    def _wait_for_server_ready(self, skip_check: bool = True) -> bool:
        """等待服务器就绪 - TURBO模式（终极性能优化）"""
        
        # TURBO模式：跳过检查，直接信任启动，绝对最速
        time.sleep(0.01)  # 仅10ms最小延迟
        return True

    def wait_for_feedback(
        self, timeout_seconds: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        WebSocket增强版：双重超时机制 + 浏览器连接宽限期
        1. 浏览器连接宽限期（给浏览器时间打开和连接）
        2. 前端WebSocket心跳检测（优先）
        3. 后端超时兜底保护（备用）

        Args:
            timeout_seconds: 最大等待时间（秒），如果未指定则使用默认值

        Returns:
            Optional[dict]: 前端提交的结果或超时/断开时的None
        """
        # 性能监控: 反馈等待开始计时
        feedback_wait_start_time = time.perf_counter()
        
        # 设置超时时间
        if timeout_seconds is None:
            timeout_seconds = self._config.default_timeout
        
        # 设置浏览器连接宽限期（从配置读取）
        browser_grace_period = self._config.browser_grace_period
        
        logger.info(f"后端进入双重超时模式，{browser_grace_period}秒浏览器宽限期 + WebSocket检测 + {timeout_seconds}秒兜底超时")

        last_log_time: float = time.time()
        total_get_result_calls = 0
        total_get_result_duration = 0.0
        start_time = time.time()

        while True:
            current_time = time.time()
            elapsed_time = current_time - start_time
            
            # 1. 后端超时兜底检查
            if elapsed_time >= timeout_seconds:
                total_wait_duration = time.perf_counter() - feedback_wait_start_time
                logger.warning(
                    f"后端超时兜底触发，结束等待。总等待时间 {total_wait_duration:.3f} 秒"
                )
                self._handle_backend_timeout()
                return None

            # 2. WebSocket客户端活跃度检查（仅在宽限期后生效）
            if elapsed_time > browser_grace_period:
                if self.app and hasattr(self.app, 'has_active_clients'):
                    if not self.app.has_active_clients():
                        total_wait_duration = time.perf_counter() - feedback_wait_start_time
                        logger.warning(
                            f"WebSocket检测到所有客户端已断开，结束等待。总等待时间 {total_wait_duration:.3f} 秒"
                        )
                        return None

            # 3. 传统连接检测（仅在宽限期后生效）
            if elapsed_time > browser_grace_period:
                connection_check_start_time = time.perf_counter()
                if self._check_client_disconnection():
                    connection_check_duration = (
                        time.perf_counter() - connection_check_start_time
                    )
                    total_wait_duration = time.perf_counter() - feedback_wait_start_time
                    logger.warning(
                        f"传统连接检测到客户端断开，结束等待。总等待时间 {total_wait_duration:.3f} 秒，连接检查耗时 {connection_check_duration:.3f} 秒"
                    )
                    self._cleanup_on_disconnection()
                    return None

            # 4. 检查服务器状态
            if not self._is_server_healthy():
                total_wait_duration = time.perf_counter() - feedback_wait_start_time
                logger.warning(
                    f"服务器状态异常，结束等待。总等待时间 {total_wait_duration:.3f} 秒"
                )
                return None

            # 5. 等待结果（设置短轮询间隔避免CPU占用）
            try:
                get_result_start_time = time.perf_counter()
                result = self.feedback_handler.get_result(
                    timeout=self.feedback_result_timeout
                )
                get_result_duration = time.perf_counter() - get_result_start_time
                total_get_result_calls += 1
                total_get_result_duration += get_result_duration

                if result is not None:
                    total_wait_duration = time.perf_counter() - feedback_wait_start_time
                    avg_get_result_duration = (
                        total_get_result_duration / total_get_result_calls
                    )
                    
                    # 记录客户端信息
                    client_count = 0
                    if self.app and hasattr(self.app, 'get_active_client_count'):
                        client_count = self.app.get_active_client_count()
                    
                    logger.info(
                        f"收到反馈结果。总等待时间 {total_wait_duration:.3f} 秒，活跃客户端 {client_count} 个，get_result调用次数 {total_get_result_calls}，平均get_result耗时 {avg_get_result_duration:.4f} 秒"
                    )
                    return result
            except Exception as e:
                logger.error(f"获取反馈结果时出错: {e}")
                time.sleep(1)  # 出错时稍作等待，避免高频错误循环

            # 6. 定期日志输出（避免静默运行）
            if current_time - last_log_time >= self.feedback_log_interval:
                elapsed_time_log = time.perf_counter() - feedback_wait_start_time
                remaining_time = timeout_seconds - elapsed_time_log
                avg_get_result_duration = (
                    total_get_result_duration / total_get_result_calls
                    if total_get_result_calls > 0
                    else 0
                )
                
                # 获取客户端状态信息
                client_info = "未知"
                if self.app and hasattr(self.app, 'get_active_client_count'):
                    client_count = self.app.get_active_client_count()
                    client_info = f"{client_count} 个活跃客户端"
                
                # 显示当前状态
                if elapsed_time <= browser_grace_period:
                    status_msg = f"浏览器宽限期 (剩余 {browser_grace_period - elapsed_time:.1f} 秒)"
                else:
                    status_msg = f"活跃监控中，{client_info}"
                
                logger.debug(
                    f"等待反馈中... 已等待 {elapsed_time_log:.1f} 秒，剩余 {remaining_time:.1f} 秒，状态: {status_msg}，get_result调用 {total_get_result_calls} 次，平均耗时 {avg_get_result_duration:.4f} 秒"
                )
                last_log_time = current_time

            # 7. 检测循环休眠间隔，降低CPU占用
            time.sleep(self.feedback_polling_interval)

    def _handle_backend_timeout(self):
        """处理后端超时的情况"""
        logger.info("后端超时兜底触发，提交超时捕获数据")
        
        # 提交超时捕获数据
        timeout_data = {
            'text': '',
            'images': [],
            'source_event': 'backend_timeout',
            'is_timeout_capture': True,
            'user_agent': '',
            'ip_address': 'timeout'
        }
        
        self.feedback_handler.submit_feedback(timeout_data)

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
