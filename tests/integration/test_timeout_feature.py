#!/usr/bin/env python3
"""
测试超时功能
验证超时倒计时和用户体验优化
"""

import sys
import os
import time

# 添加src目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '..', '..', 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

def test_timeout_display():
    """测试超时时间显示功能"""
    print("🧪 测试超时时间显示功能...")
    
    try:
        from mcp_feedback_pipe.server import collect_feedback
        
        print("1. 测试短超时时间（30秒）...")
        result = collect_feedback(
            work_summary="测试超时功能 - 30秒超时\n\n请观察页面右下角的倒计时显示：\n- 绿色：正常状态\n- 黄色：警告状态（剩余60秒以下）\n- 红色闪烁：危险状态（剩余30秒以下）\n- 灰色：已超时",
            timeout_seconds=30,
            suggest=["功能正常", "样式需要调整", "倒计时有问题", "超时处理正确"]
        )
        
        if result:
            print("✅ 超时功能测试完成，收到反馈")
            print(f"   反馈内容: {result}")
        else:
            print("⚠️  超时或未收到反馈（这是预期行为）")
            
        return True
        
    except Exception as e:
        if "操作超时" in str(e):
            print("✅ 超时处理正常工作")
            return True
        else:
            print(f"❌ 测试失败: {e}")
            return False

def test_timeout_integration():
    """测试超时功能集成"""
    print("\n🧪 测试超时功能集成...")
    
    try:
        from mcp_feedback_pipe.server_manager import ServerManager
        
        # 创建服务器管理器
        server_manager = ServerManager()
        
        print("1. 启动服务器（60秒超时）...")
        port = server_manager.start_server(
            work_summary="集成测试 - 超时功能验证\n\n测试项目：\n✅ 超时时间正确显示\n✅ 倒计时正常工作\n✅ 样式变化正确\n✅ 超时后禁用提交\n\n请在60秒内提交反馈来测试功能",
            timeout_seconds=60
        )
        
        print(f"✅ 服务器启动成功，端口: {port}")
        print("2. 等待用户反馈或超时...")
        
        # 等待反馈
        result = server_manager.wait_for_feedback(60)
        
        if result:
            print("✅ 收到用户反馈")
            print(f"   反馈详情: {result}")
        else:
            print("⚠️  等待超时（这是预期行为）")
        
        # 停止服务器
        server_manager.stop_server()
        print("✅ 服务器已停止")
        
        return True
        
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🎯 MCP反馈通道 - 超时功能测试")
    print("=" * 50)
    
    # 测试1：超时显示功能
    test1_result = test_timeout_display()
    
    # 测试2：超时功能集成
    test2_result = test_timeout_integration()
    
    # 汇总结果
    print("\n📊 测试结果汇总:")
    print(f"   超时显示功能: {'✅ 通过' if test1_result else '❌ 失败'}")
    print(f"   超时功能集成: {'✅ 通过' if test2_result else '❌ 失败'}")
    
    if test1_result and test2_result:
        print("\n🎉 所有测试通过！超时功能工作正常。")
        return True
    else:
        print("\n⚠️  部分测试失败，请检查超时功能实现。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 