#!/usr/bin/env python3
"""
测试120秒超时时间是否正确显示
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from mcp_feedback_pipe.server_manager import ServerManager
import time
import webbrowser

def test_120s_timeout():
    """测试120秒超时是否正确显示"""
    server_manager = ServerManager()
    
    try:
        # 启动服务器，设置120秒超时
        work_summary = """
# 测试120秒超时显示

我正在测试传入120秒超时时间是否能正确显示在前端界面。

**预期结果：**
- 前端应显示"2分钟"而不是"5分钟"
- 倒计时应从120秒开始倒数
- 进度条应基于120秒计算

**请验证：**
1. 页面顶部的超时信息是否正确显示"2分钟"
2. 倒计时是否从"2分钟"开始
3. 进度条是否基于120秒计算进度

如果显示正确，请在反馈中输入"显示正确"。
如果仍然显示300秒或5分钟，请报告具体看到的数值。
        """
        
        port = server_manager.start_server(
            work_summary=work_summary, 
            timeout_seconds=120,  # 明确设置120秒
            suggest=""
        )
        
        url = f"http://127.0.0.1:{port}"
        print(f"\n🚀 测试服务器已启动: {url}")
        print(f"⏰ 超时时间设置为: 120秒 (2分钟)")
        print(f"📋 请检查页面上显示的超时时间是否为2分钟")
        print(f"💡 如果是SSH环境，请配置端口转发：ssh -L {port}:127.0.0.1:{port} your_server")
        
        # 尝试自动打开浏览器（本地环境）
        try:
            webbrowser.open(url)
            print(f"🌐 已尝试自动打开浏览器")
        except:
            print(f"🌐 请手动打开浏览器访问: {url}")
        
        # 等待反馈
        print(f"\n等待用户反馈...")
        result = server_manager.wait_for_feedback(120)
        
        if result:
            print(f"\n✅ 收到反馈:")
            print(f"   文本: {result.get('text', '无')}")
            if result.get('images'):
                print(f"   图片数量: {len(result['images'])}")
            
            # 分析反馈内容
            feedback_text = result.get('text', '').lower()
            if '显示正确' in feedback_text or '2分钟' in feedback_text:
                print(f"\n🎉 测试通过！倒计时显示正确")
            elif '300' in feedback_text or '5分钟' in feedback_text:
                print(f"\n❌ 测试失败！仍然显示300秒/5分钟")
            else:
                print(f"\n⚠️ 反馈内容需要人工分析")
        else:
            print(f"\n⏰ 测试超时（120秒），未收到反馈")
            
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
    finally:
        # 清理
        try:
            server_manager.cleanup()
        except:
            pass

if __name__ == "__main__":
    test_120s_timeout() 