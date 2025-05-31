"""
Web服务器管理模块
处理服务器启动、端口管理和浏览器操作
"""

import socket
import threading
import time
import webbrowser
from typing import Optional
from urllib.parse import quote

from .app import FeedbackApp
from .feedback_handler import FeedbackHandler


class ServerManager:
    """Web服务器管理器"""
    
    def __init__(self):
        self.feedback_handler = FeedbackHandler()
        self.app = None
        self.server_thread = None
        self.current_port = None
    
    def find_free_port(self) -> int:
        """查找可用端口"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port
    
    def start_server(self, work_summary: str = "", timeout_seconds: int = 300, suggest: str = "") -> int:
        """启动Web服务器"""
        # 创建应用实例
        self.app = FeedbackApp(self.feedback_handler)
        self.current_port = self.find_free_port()
        
        # 启动服务器线程
        def run_server():
            self.app.run(host='127.0.0.1', port=self.current_port, debug=False)
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        # 等待服务器启动
        time.sleep(1)
        
        # 打开浏览器
        self._open_browser(work_summary, suggest)
        
        return self.current_port
    
    def _open_browser(self, work_summary: str, suggest: str = "") -> None:
        """在浏览器中打开反馈页面"""
        try:
            encoded_summary = quote(work_summary)
            encoded_suggest = quote(suggest) if suggest else ""
            url = f"http://127.0.0.1:{self.current_port}/?work_summary={encoded_summary}"
            if encoded_suggest:
                url += f"&suggest={encoded_suggest}"
            webbrowser.open(url)
        except Exception as e:
            print(f"无法自动打开浏览器: {e}")
            print(f"请手动访问: http://127.0.0.1:{self.current_port}")
    
    def wait_for_feedback(self, timeout_seconds: int = 300) -> Optional[dict]:
        """等待用户反馈"""
        return self.feedback_handler.get_result(timeout_seconds)
    
    def stop_server(self) -> None:
        """停止服务器"""
        if self.server_thread and self.server_thread.is_alive():
            # 清理资源
            self.feedback_handler.clear_queue()
            self.current_port = None
    
    def get_server_info(self) -> dict:
        """获取服务器信息"""
        return {
            'port': self.current_port,
            'url': f"http://127.0.0.1:{self.current_port}" if self.current_port else None,
            'is_running': self.server_thread.is_alive() if self.server_thread else False
        } 