"""
网络工具模块
处理端口管理和网络相关功能
"""

import logging
import socket
import time
from typing import Optional

# 配置模块级别的logger
logger = logging.getLogger(__name__)

# 端口查找相关常量
MAX_PORT_FIND_RETRIES: int = 5
PORT_RETRY_INTERVAL: float = 0.1
PORT_TEST_TIMEOUT: float = 0.1


def find_free_port(
    max_retries: Optional[int] = None,
    retry_interval: Optional[float] = None,
    test_timeout: Optional[float] = None,
    preferred_port: Optional[int] = None,
) -> int:
    """
    查找可用端口（带重试机制和可用性测试）

    Args:
        max_retries: 最大重试次数，默认使用 MAX_PORT_FIND_RETRIES
        retry_interval: 重试间隔，默认使用 PORT_RETRY_INTERVAL
        test_timeout: 测试超时时间，默认使用 PORT_TEST_TIMEOUT
        preferred_port: 首选端口号，如果可用则优先使用此端口

    Returns:
        int: 可用端口号

    Raises:
        RuntimeError: 如果无法找到可用端口
    """
    if max_retries is None:
        max_retries = MAX_PORT_FIND_RETRIES
    if retry_interval is None:
        retry_interval = PORT_RETRY_INTERVAL
    if test_timeout is None:
        test_timeout = PORT_TEST_TIMEOUT

    # 尝试使用首选端口
    if preferred_port is not None:
        logger.info(f"尝试使用首选端口: {preferred_port}")
        if _test_port_availability(preferred_port, test_timeout):
            logger.info(f"首选端口 {preferred_port} 可用。")
            return preferred_port
        else:
            logger.warning(
                f"首选端口 {preferred_port} 当前不可用或已被占用，将尝试动态查找其他端口..."
            )

    for attempt in range(max_retries):
        try:
            # 1. 获取候选端口
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("", 0))
                s.listen(1)
                port = s.getsockname()[1]

            # 2. 端口可用性测试 - 尝试短暂监听该端口
            if _test_port_availability(port, test_timeout):
                return port
            else:
                logger.warning(
                    f"端口 {port} 可用性测试失败，重试 (尝试 {attempt + 1}/{max_retries})"
                )
                time.sleep(retry_interval)  # 短暂等待后重试

        except (OSError, socket.error) as e:
            logger.warning(
                f"查找端口时出错，重试 (尝试 {attempt + 1}/{max_retries}): {e}"
            )
            time.sleep(retry_interval)  # 短暂等待后重试
        except Exception as e:
            logger.error(
                f"查找端口时出现未预期错误，重试 (尝试 {attempt + 1}/{max_retries}): {e}"
            )
            time.sleep(retry_interval)  # 短暂等待后重试

    # 所有重试都失败
    raise RuntimeError(f"无法找到可用端口，已重试 {max_retries} 次")


def _test_port_availability(port: int, timeout: Optional[float] = None) -> bool:
    """
    测试端口可用性

    Args:
        port: 要测试的端口号
        timeout: 测试超时时间，默认使用 PORT_TEST_TIMEOUT

    Returns:
        bool: 端口是否可用
    """
    if timeout is None:
        timeout = PORT_TEST_TIMEOUT

    try:
        # 尝试在指定端口上创建并绑定socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as test_socket:
            # 设置socket选项，允许端口重用
            test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            test_socket.bind(("", port))  # 绑定到所有接口，更通用
            test_socket.listen(1)

            # 短暂监听以确保端口真正可用
            test_socket.settimeout(timeout)

            return True

    except socket.error as e:
        # 端口不可用的常见错误码
        if e.errno in (10048, 98):  # Windows: WSAEADDRINUSE, Linux: EADDRINUSE
            return False
        # 其他 socket 错误也视为不可用，并记录警告
        logger.warning(f"测试端口 {port} 可用性时发生意外的 socket 错误: {e}")
        return False
    except Exception as e:  # 捕获具体的异常实例以便记录
        # 任何其他异常都视为不可用，并记录错误
        logger.error(f"测试端口 {port} 可用性时发生未预期错误: {e}")
        return False
