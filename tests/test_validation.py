#!/usr/bin/env python3
"""
测试验证脚本
快速验证项目结构和基本功能
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_imports():
    """测试模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        import mcp_feedback_pipe
        print("✅ mcp_feedback_pipe 导入成功")
        
        from mcp_feedback_pipe.server import collect_feedback, pick_image
        print("✅ server 模块导入成功")
        
        from mcp_feedback_pipe.app import FeedbackApp
        print("✅ app 模块导入成功")
        
        from mcp_feedback_pipe.feedback_handler import FeedbackHandler
        print("✅ feedback_handler 模块导入成功")
        
        from mcp_feedback_pipe.server_manager import ServerManager
        print("✅ server_manager 模块导入成功")
        
        from mcp_feedback_pipe.utils import get_image_info
        print("✅ utils 模块导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_file_structure():
    """测试文件结构"""
    print("🔍 测试文件结构...")
    
    base_path = Path(__file__).parent.parent
    required_files = [
        "src/mcp_feedback_pipe/__init__.py",
        "src/mcp_feedback_pipe/server.py",
        "src/mcp_feedback_pipe/app.py",
        "src/mcp_feedback_pipe/feedback_handler.py",
        "src/mcp_feedback_pipe/server_manager.py",
        "src/mcp_feedback_pipe/utils.py",
        "src/mcp_feedback_pipe/templates/feedback.html",
        "src/mcp_feedback_pipe/static/css/styles.css",
        "src/mcp_feedback_pipe/static/js/feedback.js",
        "tests/__init__.py",
        "tests/unit/__init__.py",
        "tests/integration/__init__.py",
        "tests/e2e/__init__.py",
        "requirements.txt",
        "pyproject.toml",
        "pytest.ini",
    ]
    
    missing_files = []
    for file_path in required_files:
        if not (base_path / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ 缺少文件: {', '.join(missing_files)}")
        return False
    else:
        print("✅ 所有必需文件都存在")
        return True

def test_line_count():
    """测试文件行数"""
    print("🔍 测试Python文件行数...")
    
    base_path = Path(__file__).parent.parent
    src_files = [
        "src/mcp_feedback_pipe/server.py",
        "src/mcp_feedback_pipe/app.py", 
        "src/mcp_feedback_pipe/feedback_handler.py",
        "src/mcp_feedback_pipe/server_manager.py",
        "src/mcp_feedback_pipe/utils.py",
    ]
    
    max_lines = 250
    oversized_files = []
    
    for file_path in src_files:
        full_path = base_path / file_path
        if full_path.exists():
            line_count = len(full_path.read_text().splitlines())
            print(f"  {file_path}: {line_count} 行")
            if line_count > max_lines:
                oversized_files.append((file_path, line_count))
    
    if oversized_files:
        print(f"❌ 超过{max_lines}行的文件:")
        for file_path, count in oversized_files:
            print(f"    {file_path}: {count} 行")
        return False
    else:
        print(f"✅ 所有Python文件都在{max_lines}行以内")
        return True

def test_dependencies():
    """测试依赖"""
    print("🔍 测试依赖安装...")
    
    required_packages = ['flask', 'pillow', 'mcp']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'pillow':
                import PIL
            elif package == 'flask':
                import flask
            elif package == 'mcp':
                import mcp
            print(f"✅ {package} 已安装")
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少依赖: {', '.join(missing_packages)}")
        return False
    else:
        print("✅ 所有依赖都已安装")
        return True

def main():
    """主函数"""
    print("🎯 MCP反馈通道 v3.0 验证测试")
    print("=" * 60)
    
    tests = [
        test_file_structure,
        test_dependencies,
        test_imports,
        test_line_count,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有验证测试通过！项目结构完整且符合要求。")
        return 0
    else:
        print("❌ 部分验证测试失败，请检查上述问题。")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 