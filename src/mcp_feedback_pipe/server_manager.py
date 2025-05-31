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
        # 创建应用实例 - 使用关键字参数确保正确传递
        self.app = FeedbackApp(
            feedback_handler=self.feedback_handler,
            work_summary=work_summary,
            suggest_json=suggest,
            timeout_seconds=timeout_seconds
        )
        self.current_port = self.find_free_port()
        
        # 启动服务器线程
        def run_server():
            try:
                self.app.run(host='127.0.0.1', port=self.current_port, debug=False)
            except Exception as e:
                print(f"服务器启动失败: {e}")
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        # 更健壮的服务器启动等待机制
        self._wait_for_server_ready()
        
        # 打开浏览器
        self._open_browser(work_summary, suggest)
        
        return self.current_port
    
    def _wait_for_server_ready(self, max_attempts: int = 10) -> bool:
        """等待服务器就绪"""
        try:
            import requests
        except ImportError:
            print("⚠️  requests模块不可用，跳过服务器就绪检查")
            time.sleep(2)  # 简单等待
            return True
            
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"http://127.0.0.1:{self.current_port}/ping", timeout=1)
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(0.5)
        
        print("⚠️  服务器启动验证超时，但继续执行")
        return False
    
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
        try:
            # 不再发送关闭请求，让Flask服务器自然结束
            # 因为服务器线程是daemon线程，会在主程序结束时自动清理
            
            # 清理资源
            self.feedback_handler.clear_queue()
            self.current_port = None
            self.app = None
            
        except Exception as e:
            print(f"服务器停止过程中出现错误: {e}")
            # 强制清理
            self.current_port = None
            self.app = None
    
    def get_server_info(self) -> dict:
        """获取服务器信息"""
        return {
            'port': self.current_port,
            'url': f"http://127.0.0.1:{self.current_port}" if self.current_port else None,
            'is_running': self.server_thread.is_alive() if self.server_thread else False
        } 