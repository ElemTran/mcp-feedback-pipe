#!/usr/bin/env python3
"""
纯后端超时测试：验证ServerManager的用户活动暂停功能
不依赖前端，直接测试后端逻辑
"""
import sys
import os
import time
import threading
from datetime import datetime

from backend.server_manager import ServerManager

def timestamp():
    """获取当前时间戳字符串"""
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]

def log_with_timestamp(message):
    """带时间戳的日志输出"""
    print(f"[{timestamp()}] {message}")

def test_backend_user_activity_logic():
    """
    纯后端测试：验证用户活动暂停恢复逻辑
    """
    log_with_timestamp("🔍 测试后端用户活动暂停恢复逻辑（纯后端）")
    print("=" * 60)
    
    test_start_time = time.time()
    timeout_seconds = 6  # 短超时用于快速测试
    
    # 创建ServerManager但不启动Web服务器
    sm = ServerManager()
    
    log_with_timestamp(f"开始后端超时测试（超时: {timeout_seconds}秒）...")
    
    def send_activity_signals():
        """在独立线程中发送用户活动信号"""
        time.sleep(2)  # 第2秒发送活跃信号
        elapsed = time.time() - test_start_time
        log_with_timestamp(f"📡 发送用户活跃信号 (第{elapsed:.1f}秒)")
        sm.update_user_activity_status(True, timeout_seconds - 2)
        
        time.sleep(3)  # 第5秒发送不活跃信号
        elapsed = time.time() - test_start_time
        log_with_timestamp(f"📡 发送用户不活跃信号 (第{elapsed:.1f}秒)")
        sm.update_user_activity_status(False, timeout_seconds - 5)
    
    # 启动活动信号线程
    activity_thread = threading.Thread(target=send_activity_signals)
    activity_thread.start()
    
    log_with_timestamp(f"⏰ 开始等待最多 {timeout_seconds} 秒...")
    
    # 开始等待（这里不会有前端干扰）
    result_wait_start = time.time()
    result = sm.wait_for_feedback(timeout_seconds)  # 使用原始超时时间
    result_received_time = time.time()
    
    # 等待线程完成
    activity_thread.join()
    
    total_test_time = result_received_time - test_start_time
    
    print("\n" + "=" * 50)
    log_with_timestamp("🔍 纯后端测试结果分析")
    print("=" * 50)
    
    log_with_timestamp(f"⏱️  总测试时间: {total_test_time:.1f}秒 (设定超时: {timeout_seconds}秒)")
    
    if result is None:
        # 这是期望的结果：后端应该超时
        expected_timeout = 2 + (timeout_seconds - 2) + 3  # 前2秒 + 暂停3秒 + 剩余4秒 = 9秒
        log_with_timestamp(f"📥 后端正确超时（无前端干扰）")
        
        if 8 <= total_test_time <= 11:  # 允许1-2秒误差，预期9秒左右
            log_with_timestamp("✅ 后端用户活动暂停功能工作正常！")
            log_with_timestamp("   - 用户活跃时成功暂停后端计时器")
            log_with_timestamp("   - 用户不活跃时成功恢复后端计时器")
            log_with_timestamp("   - 最终超时时间符合预期（考虑暂停时间）")
            return True
        else:
            log_with_timestamp(f"⚠️  超时时间不符合预期（预期约9秒，实际{total_test_time:.1f}秒）")
            log_with_timestamp("   - 可能后端暂停逻辑仍有问题")
            return False
    else:
        log_with_timestamp("❌ 收到了意外的结果（应该超时但收到了数据）")
        log_with_timestamp(f"   结果: {result}")
        return False

if __name__ == "__main__":
    try:
        success = test_backend_user_activity_logic()
        print(f"\n测试完成，结果: {'成功' if success else '失败'}")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        log_with_timestamp("测试被用户中断")
        sys.exit(2)
    except Exception as e:
        log_with_timestamp(f"测试失败: {e}")
        sys.exit(3)
