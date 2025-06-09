#!/usr/bin/env python3
"""
MCP反馈通道启动脚本
"""
import sys

try:
    from backend.server import main
    print("🚀 启动MCP反馈通道...")
    print("📱 Web界面将在 http://localhost:5000 启动")
    print("🔧 在SSH环境中，请使用端口转发：ssh -L 5000:localhost:5000 user@server")
    print("=" * 60)
    main()
except KeyboardInterrupt:
    print("\n👋 服务已停止")
except Exception as e:
    print(f"❌ 启动失败: {e}")
    sys.exit(1) 