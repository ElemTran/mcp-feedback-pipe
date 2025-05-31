#!/usr/bin/env python3
"""
MCP反馈通道部署测试脚本
"""
import os
import sys
import subprocess
from pathlib import Path

# 添加src目录到Python路径
current_dir = Path(__file__).parent.parent.parent  # 回到项目根目录
src_dir = current_dir / 'src'
sys.path.insert(0, str(src_dir))

def test_imports():
    """测试模块导入"""
    print("📦 测试模块导入...")
    try:
        import mcp_feedback_pipe
        from mcp_feedback_pipe import server
        from mcp_feedback_pipe.app import FeedbackApp
        print("✅ 模块导入成功")
        return True
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_flask_app():
    """测试Flask应用"""
    print("🌐 测试Flask应用...")
    try:
        from mcp_feedback_pipe.app import FeedbackApp
        from mcp_feedback_pipe.feedback_handler import FeedbackHandler
        
        # 创建反馈处理器和应用实例
        handler = FeedbackHandler()
        feedback_app = FeedbackApp(handler)
        
        # 测试Flask应用
        with feedback_app.app.test_client() as client:
            response = client.get('/')
            print(f"✅ Flask应用测试成功，状态码: {response.status_code}")
            return True
    except Exception as e:
        print(f"❌ Flask应用测试失败: {e}")
        return False

def test_dependencies():
    """测试依赖包"""
    print("🔧 测试依赖包...")
    dependencies = ['flask', 'mcp', 'PIL']
    all_ok = True
    
    for dep in dependencies:
        try:
            if dep == 'PIL':
                import PIL
                print(f"✅ {dep} 已安装")
            else:
                __import__(dep)
                print(f"✅ {dep} 已安装")
        except ImportError:
            print(f"❌ {dep} 未安装")
            all_ok = False
    
    return all_ok

def check_port():
    """检查端口占用"""
    print("🔍 检查端口5000...")
    try:
        result = subprocess.run(['netstat', '-tulpn'], 
                              capture_output=True, text=True)
        if ':5000' in result.stdout:
            print("⚠️  端口5000已被占用")
            return False
        else:
            print("✅ 端口5000可用")
            return True
    except Exception as e:
        print(f"⚠️  无法检查端口: {e}")
        return True

def main():
    """主测试函数"""
    print("🚀 MCP反馈通道部署测试")
    print("=" * 50)
    
    # 测试导入
    if not test_imports():
        return False
    
    # 测试依赖
    if not test_dependencies():
        print("⚠️  请安装缺失的依赖: pip install -r requirements.txt")
        return False
    
    # 测试Flask应用
    if not test_flask_app():
        return False
    
    # 检查端口
    port_available = check_port()
    
    print("\n📋 部署建议:")
    print("1. 启动服务: python scripts/start_server.py")
    print("2. 本地访问: http://localhost:5000")
    print("3. SSH转发: ssh -L 5000:localhost:5000 user@server")
    
    if not port_available:
        print("4. 如端口被占用，请使用: export FLASK_PORT=8080")
    
    print("\n🎉 部署测试完成！")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 