"""
请求验证模块
提供请求来源验证、数据安全性检查等功能
"""

import sys
from typing import Dict, Any, Optional
from flask import jsonify
from backend.security.csrf_handler import SecurityConfig
from backend.utils.logging_utils import log_message


def validate_request_origin_and_respond(flask_request) -> Optional[Any]:
    """
    验证请求来源并返回响应（如果验证失败）

    Args:
        flask_request: Flask请求对象

    Returns:
        Optional[Any]: 如果验证失败则返回错误响应，否则返回None
    """
    if not validate_request_origin(flask_request):
        return jsonify({"success": False, "message": "请求来源验证失败"}), 403
    return None


def validate_request_origin(flask_request) -> bool:
    """验证请求来源"""
    # 只允许本地请求
    remote_addr = flask_request.environ.get("REMOTE_ADDR", "")
    allowed_ips = ["127.0.0.1", "::1", "localhost"]

    # 检查X-Forwarded-For头（用于代理环境）
    forwarded_for = (
        flask_request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
    )
    if forwarded_for:
        remote_addr = forwarded_for

    return any(allowed_ip in remote_addr for allowed_ip in allowed_ips)


def validate_data_safety_and_respond(data: Dict[str, Any]) -> Optional[Any]:
    """
    验证数据安全性并返回响应（如果验证失败）

    Args:
        data: 要验证的数据

    Returns:
        Optional[Any]: 如果验证失败则返回错误响应，否则返回None
    """
    if not check_memory_safety(data):
        return jsonify({"success": False, "message": "数据大小超出限制"}), 413
    return None


def check_memory_safety(data: Dict[str, Any]) -> bool:
    """检查内存安全性"""
    try:
        # 使用sys.getsizeof进行精确内存计算
        total_size = sys.getsizeof(data)

        # 递归计算嵌套对象大小，添加递归深度限制防止栈溢出
        def get_deep_size(obj, seen=None, depth=0, max_depth=100):
            """
            递归计算对象深度大小

            Args:
                obj: 要计算大小的对象
                seen: 已访问对象的集合，用于避免循环引用
                depth: 当前递归深度
                max_depth: 最大允许的递归深度，默认100

            Returns:
                int: 对象的总大小（字节）
            """
            if seen is None:
                seen = set()

            # 递归深度限制检查
            if depth >= max_depth:
                log_message(
                    f"[WARNING] 递归深度达到限制 ({max_depth})，停止进一步递归以防止栈溢出"
                )
                return 0

            obj_id = id(obj)
            if obj_id in seen:
                return 0

            seen.add(obj_id)
            size = sys.getsizeof(obj)

            if isinstance(obj, dict):
                size += sum(
                    get_deep_size(k, seen, depth + 1, max_depth)
                    + get_deep_size(v, seen, depth + 1, max_depth)
                    for k, v in obj.items()
                )
            elif isinstance(obj, (list, tuple, set, frozenset)):
                size += sum(
                    get_deep_size(item, seen, depth + 1, max_depth) for item in obj
                )

            return size

        total_size = get_deep_size(data)
        return total_size <= SecurityConfig.MAX_MEMORY_PER_REQUEST

    except Exception as e:
        # 保留错误日志，因为这对调试很重要
        log_message(f"[ERROR] 内存检查失败: {e}")
        return False
