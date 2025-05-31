"""
Flask Web应用模块
处理HTTP路由和静态文件服务
"""

import base64
import json
import logging
import threading
from pathlib import Path
from typing import TYPE_CHECKING

try:
    from flask import Flask, render_template, request, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

if TYPE_CHECKING:
    from flask import Flask

from .feedback_handler import FeedbackHandler
from .type_definitions import FeedbackResult, FeedbackRequest


class FeedbackApp:
    """反馈收集Web应用"""
    
    def __init__(self, feedback_handler: FeedbackHandler):
        if not FLASK_AVAILABLE:
            raise ImportError("Flask未安装，请运行: pip install flask")
            
        self.feedback_handler = feedback_handler
        self.logger = logging.getLogger('mcp_feedback_pipe.app')
        self.app = self._create_app()
    
    def _create_app(self):
        """创建Flask应用实例"""
        # 设置模板和静态文件路径
        template_dir = Path(__file__).parent / 'templates'
        static_dir = Path(__file__).parent / 'static'
        
        app = Flask(__name__, 
                   template_folder=str(template_dir),
                   static_folder=str(static_dir))
        
        self._register_routes(app)
        return app
    
    def _register_routes(self, app):
        """注册路由"""
        
        @app.route('/')
        def index():
            work_summary = request.args.get('work_summary', '')
            suggest = request.args.get('suggest', '')
            return render_template('feedback.html', work_summary=work_summary, suggest=suggest)
        
        @app.route('/submit_feedback', methods=['POST'])
        def submit_feedback():
            try:
                # 验证请求数据
                if not request.json:
                    return jsonify({'success': False, 'message': '无效的请求数据'}), 400
                
                data = request.json
                result = self._process_feedback_data(data)
                
                # 将结果传递给处理器
                self.feedback_handler.put_result(result)
                
                return jsonify({'success': True, 'message': '反馈提交成功'})
                
            except ValueError as e:
                # 数据验证错误
                return jsonify({'success': False, 'message': '数据格式错误'}), 400
            except Exception as e:
                # 记录详细错误但不暴露给客户端
                self.logger.error(f"反馈提交错误: {e}", exc_info=True)
                return jsonify({'success': False, 'message': '服务器内部错误'}), 500
        
        @app.route('/ping')
        def ping():
            return jsonify({'status': 'ok'})
        
        @app.route('/close', methods=['POST'])
        def close():
            # 增强安全性：只允许POST请求，并验证来源
            if request.method != 'POST':
                return jsonify({'success': False, 'message': '只允许POST请求'}), 405
            
            # 验证请求来源（简单的本地验证）
            if request.remote_addr not in ['127.0.0.1', '::1', 'localhost']:
                return jsonify({'success': False, 'message': '访问被拒绝'}), 403
            
            # 触发服务器关闭
            threading.Timer(1.0, self._shutdown_server).start()
            return jsonify({'success': True, 'message': '服务器正在关闭'})
    
    def _process_feedback_data(self, data: FeedbackRequest) -> FeedbackResult:
        """处理前端提交的反馈数据"""
        # 数据大小限制检查
        data_size = len(str(data))
        if data_size > 10 * 1024 * 1024:  # 10MB限制
            raise ValueError("数据包过大，请减少内容或图片数量")
        
        processed_images = []
        
        if data.get('images'):
            # 限制图片数量
            if len(data['images']) > 10:
                raise ValueError("图片数量过多，最多支持10张图片")
                
            for img_data in data['images']:
                try:
                    # 验证图片数据格式
                    if not img_data.get('data') or not img_data['data'].startswith('data:image/'):
                        raise ValueError("无效的图片数据格式")
                    
                    # 从data URL中提取base64数据
                    header, base64_data = img_data['data'].split(',', 1)
                    
                    # base64解码并验证大小
                    image_bytes = base64.b64decode(base64_data)
                    if len(image_bytes) > 5 * 1024 * 1024:  # 5MB图片限制
                        raise ValueError(f"图片 '{img_data.get('name', '未知')}' 过大，请压缩后重试")
                    
                    processed_images.append({
                        'data': image_bytes,
                        'source': img_data.get('source', '未知'),
                        'name': img_data.get('name', '未命名图片')
                    })
                    
                except (ValueError, TypeError) as e:
                    if "图片" in str(e):
                        raise  # 重新抛出我们的自定义错误
                    raise ValueError(f"图片数据处理失败: {img_data.get('name', '未知')}")
                except Exception as e:
                    raise ValueError(f"图片数据解码失败: {img_data.get('name', '未知')}")
        
        # 验证文本反馈长度
        text_feedback = data.get('textFeedback', '')
        if text_feedback and len(text_feedback) > 50000:  # 50KB文本限制
            raise ValueError("文本反馈过长，请适当缩减内容")
        
        return {
            'success': True,
            'text_feedback': text_feedback if text_feedback else None,
            'images': processed_images,
            'timestamp': data.get('timestamp'),
            'has_text': bool(text_feedback),
            'has_images': len(processed_images) > 0,
            'image_count': len(processed_images)
        }
    
    def _shutdown_server(self):
        """关闭Flask服务器"""
        try:
            # 尝试优雅关闭（仅在请求上下文中有效）
            func = request.environ.get('werkzeug.server.shutdown')
            if func is not None:
                func()
        except RuntimeError:
            # 在请求上下文外，使用系统退出
            import os
            os._exit(0)
    
    def run(self, host='127.0.0.1', port=5000, debug=False):
        """启动应用"""
        self.app.run(host=host, port=port, debug=debug, 
                    use_reloader=False, threaded=True) 