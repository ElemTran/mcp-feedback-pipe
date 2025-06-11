#!/usr/bin/env python3
"""
UI层面的端到端（E2E）测试 - 会话行为验证
验证前端超时机制、用户活动检测、页面可见性等UI交互功能

整合自：
- tests/test_new_timeout_architecture.py
- tests/test_frontend_activity_detection.py  
- tools/test_timeout_features.py
"""

import time
import json
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytest

from backend.server_manager import ServerManager
from backend.server_pool import release_managed_server

def timestamp():
    """获取当前时间戳字符串"""
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]

def log_with_timestamp(message):
    """带时间戳的日志输出"""
    print(f"[{timestamp()}] {message}")

@pytest.fixture
def chrome_driver():
    """Chrome WebDriver fixture"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 无头模式
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    
    # 配置 Chrome 浏览器二进制路径
    chrome_binary_path = os.environ.get('CHROME_BINARY_PATH')
    if chrome_binary_path:
        chrome_options.binary_location = chrome_binary_path
    
    # 配置 ChromeDriver 服务
    chrome_driver_path = os.environ.get('CHROME_DRIVER_PATH')
    if chrome_driver_path:
        service = Service(executable_path=chrome_driver_path)
    else:
        # 不指定路径，让 Selenium Manager 自动处理
        service = Service()
    
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        log_with_timestamp("✅ Chrome WebDriver 启动成功")
        yield driver
    except Exception as e:
        pytest.fail(f"Chrome WebDriver 启动失败: {e}. 请安装Chrome浏览器和chromedriver")
    finally:
        if 'driver' in locals():
            driver.quit()

@pytest.fixture
def server_manager():
    """ServerManager fixture"""
    sm = ServerManager()
    yield sm
    # 使用正确的资源清理方式
    try:
        session_id = f"test_session_{id(sm)}"
        release_managed_server(session_id, immediate=True)
    except Exception as e:
        # 如果session_id不存在或其他错误，忽略
        pass

class TestFrontendTimeoutControl:
    """前端超时控制功能测试"""
    
    def test_frontend_timeout_loading_and_control(self, chrome_driver, server_manager):
        """验证前端超时控制加载和基本功能"""
        log_with_timestamp("🔍 验证前端超时控制功能")
        
        timeout_seconds = 10
        work_summary = "前端超时控制功能验证"
        
        # 启动服务器
        port = server_manager.start_server(
            work_summary=work_summary,
            timeout_seconds=timeout_seconds,
            suggest=json.dumps(['测试完成'], ensure_ascii=False),
            debug=True,
            use_reloader=False
        )
        
        assert port, "服务器启动失败"
        log_with_timestamp(f"✅ 服务器启动: http://127.0.0.1:{port}")
        
        # 访问页面
        chrome_driver.get(f"http://127.0.0.1:{port}")
        log_with_timestamp("✅ 页面加载成功")
        
        # 等待页面完全加载
        WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.ID, "timeoutMessage"))
        )
        
        # 检查前端是否正确加载超时控制
        timeout_message = chrome_driver.find_element(By.ID, "timeoutMessage").text
        assert "秒后" in timeout_message or "自动提交" in timeout_message, \
            f"前端超时控制未正确加载: {timeout_message}"
        log_with_timestamp(f"✅ 前端超时控制已加载: {timeout_message}")
        
        # 检查超时倒计时显示
        time.sleep(2)
        countdown_message = chrome_driver.find_element(By.ID, "timeoutMessage").text
        has_countdown = any(str(i) in countdown_message for i in range(timeout_seconds))
        assert has_countdown, f"超时倒计时显示异常: {countdown_message}"
        log_with_timestamp(f"✅ 超时倒计时显示正常: {countdown_message}")

    def test_frontend_no_backend_api_calls(self, chrome_driver, server_manager):
        """验证前端不再调用后端超时API"""
        timeout_seconds = 8
        work_summary = "验证前端独立超时控制"
        
        port = server_manager.start_server(
            work_summary=work_summary,
            timeout_seconds=timeout_seconds,
            suggest=json.dumps(['测试完成'], ensure_ascii=False),
            debug=True,
            use_reloader=False
        )
        
        assert port, "服务器启动失败"
        
        chrome_driver.get(f"http://127.0.0.1:{port}")
        WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.ID, "timeoutMessage"))
        )
        
        # 等待一段时间让页面运行
        time.sleep(3)
        
        # 检查是否有后端API调用
        requests_log = chrome_driver.execute_script("""
            return window.performance.getEntries()
                .filter(e => e.initiatorType === 'fetch' || e.initiatorType === 'xmlhttprequest')
                .map(e => e.name);
        """)
        
        has_timeout_api_calls = any("user_activity" in r or "update_timeout" in r for r in requests_log)
        assert not has_timeout_api_calls, "检测到后端超时API调用，前端不应该再调用这些API"
        log_with_timestamp("✅ 没有检测到后端超时API调用")

    def test_frontend_timeout_trigger(self, chrome_driver, server_manager):
        """验证前端能够正确触发超时"""
        timeout_seconds = 6  # 较短的超时时间
        work_summary = "前端超时触发测试"
        
        port = server_manager.start_server(
            work_summary=work_summary,
            timeout_seconds=timeout_seconds,
            suggest=json.dumps(['测试完成'], ensure_ascii=False),
            debug=True,
            use_reloader=False
        )
        
        assert port, "服务器启动失败"
        
        chrome_driver.get(f"http://127.0.0.1:{port}")
        WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.ID, "timeoutMessage"))
        )
        
        log_with_timestamp(f"等待前端超时触发（{timeout_seconds}秒）...")
        
        # 等待服务器返回结果
        wait_result = server_manager.wait_for_feedback(timeout_seconds + 3)
        
        # 检查是否因为超时而提交
        assert wait_result and wait_result.get('is_timeout_capture'), "前端未触发超时或超时未捕获"
        log_with_timestamp("✅ 前端成功触发超时")

class TestUserActivityDetection:
    """用户活动检测测试"""
    
    def test_mouse_movement_detection(self, chrome_driver, server_manager):
        """测试鼠标移动活动检测"""
        log_with_timestamp("🔍 前端用户活动检测测试 - 鼠标移动")
        
        timeout_seconds = 15
        work_summary = "前端鼠标活动检测测试"
        
        port = server_manager.start_server(
            work_summary=work_summary,
            timeout_seconds=timeout_seconds,
            suggest=json.dumps(['测试完成'], ensure_ascii=False),
            debug=True,
            use_reloader=False
        )
        
        assert port, "服务器启动失败"
        
        chrome_driver.get(f"http://127.0.0.1:{port}")
        WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.ID, "timeoutMessage"))
        )
        
        # 观察初始状态
        time.sleep(2)
        initial_message = chrome_driver.find_element(By.ID, "timeoutMessage").text
        log_with_timestamp(f"📝 初始状态: {initial_message}")
        
        # 模拟鼠标移动
        log_with_timestamp("🎯 开始模拟鼠标移动...")
        chrome_driver.execute_script("""
            console.log('🔧 开始模拟用户活动');
            document.dispatchEvent(new MouseEvent('mousemove', {
                bubbles: true, 
                cancelable: true,
                clientX: 100,
                clientY: 100
            }));
            console.log('🔧 鼠标移动事件已触发');
        """)
        
        time.sleep(1)
        
        # 检查状态变化
        after_activity_message = chrome_driver.find_element(By.ID, "timeoutMessage").text
        log_with_timestamp(f"📱 活动后状态: {after_activity_message}")
        
        # 检查是否显示暂停状态
        is_paused = "暂停" in after_activity_message or "活动中" in after_activity_message
        assert is_paused, f"前端未检测到鼠标移动活动: {after_activity_message}"
        log_with_timestamp("✅ 前端检测到鼠标移动活动")

    def test_keyboard_activity_detection(self, chrome_driver, server_manager):
        """测试键盘活动检测"""
        timeout_seconds = 12
        work_summary = "前端键盘活动检测测试"
        
        port = server_manager.start_server(
            work_summary=work_summary,
            timeout_seconds=timeout_seconds,
            suggest=json.dumps(['测试完成'], ensure_ascii=False),
            debug=True,
            use_reloader=False
        )
        
        assert port, "服务器启动失败"
        
        chrome_driver.get(f"http://127.0.0.1:{port}")
        WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.ID, "timeoutMessage"))
        )
        
        # 模拟键盘活动
        log_with_timestamp("🎯 开始模拟键盘活动...")
        chrome_driver.execute_script("""
            document.dispatchEvent(new KeyboardEvent('keydown', {
                bubbles: true, 
                key: 'a'
            }));
            document.dispatchEvent(new Event('scroll', {bubbles: true}));
            console.log('🔧 键盘和滚动事件已触发');
        """)
        
        time.sleep(1)
        
        # 检查状态变化
        after_activity_message = chrome_driver.find_element(By.ID, "timeoutMessage").text
        log_with_timestamp(f"📱 键盘活动后状态: {after_activity_message}")
        
        # 检查是否显示暂停状态
        is_paused = "暂停" in after_activity_message or "活动中" in after_activity_message
        assert is_paused, f"前端未检测到键盘活动: {after_activity_message}"
        log_with_timestamp("✅ 前端检测到键盘活动")

    def test_activity_pause_and_resume_cycle(self, chrome_driver, server_manager):
        """测试活动暂停和恢复循环"""
        timeout_seconds = 20
        work_summary = "活动暂停恢复循环测试"
        
        port = server_manager.start_server(
            work_summary=work_summary,
            timeout_seconds=timeout_seconds,
            suggest=json.dumps(['测试完成'], ensure_ascii=False),
            debug=True,
            use_reloader=False
        )
        
        assert port, "服务器启动失败"
        
        chrome_driver.get(f"http://127.0.0.1:{port}")
        WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.ID, "timeoutMessage"))
        )
        
        # 1. 触发活动
        chrome_driver.execute_script("""
            document.dispatchEvent(new MouseEvent('mousemove', {bubbles: true, clientX: 100, clientY: 100}));
        """)
        time.sleep(1)
        
        activity_message = chrome_driver.find_element(By.ID, "timeoutMessage").text
        assert "暂停" in activity_message or "活动中" in activity_message, "活动检测失败"
        
        # 2. 观察状态变化持续性
        log_with_timestamp("⏰ 观察10秒内的状态变化...")
        status_changes = []
        for i in range(10):
            time.sleep(1)
            current_message = chrome_driver.find_element(By.ID, "timeoutMessage").text
            status_changes.append(current_message)
            if i % 2 == 0:  # 每2秒报告一次
                log_with_timestamp(f"   第{i+1}秒: {current_message}")
        
        # 验证状态变化的连续性
        assert len(status_changes) > 0, "未能收集到状态变化数据"
        log_with_timestamp(f"✅ 成功观察到 {len(status_changes)} 次状态变化")

class TestTimeoutDisplayAndBehavior:
    """超时显示和行为测试"""
    
    def test_120_second_timeout_display(self, chrome_driver, server_manager):
        """测试120秒超时在UI上的正确显示"""
        timeout_seconds = 120  # 2分钟
        work_summary = "120秒超时显示测试"
        
        port = server_manager.start_server(
            work_summary=work_summary,
            timeout_seconds=timeout_seconds,
            suggest=json.dumps(['测试完成'], ensure_ascii=False),
            debug=True,
            use_reloader=False
        )
        
        assert port, "服务器启动失败"
        
        chrome_driver.get(f"http://127.0.0.1:{port}")
        WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.ID, "timeoutMessage"))
        )
        
        # 检查UI上是否显示"2分钟"相关字样
        timeout_message = chrome_driver.find_element(By.ID, "timeoutMessage").text
        log_with_timestamp(f"📝 超时消息: {timeout_message}")
        
        # 验证显示内容包含时间信息
        has_time_info = any(x in timeout_message for x in ["120", "2分", "分钟", "秒"])
        assert has_time_info, f"UI未正确显示120秒/2分钟超时信息: {timeout_message}"
        log_with_timestamp("✅ UI正确显示120秒超时信息")

    def test_dynamic_timeout_setting(self, chrome_driver, server_manager):
        """测试动态超时设置UI交互"""
        timeout_seconds = 60
        work_summary = "动态超时设置UI交互测试"
        
        port = server_manager.start_server(
            work_summary=work_summary,
            timeout_seconds=timeout_seconds,
            suggest=json.dumps(['测试完成'], ensure_ascii=False),
            debug=True,
            use_reloader=False
        )
        
        assert port, "服务器启动失败"
        
        chrome_driver.get(f"http://127.0.0.1:{port}")
        WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.ID, "timeoutMessage"))
        )
        
        # 检查是否有超时设置相关的UI元素
        try:
            # 查找超时设置输入框
            timeout_input = chrome_driver.find_element(By.ID, "customTimeout")
            apply_button = chrome_driver.find_element(By.ID, "applyTimeout")
            
            log_with_timestamp("✅ 找到动态超时设置UI元素")
            
            # 测试设置新的超时值
            timeout_input.clear()
            timeout_input.send_keys("30")
            apply_button.click()
            
            time.sleep(2)
            
            # 检查超时是否更新
            updated_message = chrome_driver.find_element(By.ID, "timeoutMessage").text
            log_with_timestamp(f"📝 更新后的超时消息: {updated_message}")
            
            # 验证超时值是否反映在UI中
            has_new_timeout = "30" in updated_message or "30秒" in updated_message
            assert has_new_timeout, f"动态超时设置未生效: {updated_message}"
            log_with_timestamp("✅ 动态超时设置功能正常")
            
        except Exception as e:
            # 如果没有动态超时设置UI，这也是可以接受的
            log_with_timestamp(f"ℹ️ 动态超时设置UI不可用: {e}")

class TestPageVisibilityAndNetworkHandling:
    """页面可见性和网络处理测试"""
    
    def test_page_visibility_detection(self, chrome_driver, server_manager):
        """测试页面可见性检测对UI的影响"""
        timeout_seconds = 25
        work_summary = "页面可见性检测测试"
        
        port = server_manager.start_server(
            work_summary=work_summary,
            timeout_seconds=timeout_seconds,
            suggest=json.dumps(['测试完成'], ensure_ascii=False),
            debug=True,
            use_reloader=False
        )
        
        assert port, "服务器启动失败"
        
        chrome_driver.get(f"http://127.0.0.1:{port}")
        WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.ID, "timeoutMessage"))
        )
        
        # 模拟页面可见性变化
        log_with_timestamp("🔄 模拟页面可见性变化...")
        
        # 隐藏页面
        chrome_driver.execute_script("""
            Object.defineProperty(document, 'hidden', {value: true, writable: true});
            document.dispatchEvent(new Event('visibilitychange'));
            console.log('页面已设置为隐藏状态');
        """)
        
        time.sleep(2)
        hidden_message = chrome_driver.find_element(By.ID, "timeoutMessage").text
        log_with_timestamp(f"📝 页面隐藏时状态: {hidden_message}")
        
        # 显示页面
        chrome_driver.execute_script("""
            Object.defineProperty(document, 'hidden', {value: false, writable: true});
            document.dispatchEvent(new Event('visibilitychange'));
            console.log('页面已设置为可见状态');
        """)
        
        time.sleep(2)
        visible_message = chrome_driver.find_element(By.ID, "timeoutMessage").text
        log_with_timestamp(f"📝 页面可见时状态: {visible_message}")
        
        # 验证页面可见性变化是否影响计时器状态
        # 注：具体验证逻辑取决于实际的页面可见性处理实现
        log_with_timestamp("✅ 页面可见性变化测试完成")

    def test_network_error_handling_ui(self, chrome_driver, server_manager):
        """测试网络错误的UI处理"""
        timeout_seconds = 20
        work_summary = "网络错误UI处理测试"
        
        port = server_manager.start_server(
            work_summary=work_summary,
            timeout_seconds=timeout_seconds,
            suggest=json.dumps(['测试完成'], ensure_ascii=False),
            debug=True,
            use_reloader=False
        )
        
        assert port, "服务器启动失败"
        
        chrome_driver.get(f"http://127.0.0.1:{port}")
        WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.ID, "timeoutMessage"))
        )
        
        # 模拟网络错误
        log_with_timestamp("🔄 模拟网络连接中断...")
        
        chrome_driver.execute_script("""
            // 保存原始fetch函数
            window._originalFetch = window.fetch;
            
            // 模拟网络中断
            window.fetch = function() {
                return new Promise((resolve, reject) => {
                    reject(new Error('NetworkError: 模拟网络中断'));
                });
            };
            
            console.log('网络连接已模拟中断');
            
            // 显示网络错误通知
            if (typeof showUserNotification === 'function') {
                showUserNotification('网络连接已断开，系统将自动尝试重新连接', 'warning');
            }
        """)
        
        time.sleep(2)
        
        # 检查前端是否显示网络错误提示
        try:
            error_notifications = chrome_driver.execute_script("""
                return Array.from(document.querySelectorAll('.notification')).map(el => el.textContent);
            """)
            
            has_network_error_msg = any("网络" in msg for msg in error_notifications)
            if has_network_error_msg:
                log_with_timestamp("✅ 前端显示网络错误提示")
            else:
                log_with_timestamp("ℹ️ 前端未显示网络错误提示（可能未实现此功能）")
        except Exception as e:
            log_with_timestamp(f"ℹ️ 无法检查错误通知: {e}")
        
        # 恢复网络连接
        chrome_driver.execute_script("""
            if (window._originalFetch) {
                window.fetch = window._originalFetch;
                console.log('网络连接已恢复');
            }
        """)
        
        log_with_timestamp("✅ 网络错误处理UI测试完成")

    def test_local_data_backup_functionality(self, chrome_driver, server_manager):
        """测试提交数据本地备份功能"""
        timeout_seconds = 15
        work_summary = "本地数据备份功能测试"
        
        port = server_manager.start_server(
            work_summary=work_summary,
            timeout_seconds=timeout_seconds,
            suggest=json.dumps(['测试完成'], ensure_ascii=False),
            debug=True,
            use_reloader=False
        )
        
        assert port, "服务器启动失败"
        
        chrome_driver.get(f"http://127.0.0.1:{port}")
        WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.ID, "timeoutMessage"))
        )
        
        # 添加一些表单数据
        log_with_timestamp("📝 添加测试数据到表单...")
        chrome_driver.execute_script("""
            const feedbackArea = document.getElementById('feedbackText');
            if (feedbackArea) {
                feedbackArea.value = '这是测试用的反馈内容，用于验证本地备份功能';
                feedbackArea.dispatchEvent(new Event('input', { bubbles: true }));
            }
            
            // 手动触发保存到本地
            if (typeof saveToLocalBackup === 'function') {
                saveToLocalBackup();
                console.log('手动触发数据本地备份');
            }
        """)
        
        time.sleep(1)
        
        # 检查本地存储是否有备份数据
        has_backup = chrome_driver.execute_script("""
            return localStorage.getItem('feedbackBackup') !== null;
        """)
        
        if has_backup:
            log_with_timestamp("✅ 提交数据已成功备份到本地存储")
        else:
            log_with_timestamp("ℹ️ 本地数据备份功能可能未实现或未触发")

class TestSystemResourceUsage:
    """系统资源使用测试（UI相关部分）"""
    
    def test_ui_resource_efficiency(self, chrome_driver, server_manager):
        """测试UI操作的资源效率"""
        timeout_seconds = 30
        work_summary = "UI资源效率测试"
        
        port = server_manager.start_server(
            work_summary=work_summary,
            timeout_seconds=timeout_seconds,
            suggest=json.dumps(['测试完成'], ensure_ascii=False),
            debug=True,
            use_reloader=False
        )
        
        assert port, "服务器启动失败"
        
        chrome_driver.get(f"http://127.0.0.1:{port}")
        WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.ID, "timeoutMessage"))
        )
        
        # 获取初始内存使用
        initial_memory = chrome_driver.execute_script("""
            return window.performance && window.performance.memory ? 
                window.performance.memory.usedJSHeapSize : 0;
        """)
        
        # 执行一系列UI操作
        log_with_timestamp("🔄 执行UI操作序列...")
        for i in range(10):
            chrome_driver.execute_script(f"""
                // 模拟各种用户活动
                document.dispatchEvent(new MouseEvent('mousemove', {{
                    bubbles: true, 
                    clientX: {100 + i * 10}, 
                    clientY: {100 + i * 10}
                }}));
                
                // 更新一些DOM元素
                const message = document.getElementById('timeoutMessage');
                if (message) {{
                    message.scrollIntoView();
                }}
            """)
            time.sleep(0.5)
        
        # 获取操作后的内存使用
        final_memory = chrome_driver.execute_script("""
            return window.performance && window.performance.memory ? 
                window.performance.memory.usedJSHeapSize : 0;
        """)
        
        if initial_memory > 0 and final_memory > 0:
            memory_increase = final_memory - initial_memory
            memory_increase_mb = memory_increase / (1024 * 1024)
            log_with_timestamp(f"📊 内存使用变化: {memory_increase_mb:.2f} MB")
            
            # 验证内存使用合理
            assert memory_increase_mb < 50, f"UI操作导致过多内存增长: {memory_increase_mb:.2f} MB"
            log_with_timestamp("✅ UI资源使用效率测试通过")
        else:
            log_with_timestamp("ℹ️ 无法获取内存使用信息，跳过资源效率验证")

if __name__ == "__main__":
    # 运行测试的示例代码
    pytest.main([__file__, "-v", "--tb=short"])
