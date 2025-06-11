"""
反馈处理器模块
管理反馈数据队列和结果处理
"""

import base64
import logging
import queue
import threading
from typing import Dict, List, Optional
from datetime import datetime

from mcp.server.fastmcp.utilities.types import Image as MCPImage
from mcp.types import TextContent


class FeedbackHandler:
    """反馈数据处理器"""

    def __init__(self, max_queue_size: int = 100):
        # 添加队列大小限制防止内存泄漏
        self.result_queue = queue.Queue(maxsize=max_queue_size)
        self._lock = threading.Lock()
        self.max_queue_size = max_queue_size

    def put_result(self, result: Dict) -> None:
        """将结果放入队列"""
        with self._lock:
            self.result_queue.put(result)

    def submit_feedback(self, feedback_data: Dict) -> None:
        """提交反馈数据（用于Web表单）"""
        # 从传入的 feedback_data 字典中获取 is_timeout_capture 标记
        is_timeout_capture = feedback_data.get("is_timeout_capture", False)

        # 转换为标准格式
        result = {
            "success": True,
            "has_text": bool(feedback_data.get("text", "").strip()),
            "text_feedback": feedback_data.get("text", "").strip(),
            "has_images": len(feedback_data.get("images", [])) > 0,
            "images": feedback_data.get("images", []),
            "timestamp": datetime.now().isoformat(),
            "source_event": feedback_data.get("source_event"),  # 保存 source_event 标记
            "is_timeout_capture": is_timeout_capture,  # 添加 is_timeout_capture 标记
            "metadata": {
                "user_agent": feedback_data.get("user_agent", ""),
                "ip_address": feedback_data.get("ip_address", "unknown"),
            },
        }
        self.put_result(result)

    def get_result(self, timeout: int = 300) -> Optional[Dict]:
        """从队列获取结果"""
        logger = logging.getLogger(__name__)
        logger.debug("尝试从结果队列获取反馈数据...")
        try:
            result = self.result_queue.get(timeout=timeout)
            logger.debug("成功获取反馈数据")
            return result
        except queue.Empty:
            logger.warning("结果队列为空，未获取到反馈数据")
            return None

    def process_feedback_to_mcp(self, result: Dict) -> List:
        """将反馈结果转换为MCP格式"""
        # 检查 result 本身是否为 None
        if result is None:
            raise Exception("获取反馈失败")

        # 获取 is_timeout_capture 标记
        is_timeout_capture = result.get("is_timeout_capture", False)

        # 调整异常逻辑：只有在非超时捕获且不成功时才抛出异常
        if not is_timeout_capture and not result.get("success"):
            raise Exception(result.get("message", "用户取消了反馈提交"))

        feedback_items = []

        # 处理超时捕获的情况
        if is_timeout_capture:
            # 添加超时捕获说明
            timeout_notice = TextContent(
                type="text", text="⚠️ 注意：以下内容是在反馈会话超时时自动捕获的：\n---"
            )
            feedback_items.append(timeout_notice)

            # 检查是否有实际数据
            has_data = result.get("has_text") or result.get("has_images")

            if not has_data:
                # 如果没有捕获到数据，添加相应说明
                no_data_notice = TextContent(
                    type="text", text="--- (超时，未捕获到有效文本或图片)"
                )
                feedback_items.append(no_data_notice)

        # 解决方案：先添加图片反馈 (MCPImage with format='png')
        if result.get("has_images"):
            for i, img_data in enumerate(result["images"]):
                decoded_image_data = base64.b64decode(img_data["data"])
                feedback_items.append(
                    MCPImage(data=decoded_image_data, format="png")
                )  # Use format='png'

        # 解决方案：后添加文本反馈 (使用TextContent对象)
        if result.get("has_text"):
            formatted_text = (
                f"用户文字反馈：{result['text_feedback']}\n"
                f"提交时间：{result['timestamp']}"
            )
            feedback_items.append(TextContent(type="text", text=formatted_text))

        # 如果是超时捕获且有数据，添加结束标记
        if is_timeout_capture and (result.get("has_text") or result.get("has_images")):
            end_marker = TextContent(type="text", text="---")
            feedback_items.append(end_marker)

        return feedback_items

    def clear_queue(self) -> None:
        """清空队列"""
        with self._lock:
            while not self.result_queue.empty():
                try:
                    self.result_queue.get_nowait()
                except queue.Empty:
                    break
