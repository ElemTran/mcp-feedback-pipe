"""
反馈路由模块
包含所有反馈相关的路由定义
"""

import time
from typing import Optional, Any
from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
)
from backend.request_processing import (
    validate_request_origin_and_respond,
    validate_data_safety_and_respond,
    extract_feedback_data,
)
from backend.utils.logging_utils import log_message

# 创建蓝图
feedback_bp = Blueprint("feedback", __name__)

# 全局变量用于存储应用依赖
_feedback_handler = None
_csrf_protection = None
_work_summary = ""
_suggest_json = ""
_timeout_seconds = 300


def init_feedback_routes(
    feedback_handler,
    csrf_protection,
    work_summary="",
    suggest_json="",
    timeout_seconds=300,
):
    """
    初始化反馈路由的依赖

    Args:
        feedback_handler: 反馈处理器实例
        csrf_protection: CSRF保护实例
        work_summary: 工作摘要
        suggest_json: 建议JSON
        timeout_seconds: 超时秒数
    """
    global _feedback_handler, _csrf_protection, _work_summary, _suggest_json, _timeout_seconds
    _feedback_handler = feedback_handler
    _csrf_protection = csrf_protection
    _work_summary = work_summary
    _suggest_json = suggest_json
    _timeout_seconds = timeout_seconds


@feedback_bp.route("/")
def index():
    """主页面"""
    csrf_token = _csrf_protection.generate_token()
    return render_template(
        "feedback.html",
        work_summary=_work_summary,
        suggest_json=_suggest_json,
        timeout_seconds=_timeout_seconds,
        csrf_token=csrf_token,
    )


@feedback_bp.route("/submit_feedback", methods=["POST"])
def submit_feedback():
    """提交反馈数据"""
    try:
        # 验证请求来源
        origin_check_result = validate_request_origin_and_respond(request)
        if origin_check_result:
            return origin_check_result

        # 处理会话关闭通知
        session_close_result = _handle_session_close_notification(request)
        if session_close_result:
            return session_close_result

        # 处理反馈数据
        feedback_data = extract_feedback_data(request)

        # 验证数据安全性
        safety_check_result = validate_data_safety_and_respond(feedback_data)
        if safety_check_result:
            return safety_check_result

        # 提交反馈到处理队列
        _feedback_handler.submit_feedback(feedback_data)

        return jsonify({"success": True, "message": "反馈提交成功！感谢您的反馈。"})

    except Exception as e:
        return jsonify({"success": False, "message": f"提交失败: {str(e)}"}), 500


@feedback_bp.route("/ping")
def ping():
    """健康检查"""
    return jsonify({"status": "ok", "timestamp": time.time()})


def _handle_session_close_notification(flask_request) -> Optional[Any]:
    """
    处理会话关闭通知

    Args:
        flask_request: Flask请求对象

    Returns:
        Optional[Any]: 如果是会话关闭通知则返回响应，否则返回None
    """
    if not flask_request.is_json:
        return None

    json_data = flask_request.get_json()
    if not json_data or json_data.get("status") != "session_closed":
        return None

    log_message("[INFO] 收到窗口关闭通知，立即释放服务器资源")
    try:
        # 获取服务器池实例并立即释放资源
        from backend.server_pool import get_server_pool

        server_pool = get_server_pool()
        server_pool.release_server(immediate=True)
        log_message("[INFO] 服务器资源释放成功")
    except Exception as e:
        log_message(f"[ERROR] 释放服务器资源时出错: {e}")

    return jsonify({"success": True, "message": "窗口关闭处理完成"})
