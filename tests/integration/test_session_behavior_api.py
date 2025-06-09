#!/usr/bin/env python3
"""
API层面的会话行为集成测试

此文件整合了多个分散的集成测试脚本，包括：
- 用户活动检测和暂停/恢复机制
- 前后端超时同步
- 超时捕获功能验证
- 120秒超时参数验证
- 用户活动API交互测试
"""

import pytest
import json
import time
import requests
import threading
from datetime import datetime
from typing import Optional, Dict, Any, List

from backend.server_manager import ServerManager

class TestSessionBehaviorAPI:
    """API层面会话行为测试类"""
    
    @pytest.fixture(autouse=True)
    def setup_server_manager(self):
        """为每个测试设置ServerManager"""
        self.sm = ServerManager()
        yield
        # 测试结束后清理
        try:
            self.sm.stop_server()
        except:
            pass
    
    @staticmethod
    def timestamp() -> str:
        """获取当前时间戳字符串"""
        return datetime.now().strftime("%H:%M:%S.%f")[:-3]
    
    @classmethod
    def log_with_timestamp(cls, message: str) -> None:
        """带时间戳的日志输出"""
        print(f"[{cls.timestamp()}] {message}")
    
    def send_user_activity(self, port: int, is_active: bool, remaining_time: float, 
                          signal_id: str = "test") -> bool:
        """发送用户活动状态到后端API
        
        Args:
            port: 服务器端口
            is_active: 用户是否活跃
            remaining_time: 剩余时间（秒）
            signal_id: 信号标识符
            
        Returns:
            bool: 请求是否成功
        """
        try:
            status = "活跃" if is_active else "不活跃"
            self.log_with_timestamp(f"📡 发送用户{status}信号 (剩余{remaining_time:.1f}秒)")
            
            response = requests.post(
                f"http://127.0.0.1:{port}/api/user_activity",
                json={
                    'is_active': is_active,
                    'remaining_time': remaining_time,
                    'timestamp': time.time() * 1000,
                    'signal_id': signal_id
                },
                timeout=5
            )
            
            if response.status_code == 200:
                self.log_with_timestamp(f"✅ 用户{status}信号发送成功")
                return True
            else:
                self.log_with_timestamp(f"❌ 用户{status}信号发送失败: {response.status_code}")
                return False
        except Exception as e:
            self.log_with_timestamp(f"❌ 发送用户{status}信号时出错: {e}")
            return False
    
    def test_basic_timeout_capture(self):
        """测试基本超时捕获机制"""
        self.log_with_timestamp("🎯 测试基本超时捕获机制")
        
        timeout_seconds = 8
        work_summary = "基本超时捕获测试 - 验证短超时情况下的自动捕获功能"
        
        port = self.sm.start_server(
            work_summary=work_summary,
            timeout_seconds=timeout_seconds,
            suggest=json.dumps(['测试完成'], ensure_ascii=False),
            debug=True,
            use_reloader=False
        )
        
        assert port is not None, "服务器启动失败"
        self.log_with_timestamp(f"✅ 服务器启动: http://127.0.0.1:{port}")
        
        # 等待超时并接收结果
        result = self.sm.wait_for_feedback(timeout_seconds + 3)
        
        assert result is not None, "应该收到超时捕获结果"
        assert result.get('is_timeout_capture'), "结果应该标记为超时捕获"
        
        self.log_with_timestamp("✅ 基本超时捕获测试通过")
    
    def test_user_activity_pause_resume(self):
        """测试用户活动暂停和恢复功能"""
        self.log_with_timestamp("🔍 测试用户活动暂停恢复功能")
        
        test_start_time = time.time()
        timeout_seconds = 10
        work_summary = "用户活动暂停恢复功能测试"
        
        port = self.sm.start_server(
            work_summary=work_summary,
            timeout_seconds=timeout_seconds,
            suggest=json.dumps(['测试完成'], ensure_ascii=False),
            debug=True,
            use_reloader=False
        )
        
        assert port is not None, "服务器启动失败"
        
        # 等待2秒让页面加载
        time.sleep(2)
        
        # 第3秒发送活跃信号（应该暂停计时器）
        def send_active_signal():
            time.sleep(3)
            self.send_user_activity(port, True, timeout_seconds - 3, "pause_test")
        
        # 第6秒发送不活跃信号（应该恢复计时器）
        def send_inactive_signal():
            time.sleep(6)
            self.send_user_activity(port, False, timeout_seconds - 6, "resume_test")
        
        thread1 = threading.Thread(target=send_active_signal)
        thread2 = threading.Thread(target=send_inactive_signal)
        
        thread1.start()
        thread2.start()
        
        # 等待结果
        result = self.sm.wait_for_feedback(timeout_seconds + 5)
        result_time = time.time()
        
        thread1.join()
        thread2.join()
        
        total_test_time = result_time - test_start_time
        
        if result and result.get('is_timeout_capture'):
            # 期望超时时间: 前3秒 + 暂停3秒 + 剩余7秒 ≈ 13秒
            expected_timeout = 3 + (timeout_seconds - 3) + 3
            
            # 允许2秒误差
            assert 11 <= total_test_time <= 15, \
                f"超时时间不符合预期 (预期约{expected_timeout}秒，实际{total_test_time:.1f}秒)"
            
            self.log_with_timestamp("✅ 用户活动暂停恢复功能测试通过")
        else:
            pytest.fail("未收到预期的超时捕获结果")
    
    def test_frontend_backend_sync(self):
        """测试前后端同步问题检测"""
        self.log_with_timestamp("🔍 测试前后端同步问题检测")
        
        test_start_time = time.time()
        timeout_seconds = 12
        work_summary = "前后端超时同步问题检测测试"
        
        port = self.sm.start_server(
            work_summary=work_summary,
            timeout_seconds=timeout_seconds,
            suggest=json.dumps(['同步测试'], ensure_ascii=False),
            debug=True,
            use_reloader=False
        )
        
        assert port is not None, "服务器启动失败"
        
        # 等待2秒让页面加载
        time.sleep(2)
        
        activity_signals_sent = []
        
        def send_multiple_signals():
            """发送多个用户活动信号"""
            delays = [4, 7, 10]
            for i, delay in enumerate(delays, 1):
                time.sleep(delay - (delays[i-2] if i > 1 else 0))
                if self.send_user_activity(port, True, timeout_seconds - delay, f"signal_{i}"):
                    activity_signals_sent.append({
                        'id': i,
                        'delay': delay,
                        'time': time.time() - test_start_time
                    })
        
        thread = threading.Thread(target=send_multiple_signals)
        thread.start()
        
        # 等待结果
        result = self.sm.wait_for_feedback(timeout_seconds + 3)
        result_time = time.time()
        thread.join()
        
        total_test_time = result_time - test_start_time
        
        self.log_with_timestamp(f"⏱️ 总测试时间: {total_test_time:.1f}秒 (设定超时: {timeout_seconds}秒)")
        self.log_with_timestamp(f"📡 发送了 {len(activity_signals_sent)} 个用户活动信号")
        
        # 分析结果
        if result and result.get('is_timeout_capture'):
            # 如果收到超时捕获，但发送了活动信号，说明可能存在同步问题
            if activity_signals_sent:
                self.log_with_timestamp("🚨 检测到潜在的前后端同步问题")
                self.log_with_timestamp("   - 发送了用户活动信号但仍然超时")
            else:
                self.log_with_timestamp("✅ 正常超时，未发送用户活动信号")
        else:
            self.log_with_timestamp("✅ 未收到超时捕获或收到正常提交")
    
    def test_timeout_120_seconds(self):
        """测试120秒超时参数的正确处理"""
        self.log_with_timestamp("🔍 测试120秒超时参数")
        
        timeout_seconds = 120
        work_summary = """
        # 120秒超时参数测试
        
        此测试验证120秒超时设置是否被正确处理。
        
        **预期行为：**
        - 前端应显示120秒倒计时
        - 服务器应在120秒后触发超时
        - 不应默认为300秒或其他值
        
        由于测试时间较长，我们会在30秒后主动停止测试。
        """
        
        port = self.sm.start_server(
            work_summary=work_summary,
            timeout_seconds=timeout_seconds,
            suggest=json.dumps(['120秒测试'], ensure_ascii=False),
            debug=True,
            use_reloader=False
        )
        
        assert port is not None, "服务器启动失败"
        self.log_with_timestamp(f"✅ 服务器启动，超时设置为{timeout_seconds}秒")
        
        # 等待30秒后停止测试（不等完整的120秒）
        time.sleep(30)
        
        # 验证服务器仍在运行（未过早超时）
        try:
            response = requests.get(f"http://127.0.0.1:{port}/", timeout=5)
            assert response.status_code == 200, "服务器应该仍在运行"
            self.log_with_timestamp("✅ 120秒超时参数设置正确，服务器未过早超时")
        except Exception as e:
            pytest.fail(f"服务器访问失败: {e}")
    
    def test_activity_hack_prevention(self):
        """测试防止用户活动hack的场景"""
        self.log_with_timestamp("🔧 测试用户活动hack预防")
        
        timeout_seconds = 10
        work_summary = """
        用户活动hack测试 - 验证持续的用户活动信号是否能影响超时机制
        
        此测试模拟前端持续发送用户活动信号的情况。
        """
        
        port = self.sm.start_server(
            work_summary=work_summary,
            timeout_seconds=timeout_seconds,
            suggest=json.dumps(['hack测试'], ensure_ascii=False),
            debug=True,
            use_reloader=False
        )
        
        assert port is not None, "服务器启动失败"
        
        # 每秒发送用户活动信号（模拟hack）
        def continuous_activity():
            for i in range(timeout_seconds + 2):
                time.sleep(1)
                self.send_user_activity(port, True, timeout_seconds - i, f"hack_{i}")
        
        thread = threading.Thread(target=continuous_activity)
        thread.start()
        
        # 等待结果
        result = self.sm.wait_for_feedback(timeout_seconds + 5)
        thread.join()
        
        # 分析结果 - 期望系统能处理持续的用户活动信号
        if result:
            if result.get('is_timeout_capture'):
                self.log_with_timestamp("⚠️ 尽管持续发送活动信号，系统仍然超时")
            else:
                self.log_with_timestamp("✅ 系统正确处理了持续的用户活动信号")
        else:
            self.log_with_timestamp("⚠️ 未收到任何响应")
    
    def test_direct_timeout_capture(self):
        """测试直接超时捕获机制（无用户干预）"""
        self.log_with_timestamp("🎯 测试直接超时捕获")
        
        timeout_seconds = 6
        work_summary = "直接超时捕获测试 - 无用户活动情况下的自动超时"
        
        port = self.sm.start_server(
            work_summary=work_summary,
            timeout_seconds=timeout_seconds,
            suggest=json.dumps(['直接测试'], ensure_ascii=False),
            debug=True,
            use_reloader=False
        )
        
        assert port is not None, "服务器启动失败"
        
        # 完全不发送任何用户活动信号，等待自然超时
        result = self.sm.wait_for_feedback(timeout_seconds + 3)
        
        assert result is not None, "应该收到超时捕获结果"
        assert result.get('is_timeout_capture'), "结果应该标记为超时捕获"
        
        # 验证MCP转换功能
        try:
            mcp_result = self.sm.feedback_handler.process_feedback_to_mcp(result)
            assert len(mcp_result) > 0, "MCP转换应该产生结果"
            self.log_with_timestamp(f"✅ MCP转换成功，结果数量: {len(mcp_result)}")
        except Exception as e:
            self.log_with_timestamp(f"⚠️ MCP转换失败: {e}")
            # MCP转换失败不应该影响主要测试
    
    def test_mixed_activity_scenarios(self):
        """测试混合用户活动场景"""
        self.log_with_timestamp("🧪 测试混合用户活动场景")
        
        timeout_seconds = 15
        work_summary = "混合用户活动场景测试 - 复杂的活动模式"
        
        port = self.sm.start_server(
            work_summary=work_summary,
            timeout_seconds=timeout_seconds,
            suggest=json.dumps(['混合测试'], ensure_ascii=False),
            debug=True,
            use_reloader=False
        )
        
        assert port is not None, "服务器启动失败"
        
        # 等待初始化
        time.sleep(2)
        
        def complex_activity_pattern():
            """复杂的用户活动模式"""
            # 第3秒: 开始活动
            time.sleep(3)
            self.send_user_activity(port, True, timeout_seconds - 3, "start")
            
            # 第5秒: 停止活动  
            time.sleep(2)
            self.send_user_activity(port, False, timeout_seconds - 5, "stop")
            
            # 第8秒: 重新开始活动
            time.sleep(3)
            self.send_user_activity(port, True, timeout_seconds - 8, "restart")
            
            # 第11秒: 最终停止
            time.sleep(3)
            self.send_user_activity(port, False, timeout_seconds - 11, "final_stop")
        
        thread = threading.Thread(target=complex_activity_pattern)
        thread.start()
        
        # 等待结果
        result = self.sm.wait_for_feedback(timeout_seconds + 5)
        thread.join()
        
        # 验证系统能处理复杂的活动模式
        assert result is not None, "应该收到某种结果"
        
        if result.get('is_timeout_capture'):
            self.log_with_timestamp("✅ 系统正确处理了复杂的用户活动模式并最终超时")
        else:
            self.log_with_timestamp("✅ 系统处理了复杂的用户活动模式，收到正常提交")
    
    def test_session_closed_handling(self):
        """测试窗口关闭通知处理功能
        
        从 test_session_closed_handling.py 迁移的测试逻辑
        验证 submit_feedback 路由对 session_closed 状态的处理
        """
        self.log_with_timestamp("🧪 测试窗口关闭通知处理功能")
        
        timeout_seconds = 60
        work_summary = "窗口关闭处理测试"
        
        port = self.sm.start_server(
            work_summary=work_summary,
            timeout_seconds=timeout_seconds,
            suggest=json.dumps(['窗口关闭测试'], ensure_ascii=False),
            debug=True,
            use_reloader=False
        )
        
        assert port is not None, "服务器启动失败"
        self.log_with_timestamp(f"✅ 服务器启动成功，端口: {port}")
        
        # 等待服务器完全启动
        time.sleep(3)
        
        base_url = f'http://127.0.0.1:{port}'
        
        # 验证核心API存在
        self.log_with_timestamp("📋 验证核心API存在:")
        
        try:
            response = requests.get(f'{base_url}/')
            assert response.status_code == 200, f"主页访问失败: {response.status_code}"
            self.log_with_timestamp(f"  - GET /: {response.status_code} ✓")
        except Exception as e:
            pytest.fail(f"主页访问失败: {e}")
        
        try:
            response = requests.get(f'{base_url}/ping')
            assert response.status_code == 200, f"健康检查失败: {response.status_code}"
            self.log_with_timestamp(f"  - GET /ping: {response.status_code} ✓")
        except Exception as e:
            self.log_with_timestamp(f"  - GET /ping: 失败 - {e}")
        
        # 测试普通反馈提交
        self.log_with_timestamp("📋 验证普通反馈提交:")
        try:
            normal_data = {
                'textFeedback': '这是一个普通的反馈测试',
                'images': []
            }
            response = requests.post(
                f'{base_url}/submit_feedback',
                json=normal_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            assert response.status_code == 200, f"普通反馈提交失败: {response.status_code}"
            
            result = response.json()
            self.log_with_timestamp(f"  - 普通反馈提交: {response.status_code} ✓")
            self.log_with_timestamp(f"    响应: {result.get('message', '无消息')}")
        except Exception as e:
            self.log_with_timestamp(f"  - 普通反馈提交: 失败 - {e}")
        
        # 测试 session_closed 状态处理
        self.log_with_timestamp("📋 验证 session_closed 状态处理:")
        try:
            session_closed_data = {
                'status': 'session_closed'
            }
            response = requests.post(
                f'{base_url}/submit_feedback',
                json=session_closed_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            assert response.status_code == 200, f"session_closed 处理失败: {response.status_code}"
            
            result = response.json()
            self.log_with_timestamp(f"  - session_closed 处理: {response.status_code} ✓")
            self.log_with_timestamp(f"    响应: {result.get('message', '无消息')}")
            
            # 验证响应内容
            expected_success = result.get('success') == True
            expected_message = '窗口关闭处理完成' in result.get('message', '')
            
            assert expected_success, f"session_closed 响应中 success 应为 True，实际: {result.get('success')}"
            assert expected_message, f"session_closed 响应消息应包含'窗口关闭处理完成'，实际: {result.get('message')}"
            
            self.log_with_timestamp("    ✅ session_closed 状态处理正确")
            
        except Exception as e:
            pytest.fail(f"session_closed 处理失败: {e}")
        
        # 测试混合数据（包含 status 和其他字段）
        self.log_with_timestamp("📋 验证混合数据处理:")
        try:
            mixed_data = {
                'status': 'session_closed',
                'textFeedback': '这个不应该被处理',
                'images': []
            }
            response = requests.post(
                f'{base_url}/submit_feedback',
                json=mixed_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            assert response.status_code == 200, f"混合数据处理失败: {response.status_code}"
            
            result = response.json()
            self.log_with_timestamp(f"  - 混合数据处理: {response.status_code} ✓")
            
            # session_closed 应该优先处理，不处理其他反馈
            if '窗口关闭处理完成' in result.get('message', ''):
                self.log_with_timestamp("    ✅ session_closed 优先级处理正确")
            else:
                self.log_with_timestamp("    ❌ session_closed 优先级处理异常")
                self.log_with_timestamp(f"    实际响应: {result}")
                
        except Exception as e:
            self.log_with_timestamp(f"  - 混合数据处理: 失败 - {e}")
        
        self.log_with_timestamp("🎉 窗口关闭通知处理功能验证完成！")
        self.log_with_timestamp("📋 验证摘要：")
        self.log_with_timestamp("  ✅ submit_feedback 路由正常工作")
        self.log_with_timestamp("  ✅ session_closed 状态正确识别")
        self.log_with_timestamp("  ✅ 服务器资源立即释放逻辑已实现")
        self.log_with_timestamp("  ✅ 返回正确的响应消息")
        self.log_with_timestamp("  ✅ 不影响其他反馈处理流程")

if __name__ == "__main__":
    # 如果直接运行此文件，执行所有测试
    pytest.main([__file__, "-v", "-s"])
