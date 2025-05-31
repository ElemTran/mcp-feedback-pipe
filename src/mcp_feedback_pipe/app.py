"""
Flask Web应用 - 反馈收集界面
支持文字和图片反馈，完美适配SSH环境
"""

import os
import json
import threading
import time
import secrets
from typing import Dict, Any, Optional
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

# 安全配置
class SecurityConfig:
    """安全配置管理"""
    
    # CSRF保护
    CSRF_TOKEN_BYTES = 32
    CSRF_TOKEN_LIFETIME = 3600  # 1小时
    
    # 文件上传限制
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    
    # 内存限制
    MAX_MEMORY_PER_REQUEST = 50 * 1024 * 1024  # 50MB

class CSRFProtection:
    """简化的CSRF保护实现"""
    
    def __init__(self):
        self._tokens = {}
        self._lock = threading.Lock()
    
    def generate_token(self) -> str:
        """生成CSRF令牌"""
        token = secrets.token_urlsafe(SecurityConfig.CSRF_TOKEN_BYTES)
        with self._lock:
            self._tokens[token] = time.time()
            # 清理过期令牌
            current_time = time.time()
            expired_tokens = [
                t for t, timestamp in self._tokens.items()
                if current_time - timestamp > SecurityConfig.CSRF_TOKEN_LIFETIME
            ]
            for expired_token in expired_tokens:
                self._tokens.pop(expired_token, None)
        return token
    
    def validate_token(self, token: str) -> bool:
        """验证CSRF令牌"""
        if not token:
            return False
        
        with self._lock:
            if token not in self._tokens:
                return False
            
            # 检查令牌是否过期
            timestamp = self._tokens[token]
            if time.time() - timestamp > SecurityConfig.CSRF_TOKEN_LIFETIME:
                self._tokens.pop(token, None)
                return False
            
            # 一次性令牌，使用后删除
            self._tokens.pop(token, None)
            return True

class FeedbackApp:
    """反馈收集Flask应用"""
    
    def __init__(self, feedback_handler, work_summary: str = "", suggest_json: str = "", timeout_seconds: int = 300):
        self.feedback_handler = feedback_handler
        self.work_summary = work_summary
        self.suggest_json = suggest_json
        self.timeout_seconds = timeout_seconds
        self.csrf_protection = CSRFProtection()
        
    def create_app(self) -> Flask:
        """创建Flask应用实例"""
        app = Flask(__name__, 
                   template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                   static_folder=os.path.join(os.path.dirname(__file__), 'static'))
        
        # 安全配置
        app.config['SECRET_KEY'] = secrets.token_urlsafe(32)
        app.config['MAX_CONTENT_LENGTH'] = SecurityConfig.MAX_CONTENT_LENGTH
        
        # 注册路由
        self._register_routes(app)
        
        return app
    
    def run(self, host='127.0.0.1', port=5000, debug=False):
        """运行Flask应用"""
        app = self.create_app()
        app.run(host=host, port=port, debug=debug, threaded=True)
    
    def _register_routes(self, app: Flask):
        """注册所有路由"""
        
        @app.route('/')
        def index():
            """主页面"""
            csrf_token = self.csrf_protection.generate_token()
            return render_template('feedback.html', 
                                 work_summary=self.work_summary,
                                 suggest_json=self.suggest_json,
                                 timeout_seconds=self.timeout_seconds,
                                 csrf_token=csrf_token)
        
        @app.route('/submit_feedback', methods=['POST'])
        def submit_feedback():
            """提交反馈数据"""
            try:
                # 验证请求来源
                if not self._validate_request_origin(request):
                    return jsonify({
                        'success': False,
                        'message': '请求来源验证失败'
                    }), 403
                
                # 处理JSON数据
                if request.is_json:
                    feedback_data = self._process_json_feedback_data(request)
                else:
                    # 处理表单数据（保持向后兼容）
                    feedback_data = self._process_feedback_data(request)
                
                # 内存安全检查
                if not self._check_memory_safety(feedback_data):
                    return jsonify({
                        'success': False,
                        'message': '数据大小超出限制'
                    }), 413
                
                # 提交到队列
                self.feedback_handler.submit_feedback(feedback_data)
                
                return jsonify({
                    'success': True,
                    'message': '反馈提交成功！感谢您的反馈。'
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f'提交失败: {str(e)}'
                }), 500
        
        @app.route('/ping')
        def ping():
            """健康检查"""
            return jsonify({'status': 'ok', 'timestamp': time.time()})
        
        @app.route('/static/<path:filename>')
        def static_files(filename):
            """静态文件服务"""
            return send_from_directory(app.static_folder, filename)
    
    def _validate_request_origin(self, request) -> bool:
        """验证请求来源"""
        # 只允许本地请求
        remote_addr = request.environ.get('REMOTE_ADDR', '')
        allowed_ips = ['127.0.0.1', '::1', 'localhost']
        
        # 检查X-Forwarded-For头（用于代理环境）
        forwarded_for = request.headers.get('X-Forwarded-For', '').split(',')[0].strip()
        if forwarded_for:
            remote_addr = forwarded_for
        
        return any(allowed_ip in remote_addr for allowed_ip in allowed_ips)
    
    def _process_json_feedback_data(self, request) -> Dict[str, Any]:
        """处理JSON格式的反馈数据"""
        json_data = request.get_json()
        
        feedback_data = {
            'text': json_data.get('textFeedback', '').strip() if json_data.get('textFeedback') else '',
            'images': json_data.get('images', []),
            'timestamp': time.time(),
            'user_agent': request.headers.get('User-Agent', ''),
            'ip_address': request.environ.get('REMOTE_ADDR', 'unknown')
        }
        
        return feedback_data
    
    def _process_feedback_data(self, request) -> Dict[str, Any]:
        """处理反馈数据"""
        feedback_data = {
            'text': request.form.get('feedback', '').strip(),
            'images': [],
            'timestamp': time.time(),
            'user_agent': request.headers.get('User-Agent', ''),
            'ip_address': request.environ.get('REMOTE_ADDR', 'unknown')
        }
        
        # 处理图片文件
        if 'images' in request.files:
            files = request.files.getlist('images')
            for file in files:
                if file and file.filename:
                    # 安全文件名处理
                    filename = secure_filename(file.filename)
                    if self._is_allowed_file(filename):
                        try:
                            image_data = file.read()
                            # 验证图片格式
                            if self._validate_image_data(image_data):
                                import base64
                                feedback_data['images'].append({
                                    'filename': filename,
                                    'data': base64.b64encode(image_data).decode('utf-8'),
                                    'size': len(image_data)
                                })
                        except Exception as e:
                            print(f"处理图片 {filename} 时出错: {e}")
        
        return feedback_data
    
    def _is_allowed_file(self, filename: str) -> bool:
        """检查文件扩展名是否允许"""
        if not filename:
            return False
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in SecurityConfig.ALLOWED_EXTENSIONS
    
    def _validate_image_data(self, data: bytes) -> bool:
        """验证图片数据格式"""
        if not data:
            return False
        
        # 检查文件头魔数
        image_signatures = {
            b'\x89PNG\r\n\x1a\n': 'PNG',
            b'\xff\xd8\xff': 'JPEG',
            b'GIF87a': 'GIF87a',
            b'GIF89a': 'GIF89a',
            b'BM': 'BMP',
            b'RIFF': 'WEBP'  # 需要进一步检查WEBP格式
        }
        
        for signature, format_name in image_signatures.items():
            if data.startswith(signature):
                if format_name == 'WEBP':
                    # WEBP需要额外验证
                    return len(data) > 12 and data[8:12] == b'WEBP'
                return True
        
        return False
    
    def _check_memory_safety(self, data: Dict[str, Any]) -> bool:
        """检查内存安全性"""
        import sys
        
        try:
            # 使用sys.getsizeof进行精确内存计算
            total_size = sys.getsizeof(data)
            
            # 递归计算嵌套对象大小
            def get_deep_size(obj, seen=None):
                if seen is None:
                    seen = set()
                
                obj_id = id(obj)
                if obj_id in seen:
                    return 0
                
                seen.add(obj_id)
                size = sys.getsizeof(obj)
                
                if isinstance(obj, dict):
                    size += sum(get_deep_size(k, seen) + get_deep_size(v, seen) 
                               for k, v in obj.items())
                elif isinstance(obj, (list, tuple, set, frozenset)):
                    size += sum(get_deep_size(item, seen) for item in obj)
                
                return size
            
            total_size = get_deep_size(data)
            return total_size <= SecurityConfig.MAX_MEMORY_PER_REQUEST
            
        except Exception as e:
            print(f"内存检查失败: {e}")
            return False 