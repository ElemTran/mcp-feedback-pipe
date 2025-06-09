"""
Flask Web应用 - 反馈收集界面
支持文字和图片反馈，完美适配SSH环境
"""

import os
import secrets
from flask import Flask
from backend.security.csrf_handler import CSRFProtection, SecurityConfig
from backend.routes.feedback_routes import feedback_bp, init_feedback_routes
from backend.utils.logging_utils import log_message
from backend.utils.static_cache import setup_static_cache_middleware


class FeedbackApp:
    """反馈收集Flask应用"""

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
        # Log unexpected arguments if any
        if kwargs:
            log_message(
                f"[DEBUG] FeedbackApp initialized with unexpected keyword arguments: {list(kwargs.keys())}"
            )  # Log only keys for brevity

    def create_app(self) -> Flask:
        """创建Flask应用实例"""
        # 计算项目根目录：从当前文件路径向上一级到达项目根目录
        current_file_dir = os.path.dirname(
            os.path.abspath(__file__)
        )  # 应该解析为 .../project_root/backend
        project_root = os.path.abspath(
            os.path.join(current_file_dir, "..")
        )  # 应该解析为 .../project_root/

        app = Flask(
            __name__,
            template_folder=os.path.join(project_root, "frontend", "templates"),
            static_folder=os.path.join(project_root, "frontend", "static"),
        )

        # 安全配置
        app.config["SECRET_KEY"] = secrets.token_urlsafe(32)
        app.config["MAX_CONTENT_LENGTH"] = SecurityConfig.MAX_CONTENT_LENGTH

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

    def run(self, host="127.0.0.1", port=5000, debug=False, **kwargs):
        """运行Flask应用"""
        app = self.create_app()
        # 将额外的关键字参数传递给 Flask app.run()
        app.run(host=host, port=port, debug=debug, threaded=True, **kwargs)
