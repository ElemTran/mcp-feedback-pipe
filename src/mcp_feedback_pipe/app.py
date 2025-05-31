"""
Flask Web应用模块
处理HTTP路由和静态文件服务
"""

import base64
import json
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


class FeedbackApp:
    """反馈收集Web应用"""
    
    def __init__(self, feedback_handler: FeedbackHandler):
        if not FLASK_AVAILABLE:
            raise ImportError("Flask未安装，请运行: pip install flask")
            
        self.feedback_handler = feedback_handler
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
                data = request.json
                result = self._process_feedback_data(data)
                
                # 将结果传递给处理器
                self.feedback_handler.put_result(result)
                
                return jsonify({'success': True, 'message': '反馈提交成功'})
                
            except Exception as e:
                return jsonify({'success': False, 'message': str(e)}), 400
        
        @app.route('/ping')
        def ping():
            return jsonify({'status': 'ok'})
        
        @app.route('/close')
        def close():
            # 触发服务器关闭
            threading.Timer(1.0, self._shutdown_server).start()
            return jsonify({'success': True})
    
    def _process_feedback_data(self, data: dict) -> dict:
        """处理前端提交的反馈数据"""
        processed_images = []
        
        if data.get('images'):
            for img_data in data['images']:
                # 从data URL中提取base64数据
                if img_data['data'].startswith('data:image/'):
                    header, base64_data = img_data['data'].split(',', 1)
                    image_bytes = base64.b64decode(base64_data)
                    processed_images.append({
                        'data': image_bytes,
                        'source': img_data['source'],
                        'name': img_data['name']
                    })
        
        return {
            'success': True,
            'text_feedback': data.get('textFeedback'),
            'images': processed_images,
            'timestamp': data.get('timestamp'),
            'has_text': bool(data.get('textFeedback')),
            'has_images': len(processed_images) > 0,
            'image_count': len(processed_images)
        }
    
    def _shutdown_server(self):
        """关闭Flask服务器"""
        func = request.environ.get('werkzeug.server.shutdown')
        if func is not None:
            func()
    
    def run(self, host='127.0.0.1', port=5000, debug=False):
        """启动应用"""
        self.app.run(host=host, port=port, debug=debug, 
                    use_reloader=False, threaded=True) 