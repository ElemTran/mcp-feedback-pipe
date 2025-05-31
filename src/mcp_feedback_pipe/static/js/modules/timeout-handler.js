/**
 * 超时处理模块
 * 管理超时倒计时和用户体验优化
 */

let timeoutInterval = null;
let startTime = null;
let timeoutSeconds = 300; // 默认5分钟，但会被HTML中的值覆盖
let initialTimeoutSeconds = 300; // 新增：用于存储初始设定的总超时时长

/**
 * 初始化超时处理
 */
export function initializeTimeoutHandler() {
    try {
        // 从页面获取超时时间配置
        const timeoutData = document.getElementById('timeoutData');

        if (timeoutData) {
            const rawTimeoutValue = timeoutData.textContent.trim();
            if (rawTimeoutValue !== '') {
                const parsedTimeoutValue = parseInt(rawTimeoutValue);
                if (!isNaN(parsedTimeoutValue) && parsedTimeoutValue > 0) {
                    timeoutSeconds = parsedTimeoutValue;
                    initialTimeoutSeconds = parsedTimeoutValue; // 保存初始值
                    console.log(`⏰ 超时时间设置为: ${timeoutSeconds}秒`);
                } else {
                    console.warn(`⚠️ 解析超时时间失败: '${rawTimeoutValue}'，将使用默认值 ${timeoutSeconds} 秒`);
                }
            } else {
                console.warn(`⚠️ timeoutData内容为空，将使用默认值 ${timeoutSeconds} 秒`);
            }
        } else {
            console.warn(`⚠️ 未找到timeoutData元素，将使用默认值 ${timeoutSeconds} 秒`);
        }

        // 记录开始时间
        startTime = Date.now();
        
        // 启动倒计时
        startCountdown();
        
        console.log(`⏰ 超时处理初始化完成，超时时间: ${timeoutSeconds}秒`);
        
    } catch (error) {
        console.error('❌ 超时处理初始化失败:', error);
    }
}

/**
 * 格式化时间显示（更友好的格式）
 */
function formatFriendlyTime(totalSeconds) {
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    
    if (minutes > 0) {
        if (seconds > 0) {
            return `${minutes}分${seconds}秒`;
        } else {
            return `${minutes}分钟`;
        }
    } else {
        return `${seconds}秒`;
    }
}

/**
 * 启动倒计时
 */
function startCountdown() {
    const countdownElement = document.getElementById('timeoutCountdown');
    const progressBar = document.getElementById('timeoutProgressBar');
    const messageElement = document.getElementById('timeoutMessage');
    
    if (!countdownElement) return;
    
    // 清除之前的定时器
    if (timeoutInterval) {
        clearInterval(timeoutInterval);
    }
    
    timeoutInterval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        const remaining = Math.max(0, timeoutSeconds - elapsed);
        
        updateCountdownDisplay(remaining, countdownElement, progressBar, messageElement);
        
        // 超时处理
        if (remaining <= 0) {
            handleTimeout();
        }
    }, 1000);
}

/**
 * 更新倒计时显示和进度条
 */
function updateCountdownDisplay(remaining, countdownElement, progressBar, messageElement) {
    // 更新倒计时文本
    const friendlyTime = formatFriendlyTime(remaining);
    countdownElement.textContent = friendlyTime;
    
    // 更新提示消息
    if (messageElement) {
        if (remaining > 0) {
            messageElement.innerHTML = `此窗口将在 <span id="timeoutCountdown" class="timeout-countdown">${friendlyTime}</span> 后自动关闭`;
        } else {
            messageElement.innerHTML = `<span id="timeoutCountdown" class="timeout-countdown expired">窗口已超时</span>`;
        }
    }
    
    // 更新进度条
    if (progressBar) {
        const progressPercent = (remaining / initialTimeoutSeconds) * 100;
        progressBar.style.width = `${Math.max(0, progressPercent)}%`;
        
        // 根据剩余时间更新进度条样式
        progressBar.className = 'timeout-progress-bar';
        if (remaining <= 0) {
            progressBar.className += ' expired';
        } else if (remaining <= 30) {
            progressBar.className += ' danger';
        } else if (remaining <= 60) {
            progressBar.className += ' warning';
        }
    }
    
    // 根据剩余时间更新倒计时样式
    countdownElement.className = 'timeout-countdown';
    if (remaining <= 0) {
        countdownElement.className += ' expired';
    } else if (remaining <= 30) {
        countdownElement.className += ' danger';
    } else if (remaining <= 60) {
        countdownElement.className += ' warning';
    }
}

/**
 * 处理超时情况
 */
function handleTimeout() {
    if (timeoutInterval) {
        clearInterval(timeoutInterval);
        timeoutInterval = null;
    }
    
    // 显示超时提示
    showTimeoutNotification();
    
    // 禁用提交按钮
    disableSubmitButton();
    
    console.warn('⚠️ 反馈收集已超时');
}

/**
 * 显示超时通知
 */
function showTimeoutNotification() {
    // 创建超时提示
    const notification = document.createElement('div');
    notification.className = 'alert alert-warning';
    notification.innerHTML = `
        <strong>⏰ 时间到了</strong><br>
        感谢您的耐心！反馈窗口已关闭，如需继续提供反馈，请重新打开反馈通道。
    `;
    
    // 插入到表单前面
    const form = document.getElementById('feedbackForm');
    if (form && form.parentNode) {
        form.parentNode.insertBefore(notification, form);
    }
}

/**
 * 禁用提交按钮
 */
function disableSubmitButton() {
    const submitBtn = document.getElementById('submitBtn');
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = '⏰ 已超时';
        submitBtn.className = submitBtn.className.replace('btn-success', 'btn-secondary');
    }
}

/**
 * 停止倒计时（用于提交成功后）
 */
export function stopCountdown() {
    if (timeoutInterval) {
        clearInterval(timeoutInterval);
        timeoutInterval = null;
    }
    
    const countdownElement = document.getElementById('timeoutCountdown');
    if (countdownElement) {
        countdownElement.textContent = '已完成';
        countdownElement.className = 'timeout-countdown';
    }
}

/**
 * 获取剩余时间（秒）
 */
export function getRemainingTime() {
    if (!startTime) return 0;
    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    return Math.max(0, timeoutSeconds - elapsed);
}

/**
 * 重置倒计时（用于重新开始）
 */
export function resetCountdown() {
    startTime = Date.now();
    startCountdown();
} 