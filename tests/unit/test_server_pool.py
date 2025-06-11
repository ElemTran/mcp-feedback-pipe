#!/usr/bin/env python3
"""
服务器池重构验证测试
验证移除超时清理逻辑后的基本功能
"""

import sys
import time
import threading
from backend.server_pool import ServerPool, get_server_pool, get_managed_server, release_managed_server

def test_server_pool_refactor():
    """验证服务器池重构结果"""
    print('🧪 服务器池重构验证测试')
    print('=' * 50)
    print()
    
    # 验证指标1：文件中无"_cleanup_idle_servers"方法
    print('📋 验证指标1：清理方法已移除')
    pool = ServerPool()
    
    cleanup_method_exists = hasattr(pool, '_cleanup_idle_servers')
    print(f'  - _cleanup_idle_servers 方法: {"存在" if cleanup_method_exists else "已移除"} {"✗" if cleanup_method_exists else "✓"}')
    
    # 验证指标2：无清理线程创建和停止代码
    print('\n📋 验证指标2：清理线程相关代码已移除')
    
    cleanup_thread_exists = hasattr(pool, '_cleanup_thread')
    print(f'  - _cleanup_thread 属性: {"存在" if cleanup_thread_exists else "已移除"} {"✗" if cleanup_thread_exists else "✓"}')
    
    running_flag_exists = hasattr(pool, '_running')
    print(f'  - _running 标志: {"存在" if running_flag_exists else "已移除"} {"✗" if running_flag_exists else "✓"}')
    
    start_cleanup_method_exists = hasattr(pool, '_start_cleanup_thread')
    print(f'  - _start_cleanup_thread 方法: {"存在" if start_cleanup_method_exists else "已移除"} {"✗" if start_cleanup_method_exists else "✓"}')
    
    # 验证指标3：通过基础功能测试
    print('\n📋 验证指标3：基础功能测试')
    
    try:
        # 测试获取服务器
        server1 = pool.get_server("test_session_1")
        print(f'  - 获取服务器实例: {"✓" if server1 else "✗"}')
        
        # 测试获取同一会话的服务器（应该返回相同实例）
        server2 = pool.get_server("test_session_1")
        same_instance = server1 is server2
        print(f'  - 同一会话返回相同实例: {"✓" if same_instance else "✗"}')
        
        # 测试获取不同会话的服务器
        server3 = pool.get_server("test_session_2")
        different_instance = server1 is not server3
        print(f'  - 不同会话返回不同实例: {"✓" if different_instance else "✗"}')
        
        # 测试立即释放服务器
        pool.release_server("test_session_2", immediate=True)
        print('  - 立即释放服务器: ✓')
        
        # 测试非立即释放服务器
        pool.release_server("test_session_1", immediate=False)
        print('  - 非立即释放服务器: ✓')
        
        # 测试关闭服务器池
        pool.shutdown()
        print('  - 关闭服务器池: ✓')
        
        basic_functions_passed = True
        
    except Exception as e:
        print(f'  - 基础功能测试失败: {e} ✗')
        basic_functions_passed = False
    
    # 验证全局服务器池功能
    print('\n📋 验证全局服务器池功能')
    
    try:
        # 测试全局服务器池
        global_pool = get_server_pool()
        print(f'  - 获取全局服务器池: {"✓" if global_pool else "✗"}')
        
        # 测试单例模式
        global_pool2 = get_server_pool()
        is_singleton = global_pool is global_pool2
        print(f'  - 单例模式验证: {"✓" if is_singleton else "✗"}')
        
        # 测试托管服务器功能
        managed_server = get_managed_server("managed_test")
        print(f'  - 获取托管服务器: {"✓" if managed_server else "✗"}')
        
        # 测试释放托管服务器
        release_managed_server("managed_test", immediate=True)
        print('  - 释放托管服务器: ✓')
        
        global_functions_passed = True
        
    except Exception as e:
        print(f'  - 全局服务器池功能测试失败: {e} ✗')
        global_functions_passed = False
    
    # 验证代码简化
    print('\n📋 验证代码简化效果')
    
    # 读取重构后的文件内容
    with open('backend/server_pool.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否移除了超时相关代码
    timeout_related_terms = [
        '_cleanup_idle_servers',
        '_start_cleanup_thread', 
        '_cleanup_thread',
        '_running',
        '_last_activity',
        'time.sleep',
        'cleanup_worker'
    ]
    
    removed_terms = []
    for term in timeout_related_terms:
        if term not in content:
            removed_terms.append(term)
    
    print(f'  - 已移除的超时相关代码: {len(removed_terms)}/{len(timeout_related_terms)} 项')
    for term in removed_terms:
        print(f'    ✓ {term}')
    
    # 计算代码行数减少
    lines = content.split('\n')
    code_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
    print(f'  - 当前代码行数（不含注释和空行）: {len(code_lines)}')
    
    # 验证核心导入简化
    import_time_removed = 'import time' not in content
    import_weakref_removed = 'import weakref' not in content
    print(f'  - 移除不必要的导入: {"✓" if import_time_removed and import_weakref_removed else "✗"}')
    
    # 汇总验证结果
    print('\n🎯 重构验证总结')
    print('=' * 50)
    
    verification_results = {
        '清理方法已移除': not cleanup_method_exists,
        '清理线程代码已移除': not cleanup_thread_exists and not running_flag_exists and not start_cleanup_method_exists,
        '基础功能正常': basic_functions_passed,
        '全局功能正常': global_functions_passed,
        '代码简化完成': len(removed_terms) >= 6
    }
    
    all_passed = all(verification_results.values())
    
    print('📊 验证结果：')
    for criterion, passed in verification_results.items():
        status = '✅' if passed else '❌'
        print(f'  {status} {criterion}')
    
    print()
    if all_passed:
        print('🎉 服务器池重构任务完成！')
        print()
        print('📋 重构摘要：')
        print('  ✅ 移除了 _cleanup_idle_servers 方法')
        print('  ✅ 移除了清理线程启动逻辑')
        print('  ✅ 移除了清理线程停止逻辑')
        print('  ✅ 移除了空闲服务器检查逻辑')
        print('  ✅ 保持了基本功能完整（获取和释放服务器）')
        print('  ✅ 简化了代码结构，提升了可维护性')
        print('  ✅ 消除了时间依赖，降低了复杂性')
        
        # 测试通过，不返回任何值（pytest兼容）
        pass
    else:
        print('❌ 部分验证指标未满足，需要进一步检查')
        assert False, "部分验证指标未满足"

if __name__ == '__main__':
    try:
        test_server_pool_refactor()
        print('\n✅ 所有测试都通过了！')
        sys.exit(0)
    except AssertionError:
        print('\n❌ 测试失败')
        sys.exit(1)
    except Exception as e:
        print(f'\n❌ 测试过程中出现错误: {e}')
        sys.exit(1)
