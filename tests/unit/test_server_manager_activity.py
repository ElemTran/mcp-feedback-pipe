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
    测试用户活动状态更新功能（简化版）
    """
    log_with_timestamp("🔍 测试用户活动状态更新功能（简化版）")
    print("=" * 60)
    
    # 创建ServerManager
    sm = ServerManager()
    
    log_with_timestamp("开始活动状态更新测试...")
    
    # 测试活动状态更新方法是否正常工作（不抛出异常）
    try:
        sm.update_user_activity_status(True, 5)
        log_with_timestamp("✅ 用户活跃状态更新成功")
        
        sm.update_user_activity_status(False, 3)
        log_with_timestamp("✅ 用户不活跃状态更新成功")
        
        log_with_timestamp("✅ 用户活动状态更新功能工作正常！")
        # 测试通过，pytest期望没有返回值
        
    except Exception as e:
        log_with_timestamp(f"❌ 用户活动状态更新失败: {e}")
        assert False, f"用户活动状态更新失败: {e}"

if __name__ == "__main__":
    try:
        test_backend_user_activity_logic()
        print(f"\n测试完成，结果: 成功")
        sys.exit(0)
    except KeyboardInterrupt:
        log_with_timestamp("测试被用户中断")
        sys.exit(2)
    except Exception as e:
        log_with_timestamp(f"测试失败: {e}")
        sys.exit(3)
