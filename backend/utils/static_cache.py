"""
静态资源缓存工具模块
实现静态文件的HTTP缓存机制，包括ETag、Cache-Control等响应头设置
"""

import os
import hashlib
from typing import Optional
from flask import Response, request
from backend.config import get_web_config
from backend.utils.logging_utils import log_message


class StaticCacheHandler:
    """静态文件缓存处理器"""

    def __init__(self):
        self.config = get_web_config()
        self._file_cache = {}  # 文件ETag缓存

    def is_static_file(self, file_path: str) -> bool:
        """判断是否为静态文件"""
        if not self.config.enable_static_cache:
            return False

        _, ext = os.path.splitext(file_path.lower())
        return ext in self.config.static_file_extensions

    def generate_etag(self, file_path: str) -> Optional[str]:
        """生成文件的ETag"""
        try:
            if not os.path.exists(file_path):
                return None

            # 检查缓存
            if file_path in self._file_cache:
                cached_mtime, cached_etag = self._file_cache[file_path]
                current_mtime = os.path.getmtime(file_path)
                if cached_mtime == current_mtime:
                    return cached_etag

            # 生成新的ETag
            stat = os.stat(file_path)
            etag_data = f"{stat.st_mtime}-{stat.st_size}"
            etag = hashlib.md5(etag_data.encode("utf-8")).hexdigest()

            # 缓存ETag
            self._file_cache[file_path] = (stat.st_mtime, etag)

            return etag

        except Exception as e:
            log_message(f"[WARNING] 生成ETag失败: {file_path}, 错误: {e}")
            return None

    def check_if_modified(self, file_path: str) -> bool:
        """检查文件是否已修改（基于If-None-Match头）"""
        if not self.config.enable_etag:
            return True

        etag = self.generate_etag(file_path)
        if not etag:
            return True

        # 检查If-None-Match头
        if_none_match = request.headers.get("If-None-Match")
        if if_none_match:
            # 移除弱验证标识符（W/）和引号
            client_etags = [
                tag.strip().strip('"').lstrip("W/") for tag in if_none_match.split(",")
            ]
            if etag in client_etags or "*" in client_etags:
                return False

        return True

    def apply_cache_headers(self, response: Response, file_path: str) -> Response:
        """为响应添加缓存相关的HTTP头"""
        if not self.is_static_file(file_path):
            return response

        try:
            # 设置Cache-Control头
            response.headers["Cache-Control"] = self.config.static_cache_control

            # 设置ETag头
            if self.config.enable_etag:
                etag = self.generate_etag(file_path)
                if etag:
                    response.headers["ETag"] = f'"{etag}"'

            # 设置Expires头（备用）
            if self.config.static_cache_timeout > 0:
                import datetime

                expires = datetime.datetime.now(
                    datetime.timezone.utc
                ) + datetime.timedelta(seconds=self.config.static_cache_timeout)
                response.headers["Expires"] = expires.strftime(
                    "%a, %d %b %Y %H:%M:%S GMT"
                )

            # 设置Last-Modified头
            if os.path.exists(file_path):
                import datetime

                mtime = os.path.getmtime(file_path)
                last_modified = datetime.datetime.fromtimestamp(
                    mtime, datetime.timezone.utc
                )
                response.headers["Last-Modified"] = last_modified.strftime(
                    "%a, %d %b %Y %H:%M:%S GMT"
                )

            # 设置Vary头，用于内容协商
            response.headers["Vary"] = "Accept-Encoding"

            log_message(f"[DEBUG] 已为静态文件应用缓存头: {file_path}")

        except Exception as e:
            log_message(f"[WARNING] 应用缓存头失败: {file_path}, 错误: {e}")

        return response

    def create_304_response(self) -> Response:
        """创建304 Not Modified响应"""
        response = Response(status=304)
        response.headers["Cache-Control"] = self.config.static_cache_control
        return response


def setup_static_cache_middleware(app):
    """为Flask应用设置静态文件缓存中间件"""
    cache_handler = StaticCacheHandler()

    @app.after_request
    def add_cache_headers(response):
        """为静态文件响应添加缓存头"""
        try:
            # 只处理静态文件请求
            if request.endpoint == "static":
                # 获取请求的文件路径
                filename = request.view_args.get("filename", "")
                static_folder = app.static_folder
                if static_folder and filename:
                    file_path = os.path.join(static_folder, filename)
                    file_path = os.path.normpath(file_path)

                    # 安全检查：确保文件路径在静态文件夹内
                    if file_path.startswith(os.path.normpath(static_folder)):
                        response = cache_handler.apply_cache_headers(
                            response, file_path
                        )

        except Exception as e:
            log_message(f"[WARNING] 静态文件缓存中间件处理失败: {e}")

        return response

    # 添加静态文件304响应处理
    @app.before_request
    def check_static_file_modified():
        """检查静态文件是否已修改，如未修改则返回304"""
        try:
            if request.endpoint == "static":
                filename = (
                    request.view_args.get("filename", "") if request.view_args else ""
                )
                static_folder = app.static_folder
                if static_folder and filename:
                    file_path = os.path.join(static_folder, filename)
                    file_path = os.path.normpath(file_path)

                    # 安全检查：确保文件路径在静态文件夹内
                    if file_path.startswith(os.path.normpath(static_folder)):
                        if not cache_handler.check_if_modified(file_path):
                            log_message(f"[DEBUG] 返回304响应: {filename}")
                            return cache_handler.create_304_response()

        except Exception as e:
            log_message(f"[WARNING] 静态文件304检查失败: {e}")

        return None


def get_static_cache_handler() -> StaticCacheHandler:
    """获取静态缓存处理器实例"""
    return StaticCacheHandler()
