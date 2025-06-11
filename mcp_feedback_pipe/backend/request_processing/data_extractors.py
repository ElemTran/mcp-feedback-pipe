"""
数据提取模块
提供反馈数据提取和处理功能
"""

import base64
import time
from typing import Dict, Any, List
from werkzeug.utils import secure_filename
from backend.utils.image_utils import is_allowed_file, validate_image_data
from backend.utils.logging_utils import log_message


def extract_feedback_data(flask_request) -> Dict[str, Any]:
    """
    根据请求类型提取反馈数据

    Args:
        flask_request: Flask请求对象

    Returns:
        Dict[str, Any]: 提取的反馈数据
    """
    if flask_request.is_json:
        return process_json_feedback_data(flask_request)
    else:
        # 处理表单数据（保持向后兼容）
        return process_feedback_data(flask_request)


def create_base_feedback_data(flask_request) -> Dict[str, Any]:
    """
    创建基础反馈数据结构，包含通用字段

    Args:
        flask_request: Flask请求对象

    Returns:
        Dict[str, Any]: 包含通用字段的基础反馈数据
    """
    return {
        "text": "",
        "images": [],
        "timestamp": time.time(),
        "user_agent": flask_request.headers.get("User-Agent", ""),
        "ip_address": flask_request.environ.get("REMOTE_ADDR", "unknown"),
    }


def process_json_feedback_data(flask_request) -> Dict[str, Any]:
    """处理JSON格式的反馈数据"""
    json_data = flask_request.get_json()
    feedback_data = create_base_feedback_data(flask_request)

    # 处理JSON特定字段
    feedback_data["text"] = (
        json_data.get("textFeedback", "").strip()
        if json_data.get("textFeedback")
        else ""
    )
    feedback_data["images"] = json_data.get("images", [])

    return feedback_data


def process_form_images(flask_request) -> List[Dict[str, Any]]:
    """
    处理表单上传的图片文件

    Args:
        flask_request: Flask请求对象

    Returns:
        List[Dict[str, Any]]: 处理后的图片数据列表
    """
    images = []

    if "images" not in flask_request.files:
        return images

    files = flask_request.files.getlist("images")
    for file in files:
        if not file or not file.filename:
            continue

        # 安全文件名处理
        filename = secure_filename(file.filename)
        if not is_allowed_file(filename):
            continue

        try:
            image_data = file.read()
            # 验证图片格式
            if validate_image_data(image_data):
                images.append(
                    {
                        "filename": filename,
                        "data": base64.b64encode(image_data).decode("utf-8"),
                        "size": len(image_data),
                    }
                )
        except Exception as e:
            # 保留错误日志，因为这对调试很重要
            log_message(
                f"[ERROR] Error processing image {secure_filename(file.filename if file else 'Unknown_File')}: {e}"
            )

    return images


def process_feedback_data(flask_request) -> Dict[str, Any]:
    """处理表单格式的反馈数据"""
    feedback_data = create_base_feedback_data(flask_request)

    # 处理表单特定字段
    feedback_data["text"] = flask_request.form.get("textFeedback", "").strip()
    feedback_data["images"] = process_form_images(flask_request)
    feedback_data["is_timeout_capture"] = (
        flask_request.form.get("is_timeout_capture", "false").lower() == "true"
    )
    feedback_data["source_event"] = flask_request.form.get("source_event", "")

    return feedback_data
