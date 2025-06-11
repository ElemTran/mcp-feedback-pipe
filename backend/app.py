"""
Flask Web应用 - 反馈收集界面
支持文字和图片反馈，完美适配SSH环境
升级版：支持WebSocket实时通信和客户端活跃度检测
"""

import os
import secrets
import time
import threading
from typing import Dict, Any, Optional
from flask import Flask
from flask_socketio import SocketIO, emit
from backend.security.csrf_handler import CSRFProtection, SecurityConfig
from backend.routes.feedback_routes import feedback_bp, init_feedback_routes
from backend.utils.logging_utils import log_message
from backend.utils.static_cache import setup_static_cache_middleware


class FeedbackApp:
    """反馈收集Flask应用 - WebSocket增强版"""

    def __init__(
        self,
        feedback_handler,
        work_summary: str = "",
        suggest_json: str = "",
        timeout_seconds: int = 300,
        **kwargs,
    ):
        self.feedback_handler = feedback_handler
        self.work_summary = work_summary
        self.suggest_json = suggest_json
        self.timeout_seconds = timeout_seconds
        self.csrf_protection = CSRFProtection()
        
        # WebSocket相关属性
        self.socketio: Optional[SocketIO] = None
        self.active_clients: Dict[str, Dict[str, Any]] = {}
        self.heartbeat_interval = 30  # 30秒心跳间隔
        self.client_timeout = 60  # 60秒客户端超时
        self.cleanup_thread: Optional[threading.Thread] = None
        self.shutdown_flag = threading.Event()
        
        # 记录真正意外的参数（排除已知的可选参数）
        known_optional_params = {'server_manager_instance'}  # 已知但不使用的参数
        unexpected_kwargs = {k: v for k, v in kwargs.items() if k not in known_optional_params}
        
        if unexpected_kwargs:
            log_message(
                f"[DEBUG] FeedbackApp initialized with unexpected "
                f"keyword arguments: {list(unexpected_kwargs.keys())}"
            )

    def create_app(self) -> Flask:
        """创建Flask应用实例 - WebSocket增强版"""
        # 获取当前文件的绝对路径
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 计算项目根目录（从 backend/ 目录向上一级）
        project_root = os.path.abspath(os.path.join(current_file_dir, ".."))
        
        # 固定指向 frontend/ 目录下的资源，确保使用绝对路径
        template_folder = os.path.abspath(os.path.join(project_root, "frontend", "templates"))
        static_folder = os.path.abspath(os.path.join(project_root, "frontend", "static"))
        
        # 验证路径是否存在，并记录调试信息
        log_message(f"[DEBUG] Project root: {project_root}")
        log_message(f"[DEBUG] Template folder: {template_folder}")
        log_message(f"[DEBUG] Static folder: {static_folder}")
        log_message(f"[DEBUG] Template folder exists: {os.path.exists(template_folder)}")
        log_message(f"[DEBUG] Static folder exists: {os.path.exists(static_folder)}")
        
        # 检查关键模板文件是否存在
        feedback_template_path = os.path.join(template_folder, "feedback.html")
        log_message(f"[DEBUG] feedback.html path: {feedback_template_path}")
        log_message(f"[DEBUG] feedback.html exists: {os.path.exists(feedback_template_path)}")

        app = Flask(
            __name__,
            template_folder=template_folder,
            static_folder=static_folder,
        )

        # 安全配置
        app.config["SECRET_KEY"] = secrets.token_urlsafe(32)
        app.config["MAX_CONTENT_LENGTH"] = SecurityConfig.MAX_CONTENT_LENGTH
        
        # Flask URL构建相关配置 - 修复模板渲染中的URL构建问题
        app.config["SERVER_NAME"] = None  # 允许任意主机名
        app.config["APPLICATION_ROOT"] = "/"
        app.config["PREFERRED_URL_SCHEME"] = "http"

        # 初始化SocketIO
        self.socketio = SocketIO(
            app,
            cors_allowed_origins="*",
            async_mode='eventlet',
            logger=False,
            engineio_logger=False,
            ping_timeout=60,
            ping_interval=25
        )

        # 注册WebSocket事件处理器
        self._register_socketio_events()

        # 初始化路由依赖
        init_feedback_routes(
            self.feedback_handler,
            self.csrf_protection,
            self.work_summary,
            self.suggest_json,
            self.timeout_seconds,
        )

        # 注册蓝图
        app.register_blueprint(feedback_bp)

        # 设置静态文件缓存中间件
        setup_static_cache_middleware(app)

        return app

    def _register_socketio_events(self):
        """注册WebSocket事件处理器"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """客户端连接事件"""
            client_id = self._get_client_id()
            self.active_clients[client_id] = {
                'connect_time': time.time(),
                'last_heartbeat': time.time(),
                'session_id': None
            }
            log_message(f"[WebSocket] 客户端连接: {client_id}")
            
            # 发送连接确认
            emit('connection_established', {
                'client_id': client_id,
                'server_time': time.time(),
                'heartbeat_interval': self.heartbeat_interval
            })

        @self.socketio.on('disconnect')
        def handle_disconnect():
            """客户端断开事件"""
            client_id = self._get_client_id()
            if client_id in self.active_clients:
                del self.active_clients[client_id]
                log_message(f"[WebSocket] 客户端断开: {client_id}")

        @self.socketio.on('heartbeat')
        def handle_heartbeat(data):
            """心跳事件"""
            client_id = self._get_client_id()
            log_message(f"[WebSocket] 心跳接收: client_id={client_id}, 时间={time.strftime('%Y-%m-%d %H:%M:%S')}")
            if client_id in self.active_clients:
                self.active_clients[client_id]['last_heartbeat'] = time.time()
                log_message(f"[WebSocket] 更新 last_heartbeat: {client_id} -> {self.active_clients[client_id]['last_heartbeat']}")
                
                # 发送心跳响应
                emit('heartbeat_response', {
                    'client_id': client_id,
                    'server_time': time.time()
                })

        @self.socketio.on('submit_feedback')
        def handle_submit_feedback(data):
            """处理反馈提交"""
            client_id = self._get_client_id()
            log_message(f"[WebSocket] 收到反馈提交: {client_id}")
            
            # 更新客户端活跃时间
            if client_id in self.active_clients:
                self.active_clients[client_id]['last_heartbeat'] = time.time()
            
            # 处理反馈数据
            feedback_data = {
                'text': data.get('text', ''),
                'images': data.get('images', []),
                'source_event': 'websocket_submit',
                'is_timeout_capture': False,
                'user_agent': data.get('user_agent', ''),
                'ip_address': self._get_client_ip()
            }
            
            # 提交到反馈处理器
            self.feedback_handler.submit_feedback(feedback_data)
            
            # 发送确认
            emit('feedback_received', {
                'success': True,
                'message': '反馈已成功提交'
            })

    def _get_client_id(self) -> str:
        """获取客户端ID"""
        from flask import request
        return request.sid

    def _get_client_ip(self) -> str:
        """获取客户端IP"""
        from flask import request
        return request.environ.get('REMOTE_ADDR', 'unknown')

    def start_client_monitor(self):
        """启动客户端监控线程"""
        if self.cleanup_thread and self.cleanup_thread.is_alive():
            return
            
        self.cleanup_thread = threading.Thread(
            target=self._monitor_clients,
            daemon=True
        )
        self.cleanup_thread.start()
        log_message("[WebSocket] 客户端监控线程已启动")

    def _monitor_clients(self):
        """监控客户端活跃度 - 简化版本，仅负责清理不活跃连接"""
        log_message("[WebSocket] 客户端监控开始（简化版）")
        
        while not self.shutdown_flag.is_set():
            try:
                current_time = time.time()
                inactive_clients = []
                
                # 查找不活跃的客户端
                for client_id, client_info in self.active_clients.items():
                    last_heartbeat = client_info['last_heartbeat']
                    if current_time - last_heartbeat > self.client_timeout:
                        inactive_clients.append(client_id)
                
                # 清理不活跃的客户端
                for client_id in inactive_clients:
                    if client_id in self.active_clients:
                        del self.active_clients[client_id]
                        log_message(f"[WebSocket] 清理不活跃客户端: {client_id}")
                        
            except Exception as e:
                log_message(f"[WebSocket] 客户端监控错误: {e}")
            
            # 等待下一次检查
            self.shutdown_flag.wait(10)  # 每10秒检查一次


    def has_active_clients(self) -> bool:
        """检查是否有活跃客户端"""
        current_time = time.time()
        active = False
        for client_id, client_info in self.active_clients.items():
            diff = current_time - client_info['last_heartbeat']
            log_message(f"[WebSocket] has_active_clients check: client_id={client_id}, now={current_time}, last_heartbeat={client_info['last_heartbeat']}, timeout={self.client_timeout}, diff={diff}")
            if diff <= self.client_timeout:
                log_message(f"[WebSocket] has_active_clients -> True")
                active = True
                break
        if not active:
            log_message(f"[WebSocket] has_active_clients -> False")
        return active

    def get_active_client_count(self) -> int:
        """获取活跃客户端数量"""
        current_time = time.time()
        count = 0
        for client_info in self.active_clients.values():
            if current_time - client_info['last_heartbeat'] <= self.client_timeout:
                count += 1
        return count

    def run(self, host="127.0.0.1", port=5000, debug=False, **kwargs):
        """运行Flask应用 - WebSocket增强版"""
        # 检查是否已创建应用实例，如果没有则创建
        if not hasattr(self, '_flask_app') or self._flask_app is None:
            self._flask_app = self.create_app()
        
        # 启动客户端监控
        self.start_client_monitor()
        
        # 使用SocketIO运行应用
        self.socketio.run(
            self._flask_app,
            host=host,
            port=port,
            debug=debug,
            **kwargs
        )

    def stop(self):
        """停止应用和清理资源"""
        self.shutdown_flag.set()
        if self.cleanup_thread and self.cleanup_thread.is_alive():
            self.cleanup_thread.join(timeout=5)
        log_message("[WebSocket] 应用已停止")

    def _check_memory_safety(self, data: dict, max_depth: int = 100) -> bool:
        """
        检查数据的内存安全性，包括递归深度和大小限制
        
        Args:
            data: 要检查的数据
            max_depth: 最大递归深度限制
            
        Returns:
            bool: 数据是否安全
        """
        def get_deep_size(obj, seen=None, depth=0):
            """计算对象的深度大小，防止栈溢出"""
            if seen is None:
                seen = set()
            
            # 深度限制检查
            if depth > max_depth:
                raise ValueError(f"数据嵌套深度超过限制 ({max_depth})")
            
            # 循环引用检查
            obj_id = id(obj)
            if obj_id in seen:
                return 0
            seen.add(obj_id)
            
            size = 0
            
            try:
                if isinstance(obj, dict):
                    size += sum(get_deep_size(k, seen, depth + 1) + get_deep_size(v, seen, depth + 1)
                               for k, v in obj.items())
                elif isinstance(obj, (list, tuple, set)):
                    size += sum(get_deep_size(item, seen, depth + 1) for item in obj)
                elif isinstance(obj, str):
                    size += len(obj)
                elif isinstance(obj, bytes):
                    size += len(obj)
                else:
                    size += 1
            except Exception:
                # 如果在计算过程中出现异常，视为不安全
                return -1
            
            seen.remove(obj_id)
            return size
        
        try:
            # 检查数据大小（限制为50MB）
            total_size = get_deep_size(data)
            if total_size < 0:  # 计算出错
                return False
            if total_size > 50 * 1024 * 1024:  # 50MB limit
                return False
            return True
        except (ValueError, RecursionError):
            # 深度超限或其他错误
            return False
