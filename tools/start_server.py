#!/usr/bin/env python3
"""
Flask Web 服务器启动脚本
注意：这是测试模式，正常使用应该通过 MCP 客户端调用 collect_feedback 工具
"""
import os
import sys

def main():
    print("🌐 启动 Flask Web 服务器...")
    print("注意：这是测试模式，正常使用请通过 MCP 客户端调用")
    print()
    
    try:
        from backend.server_manager import ServerManager
        
        # 创建服务器管理器
        server_manager = ServerManager()
        
        # 启动 Web 服务器
        work_summary = """
🔧 测试启动 Flask Web 服务器

这是一个临时的测试启动。正常情况下，这个 Web 界面应该通过 MCP 工具调用启动：
- 通过 MCP 客户端调用 collect_feedback() 工具
- 工具会自动启动临时的 Web 服务器
- 收集反馈后服务器会自动关闭

当前测试模式将保持服务器运行状态。
"""
        
        port = server_manager.start_server(
            work_summary=work_summary,
            timeout_seconds=3600,  # 1小时超时
            suggest="",
            debug=False,
            use_reloader=False
        )
        
        print(f"✅ Flask Web 服务器已启动！")
        print(f"📱 访问地址: http://127.0.0.1:{port}")
        print(f"🔧 SSH环境请配置端口转发：ssh -L {port}:127.0.0.1:{port} user@server")
        print(f"⏰ 服务器将运行 1 小时")
        print()
        print("💡 在浏览器中打开上述地址即可访问反馈界面")
        print("🛑 按 Ctrl+C 停止服务器")
        
        # 等待用户反馈或超时
        try:
            result = server_manager.wait_for_feedback(3600)
            if result:
                print(f"\n🎉 收到反馈！")
                print(f"📝 文字反馈: {'是' if result.get('has_text') else '否'}")
                print(f"🖼️ 图片反馈: {'是' if result.get('has_images') else '否'}")
            else:
                print(f"\n⏰ 服务器超时")
                
        except KeyboardInterrupt:
            print(f"\n🛑 用户手动停止服务器")
            
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
