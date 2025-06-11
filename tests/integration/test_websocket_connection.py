#!/usr/bin/env python3
"""
WebSocket连接测试脚本
用于诊断MCP反馈收集工具的WebSocket连接问题

此脚本将：
1. 启动后端反馈服务器
2. 创建WebSocket客户端连接
3. 验证关键事件的收发
4. 测试心跳机制
5. 提供详细的诊断信息
"""

import time
import threading
import sys
import signal
from typing import Optional, Dict, Any
import json

# 导入后端组件
from backend.server_manager import ServerManager
from backend.config import get_server_config

# 使用python-socketio作为客户端（与flask-socketio兼容）
try:
    import socketio
    print("✅ python-socketio 库已加载")
except ImportError:
    print("❌ 缺少 python-socketio 依赖")
    print("请安装: pip install python-socketio[client]")
    sys.exit(1)


class WebSocketConnectionTester:
    """WebSocket连接测试器"""
    
    def __init__(self):
        self.server_manager: Optional[ServerManager] = None
        self.server_port: Optional[int] = None
        self.client: Optional[socketio.SimpleClient] = None
        self.connection_established = False
        self.heartbeat_received = False
        self.client_id: Optional[str] = None
        self.test_results: Dict[str, Any] = {
            'server_startup': False,
            'client_connection': False,
            'connection_established_event': False,
            'heartbeat_test': False,
            'cleanup': False
        }
        self.shutdown_requested = False
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """处理停止信号"""
        print(f"\n🛑 收到停止信号 ({signum})，正在清理...")
        self.shutdown_requested = True
        self._cleanup()
        sys.exit(0)
    
    def run_test(self) -> bool:
        """运行完整的WebSocket连接测试"""
        print("🚀 开始WebSocket连接测试")
        print("=" * 50)
        
        try:
            # 步骤1: 启动服务器
            if not self._start_server():
                return False
            
            # 步骤2: 建立WebSocket连接
            if not self._connect_websocket():
                return False
            
            # 步骤3: 测试心跳机制
            if not self._test_heartbeat():
                return False
            
            # 步骤4: 清理资源
            self._cleanup()
            
            print("\n✅ WebSocket连接测试完成")
            self._print_test_summary()
            return True
            
        except Exception as e:
            print(f"\n❌ 测试过程中发生异常: {e}")
            import traceback
            traceback.print_exc()
            self._cleanup()
            return False
    
    def _start_server(self) -> bool:
        """启动后端服务器"""
        print("📡 步骤1: 启动后端服务器...")
        
        try:
            self.server_manager = ServerManager()
            
            # 使用较短的超时时间进行测试
            self.server_port = self.server_manager.start_server(
                work_summary="WebSocket连接测试",
                timeout_seconds=120,  # 2分钟超时
                suggest="",
                debug=False,
                use_reloader=False
            )
            
            print(f"✅ 服务器已启动在端口: {self.server_port}")
            print(f"🌐 服务器地址: http://127.0.0.1:{self.server_port}")
            
            # 给服务器一些启动时间
            print("⏳ 等待服务器完全启动...")
            time.sleep(2)
            
            self.test_results['server_startup'] = True
            return True
            
        except Exception as e:
            print(f"❌ 服务器启动失败: {e}")
            return False
    
    def _connect_websocket(self) -> bool:
        """建立WebSocket连接并测试基本事件"""
        print("\n🔌 步骤2: 建立WebSocket连接...")
        
        try:
            # 创建SocketIO客户端
            self.client = socketio.SimpleClient(
                logger=False,
                engineio_logger=False
            )
            
            # 尝试连接
            server_url = f"http://127.0.0.1:{self.server_port}"
            print(f"🔗 正在连接到: {server_url}")
            
            # 设置连接超时
            self.client.connect(server_url, wait_timeout=10)
            
            # 检查连接状态
            if self.client.connected:
                print("✅ WebSocket连接已建立")
                self.test_results['client_connection'] = True
            else:
                print("❌ WebSocket连接失败")
                return False
            
            # 等待并监听connection_established事件
            print("⏳ 等待服务器发送 connection_established 事件...")
            timeout = 10
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                try:
                    # 尝试接收事件
                    event = self.client.receive(timeout=1)
                    if event:
                        event_name, event_data = event
                        print(f"📨 收到事件: {event_name}")
                        
                        if event_name == 'connection_established':
                            print(f"✅ 收到 connection_established 事件: {json.dumps(event_data, indent=2, ensure_ascii=False)}")
                            self.connection_established = True
                            self.client_id = event_data.get('client_id')
                            self.test_results['connection_established_event'] = True
                            break
                        elif event_name == 'connect':
                            print("📨 收到连接确认事件")
                            
                except Exception as recv_e:
                    # 接收超时是正常的，继续尝试
                    pass
            
            if not self.connection_established:
                print("⚠️ 未收到 connection_established 事件，但连接可能仍然正常")
                # 不将此视为致命错误，因为连接已建立
            
            print("✅ WebSocket连接测试完成")
            return True
            
        except Exception as e:
            print(f"❌ WebSocket连接失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _test_heartbeat(self) -> bool:
        """测试心跳机制"""
        print("\n💓 步骤3: 测试心跳机制...")
        
        if not self.client or not self.client.connected:
            print("❌ 无法测试心跳：WebSocket连接未建立")
            return False
        
        try:
            # 发送心跳
            heartbeat_data = {
                'client_id': self.client_id or 'test_client',
                'timestamp': time.time()
            }
            
            print(f"💓 发送心跳: {json.dumps(heartbeat_data, indent=2, ensure_ascii=False)}")
            self.client.emit('heartbeat', heartbeat_data)
            
            # 等待心跳响应
            print("⏳ 等待心跳响应...")
            timeout = 5
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                try:
                    # 尝试接收事件
                    event = self.client.receive(timeout=1)
                    if event:
                        event_name, event_data = event
                        print(f"📨 收到事件: {event_name}")
                        
                        if event_name == 'heartbeat_response':
                            print(f"💓 收到心跳响应: {json.dumps(event_data, indent=2, ensure_ascii=False)}")
                            self.heartbeat_received = True
                            self.test_results['heartbeat_test'] = True
                            break
                            
                except Exception as recv_e:
                    # 接收超时是正常的，继续尝试
                    pass
            
            if self.heartbeat_received:
                print("✅ 心跳机制测试成功")
                return True
            else:
                print("⚠️ 未收到心跳响应（但连接可能仍然正常）")
                return True  # 不将此视为致命错误
                
        except Exception as e:
            print(f"❌ 心跳测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _cleanup(self) -> bool:
        """清理资源"""
        print("\n🧹 步骤4: 清理资源...")
        
        try:
            # 断开WebSocket连接
            if self.client and self.client.connected:
                print("🔌 断开WebSocket连接...")
                self.client.disconnect()
            
            # 停止服务器
            if self.server_manager:
                print("🛑 停止后端服务器...")
                self.server_manager.stop_server()
            
            print("✅ 资源清理完成")
            self.test_results['cleanup'] = True
            return True
            
        except Exception as e:
            print(f"⚠️ 清理过程中出现错误: {e}")
            return False
    
    def _print_test_summary(self):
        """打印测试结果摘要"""
        print("\n" + "=" * 50)
        print("📊 测试结果摘要")
        print("=" * 50)
        
        for test_name, result in self.test_results.items():
            status = "✅ 通过" if result else "❌ 失败"
            test_display_name = {
                'server_startup': '服务器启动',
                'client_connection': 'WebSocket连接',
                'connection_established_event': 'connection_established事件',
                'heartbeat_test': '心跳机制测试',
                'cleanup': '资源清理'
            }.get(test_name, test_name)
            
            print(f"  {test_display_name}: {status}")
        
        # 计算总体结果
        passed_tests = sum(1 for result in self.test_results.values() if result)
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"\n📈 通过率: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("🎉 WebSocket连接基本正常")
        elif success_rate >= 60:
            print("⚠️ WebSocket连接存在问题，但部分功能正常")
        else:
            print("💥 WebSocket连接存在严重问题")
        
        # 提供诊断建议
        print("\n💡 诊断建议:")
        if not self.test_results['server_startup']:
            print("  - 检查后端依赖是否完整安装")
            print("  - 检查端口是否被占用")
        
        if not self.test_results['client_connection']:
            print("  - 检查网络连接")
            print("  - 检查防火墙设置")
        
        if not self.test_results['connection_established_event']:
            print("  - 检查WebSocket事件处理逻辑")
            print("  - 检查服务器启动是否完整")
            print("  - connection_established事件可能由于时序问题未收到")
        
        if not self.test_results['heartbeat_test']:
            print("  - 心跳机制可能存在问题，但不影响基本功能")
        
        # 添加额外的调试信息
        print("\n🔍 详细诊断信息:")
        print(f"  - 服务器端口: {self.server_port}")
        print(f"  - 客户端ID: {self.client_id}")
        print(f"  - WebSocket连接状态: {'已连接' if self.client and self.client.connected else '未连接'}")


def main():
    """主函数"""
    print("🔧 WebSocket连接诊断工具")
    print("用于测试MCP反馈收集工具的WebSocket连接")
    print("=" * 50)
    
    # 检查依赖
    try:
        from backend.server_manager import ServerManager
        print("✅ 后端模块导入成功")
    except ImportError as e:
        print(f"❌ 后端模块导入失败: {e}")
        print("请确保在项目根目录下运行此脚本")
        return 1
    
    # 运行测试
    tester = WebSocketConnectionTester()
    success = tester.run_test()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)