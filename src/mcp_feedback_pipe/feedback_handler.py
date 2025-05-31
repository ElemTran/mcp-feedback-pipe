"""
反馈处理器模块
管理反馈数据队列和结果处理
"""

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
        # 转换为标准格式
        result = {
            'success': True,
            'has_text': bool(feedback_data.get('text', '').strip()),
            'text_feedback': feedback_data.get('text', '').strip(),
            'has_images': len(feedback_data.get('images', [])) > 0,
            'images': feedback_data.get('images', []),
            'timestamp': datetime.now().isoformat(),
            'metadata': {
                'user_agent': feedback_data.get('user_agent', ''),
                'ip_address': feedback_data.get('ip_address', 'unknown')
            }
        }
        self.put_result(result)
    
    def get_result(self, timeout: int = 300) -> Optional[Dict]:
        """从队列获取结果"""
        try:
            return self.result_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def process_feedback_to_mcp(self, result: Dict) -> List:
        """将反馈结果转换为MCP格式"""
        if not result or not result.get('success'):
            raise Exception(result.get('message', '用户取消了反馈提交') if result else '获取反馈失败')
        
        feedback_items = []
        
        # 添加文字反馈
        if result.get('has_text'):
            feedback_items.append(TextContent(
                type="text", 
                text=f"用户文字反馈：{result['text_feedback']}\n提交时间：{result['timestamp']}"
            ))
            
        # 添加图片反馈
        if result.get('has_images'):
            for img_data in result['images']:
                feedback_items.append(MCPImage(data=img_data['data'], format='png'))
                
        return feedback_items
    
    def clear_queue(self) -> None:
        """清空队列"""
        with self._lock:
            while not self.result_queue.empty():
                try:
                    self.result_queue.get_nowait()
                except queue.Empty:
                    break 