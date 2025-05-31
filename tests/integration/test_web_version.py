#!/usr/bin/env python3
"""
测试MCP反馈通道Web版本 v3.0
演示重构后的模块化架构和SSH环境兼容性
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径 - 适配新的测试目录结构
project_root = Path(__file__).parent.parent.parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

def test_imports():
    """测试模块导入"""
    print("📦 测试模块导入...")
    
    try:
        from mcp_feedback_pipe.server_manager import ServerManager
        print("   ✅ ServerManager 模块")
    except ImportError as e:
        print(f"   ❌ ServerManager 导入失败: {e}")
        return False
    
    try:
        from mcp_feedback_pipe.app import FeedbackApp
        print("   ✅ FeedbackApp 模块")
    except ImportError as e:
        print(f"   ❌ FeedbackApp 导入失败: {e}")
        return False
    
    try:
        from mcp_feedback_pipe.feedback_handler import FeedbackHandler
        print("   ✅ FeedbackHandler 模块")
    except ImportError as e:
        print(f"   ❌ FeedbackHandler 导入失败: {e}")
        return False
    
    try:
        from mcp_feedback_pipe.utils import get_image_info
        print("   ✅ Utils 模块")
    except ImportError as e:
        print(f"   ❌ Utils 导入失败: {e}")
        return False
    
    try:
        from mcp_feedback_pipe import collect_feedback, pick_image
        print("   ✅ 主要工具函数")
    except ImportError as e:
        print(f"   ❌ 主要工具函数导入失败: {e}")
        return False
    
    return True

def test_web_interface():
    """测试Web界面功能"""
    print("\n🚀 启动Web界面测试")
    print("="*50)
    
    try:
        from mcp_feedback_pipe.server_manager import ServerManager
        
        # 创建服务器管理器
        server_manager = ServerManager()
        
        # 模拟AI工作汇报
        work_summary = """
📊 重构完成情况汇报：

✅ 成功重构代码架构，实现关注点分离
✅ 拆分为多个独立模块，每个文件<250行
✅ 删除冗余的tkinter相关代码
✅ 创建独立的HTML、CSS、JavaScript文件
✅ 实现模块化的Flask应用架构

🔧 新架构：
- server.py: MCP工具定义 (120行)
- app.py: Flask应用 (114行)  
- server_manager.py: 服务器管理 (82行)
- feedback_handler.py: 反馈处理 (62行)
- utils.py: 工具函数 (95行)
- HTML/CSS/JS: 前后端分离

🎯 代码更清晰、可维护性更强！
"""
        
        print("🌐 正在启动Web服务器...")
        port = server_manager.start_server(work_summary, timeout_seconds=120)
        
        print(f"✅ Web服务器已启动!")
        print(f"📱 访问地址: http://127.0.0.1:{port}")
        print(f"⏰ 等待用户反馈... (最多2分钟)")
        print("\n💡 测试功能:")
        print("  - 查看重构后的现代化界面")
        print("  - 测试文字反馈输入")  
        print("  - 测试图片上传功能")
        print("  - 验证拖拽和剪贴板粘贴")
        
        # 等待用户反馈
        try:
            result = server_manager.wait_for_feedback(120)
            
            if result:
                print("\n🎉 收到用户反馈!")
                print("="*50)
                print(f"📝 有文字反馈: {'是' if result['has_text'] else '否'}")
                print(f"🖼️ 有图片反馈: {'是' if result['has_images'] else '否'}")
                
                if result['has_text']:
                    print(f"\n💬 文字内容:")
                    print(f"   {result['text_feedback']}")
                    
                if result['has_images']:
                    print(f"\n📷 图片数量: {result['image_count']}张")
                    for i, img in enumerate(result['images'], 1):
                        print(f"   图片{i}: {img['source']} - {img['name']}")
                        
                print(f"\n⏰ 提交时间: {result['timestamp']}")
            else:
                print(f"\n⏰ 等待超时")
                
        except Exception as e:
            print(f"\n❌ 测试过程中发生错误: {e}")
            
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False
        
    return True

def test_ssh_compatibility():
    """测试SSH环境兼容性"""
    print("\n🔒 SSH环境兼容性检查")
    print("="*30)
    
    # 检查是否在SSH环境中
    ssh_indicators = [
        os.getenv('SSH_CLIENT'),
        os.getenv('SSH_CONNECTION'), 
        os.getenv('SSH_TTY')
    ]
    
    in_ssh = any(ssh_indicators)
    print(f"📡 检测到SSH环境: {'是' if in_ssh else '否'}")
    
    if in_ssh:
        print("💡 SSH环境使用建议:")
        print("   1. 使用端口转发访问Web界面")
        print("   2. ssh -L 5000:127.0.0.1:5000 user@server")
        print("   3. 然后在本地浏览器访问 http://127.0.0.1:5000")
    else:
        print("💻 本地环境，Web界面将自动在浏览器中打开")
    
    # 检查依赖
    print("\n📦 依赖检查:")
    try:
        import flask
        print(f"   ✅ Flask {flask.__version__}")
    except ImportError:
        print("   ❌ Flask 未安装")
        
    try:
        from PIL import Image
        print(f"   ✅ Pillow 可用")
    except ImportError:
        print("   ❌ Pillow 未安装")
        
    try:
        import webbrowser
        print("   ✅ webbrowser 模块可用")
    except ImportError:
        print("   ❌ webbrowser 模块不可用")

def check_file_structure():
    """检查重构后的文件结构"""
    print("\n📁 检查文件结构")
    print("="*25)
    
    base_path = project_root / "src" / "mcp_feedback_pipe"
    
    files_to_check = [
        "server.py",
        "app.py", 
        "server_manager.py",
        "feedback_handler.py",
        "utils.py",
        "templates/feedback.html",
        "static/css/styles.css",
        "static/js/feedback.js"
    ]
    
    for file_path in files_to_check:
        full_path = base_path / file_path
        if full_path.exists():
            if full_path.is_file():
                size = len(full_path.read_text().splitlines())
                print(f"   ✅ {file_path} ({size} 行)")
            else:
                print(f"   ✅ {file_path} (目录)")
        else:
            print(f"   ❌ {file_path} 缺失")

def main():
    """主测试函数"""
    print("🎯 MCP反馈通道 v3.0 重构版本测试")
    print("🏗️ 模块化架构 + 前后端分离 + SSH兼容")
    print()
    
    # 检查文件结构
    check_file_structure()
    
    # 测试模块导入
    if not test_imports():
        print("\n❌ 模块导入测试失败，请检查代码结构")
        return
    
    # 兼容性检查
    test_ssh_compatibility()
    
    # 询问是否进行Web界面测试
    print(f"\n{'='*50}")
    response = input("是否启动Web界面测试? (y/N): ").strip().lower()
    
    if response in ['y', 'yes', '是']:
        if test_web_interface():
            print("\n✅ 测试完成!")
        else:
            print("\n❌ 测试失败!")
    else:
        print("\n📋 测试跳过，依赖检查完成")
        
    print("\n🎉 重构完成！新架构特点:")
    print("  • 📦 模块化设计，关注点分离")
    print("  • 📏 每个Python文件 < 250行")
    print("  • 🗂️ 前后端文件分离")
    print("  • 🧹 删除冗余tkinter代码")
    print("  • 🔧 更好的可维护性和扩展性")

if __name__ == "__main__":
    main() 