/**
 * 超时UI处理模块
 * 负责所有与超时功能直接相关的UI更新函数，包括倒计时显示、通知、进度条等
 */

import {
  DANGER_THRESHOLD,
  WARNING_THRESHOLD,
  NOTIFICATION_AUTO_HIDE_DELAY
} from '../config/app-config.js';

/**
 * 超时UI处理器类
 * 包含DOM元素缓存和UI更新方法
 */
export class TimeoutUI {
  constructor() {
    // R2.1: DOM元素缓存对象 - 优化DOM查询性能
    this.elements = {
      // 核心UI元素
      timeoutData: null,
      timeoutMessage: null,
      timeoutCountdown: null,
      timeoutProgressBar: null,

      // 表单相关元素
      textFeedback: null,
      feedbackForm: null,
      submitBtn: null,
      csrfToken: null,

      // 自定义超时控制元素
      customTimeoutInput: null,
      applyCustomTimeoutBtn: null,

      // 动态生成的元素
      notificationStyles: null
    };
  }

  /**
   * 获取元素的通用方法，支持懒加载缓存
   * @param {string} elementKey - 元素键名
   * @param {string} elementId - DOM元素ID
   * @returns {HTMLElement|null} DOM元素或null
   */
  getElement(elementKey, elementId) {
    if (this.elements[elementKey] === null) {
      this.elements[elementKey] = document.getElementById(elementId);
    }
    return this.elements[elementKey];
  }

  /**
   * 强制刷新缓存的元素（用于动态生成的元素）
   * @param {string} elementKey - 元素键名
   * @param {string} elementId - DOM元素ID
   * @returns {HTMLElement|null} DOM元素或null
   */
  refreshElement(elementKey, elementId) {
    this.elements[elementKey] = document.getElementById(elementId);
    return this.elements[elementKey];
  }

  /**
   * 清除所有缓存（用于测试或重置）
   */
  clearCache() {
    Object.keys(this.elements).forEach(key => {
      this.elements[key] = null;
    });
  }

  /**
   * 格式化时间显示（更友好的格式）
   * @param {number} totalSeconds - 总秒数
   * @returns {string} 格式化的时间字符串
   */
  formatFriendlyTime(totalSeconds) {
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
   * 更新倒计时显示和进度条
   * @param {number} remaining - 剩余时间（秒）
   * @param {HTMLElement} countdownElement - 倒计时元素
   * @param {HTMLElement} progressBar - 进度条元素
   * @param {HTMLElement} messageElement - 消息元素
   * @param {boolean} isPaused - 是否暂停状态
   * @param {number} remainingTimeOnPause - 暂停时的剩余时间
   * @param {number} initialTimeoutSeconds - 初始超时时间
   */
  updateCountdownDisplay(
    remaining,
    countdownElement,
    progressBar,
    messageElement,
    isPaused = false,
    remainingTimeOnPause = 0,
    initialTimeoutSeconds = 300
  ) {
    const friendlyTime = this.formatFriendlyTime(remaining);

    this._updateMessageDisplay(
      messageElement,
      countdownElement,
      friendlyTime,
      remaining,
      isPaused,
      remainingTimeOnPause
    );
    this._updateProgressBar(progressBar, remaining, initialTimeoutSeconds, isPaused);
    this._updateCountdownStyles(remaining, isPaused);
  }

  /**
   * 更新消息显示
   * @private
   */
  _updateMessageDisplay(
    messageElement,
    countdownElement,
    friendlyTime,
    remaining,
    isPaused,
    remainingTimeOnPause
  ) {
    if (messageElement) {
      this._updateMessageElementContent(
        messageElement,
        friendlyTime,
        remaining,
        isPaused,
        remainingTimeOnPause
      );
    } else if (countdownElement) {
      // Fallback if messageElement is not present
      countdownElement.textContent = friendlyTime;
    }
  }

  /**
   * 更新消息元素内容
   * @private
   */
  _updateMessageElementContent(
    messageElement,
    friendlyTime,
    remaining,
    isPaused,
    remainingTimeOnPause
  ) {
    if (isPaused) {
      // 暂停状态的消息由暂停函数处理，这里不覆盖
      this._updatePausedMessage(messageElement, remainingTimeOnPause);
    } else if (remaining > 0) {
      // P2.2 修复：确保超时消息显示正确，使用更清晰的描述
      messageElement.innerHTML = `此窗口将在 <span id="timeoutCountdown" class="timeout-countdown">${friendlyTime}</span> 后自动提交`;
    } else {
      messageElement.innerHTML =
        '<span id="timeoutCountdown" class="timeout-countdown expired">时间已到，正在提交...</span>';
    }

    // 确保 #timeoutCountdown 元素内的文本也更新
    const embeddedCountdown = messageElement.querySelector('#timeoutCountdown');
    if (embeddedCountdown && !isPaused) {
      embeddedCountdown.textContent = friendlyTime;
    }
  }

  /**
   * 更新暂停状态的消息
   * @private
   */
  _updatePausedMessage(messageElement, remainingTimeOnPause) {
    const embeddedCountdown = messageElement.querySelector('#timeoutCountdown');
    if (embeddedCountdown && embeddedCountdown.textContent.includes('剩余')) {
      // 暂停时，如果消息包含 "剩余"，则更新其中的时间
      embeddedCountdown.innerHTML = `已暂停 (剩余: ${this.formatFriendlyTime(remainingTimeOnPause)})`;
      if (messageElement.textContent.includes('因不活动')) {
        embeddedCountdown.innerHTML = `已暂停 (因不活动) (剩余: ${this.formatFriendlyTime(remainingTimeOnPause)})`;
      }
    }
  }

  /**
   * 更新进度条
   * @private
   */
  _updateProgressBar(progressBar, remaining, initialTimeoutSeconds, isPaused) {
    if (!progressBar) return;

    const progressPercent = (remaining / initialTimeoutSeconds) * 100;
    progressBar.style.width = `${Math.max(0, progressPercent)}%`;

    // 根据剩余时间更新进度条样式
    progressBar.className = 'timeout-progress-bar'; // Reset classes
    progressBar.className += this._getProgressBarStyleClass(remaining, isPaused);
  }

  /**
   * 获取进度条样式类
   * @private
   */
  _getProgressBarStyleClass(remaining, isPaused) {
    if (remaining <= 0) {
      return ' expired';
    } else if (isPaused) {
      return ' paused-style';
    } else if (remaining <= DANGER_THRESHOLD) {
      return ' danger';
    } else if (remaining <= WARNING_THRESHOLD) {
      return ' warning';
    }
    return '';
  }

  /**
   * 更新倒计时样式
   * @private
   */
  _updateCountdownStyles(remaining, isPaused) {
    const currentCountdownDisplay = this.refreshElement('timeoutCountdown', 'timeoutCountdown');
    if (!currentCountdownDisplay) return;

    currentCountdownDisplay.className = 'timeout-countdown'; // Reset classes
    currentCountdownDisplay.className += this._getCountdownStyleClass(remaining, isPaused);
  }

  /**
   * 获取倒计时样式类
   * @private
   */
  _getCountdownStyleClass(remaining, isPaused) {
    if (remaining <= 0) {
      return ' expired';
    } else if (isPaused) {
      return ' paused';
    } else if (remaining <= DANGER_THRESHOLD) {
      return ' danger';
    } else if (remaining <= WARNING_THRESHOLD) {
      return ' warning';
    }
    return '';
  }

  /**
   * 显示用户友好的错误提示
   * @param {string} message - 提示消息
   * @param {string} type - 提示类型 ('info', 'success', 'warning', 'error')
   */
  showUserNotification(message, type = 'info') {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'success' ? 'success' : type === 'warning' ? 'warning' : 'danger'}`;
    notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            animation: slideIn 0.3s ease-out;
        `;

    const icon = type === 'success' ? '✅' : type === 'warning' ? '⚠️' : '❌';
    notification.innerHTML = `
            <strong>${icon} ${message}</strong>
            <button type="button" class="btn-close" onclick="this.parentElement.remove()" style="float: right;">×</button>
        `;

    // 添加CSS动画
    const existingStyles = this.getElement('notificationStyles', 'notification-styles');
    if (!existingStyles) {
      const style = document.createElement('style');
      style.id = 'notification-styles';
      style.textContent = `
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
      document.head.appendChild(style);
      // 更新缓存
      this.elements.notificationStyles = style;
    }

    document.body.appendChild(notification);

    // 自动移除通知
    setTimeout(() => {
      if (notification.parentNode) {
        notification.remove();
      }
    }, NOTIFICATION_AUTO_HIDE_DELAY);
  }

  /**
   * 显示超时通知
   */
  showTimeoutNotification() {
    // 创建超时提示
    const notification = document.createElement('div');
    notification.className = 'alert alert-warning';
    notification.innerHTML = `
            <strong>⏰ 时间到了</strong><br>
            感谢您的耐心！反馈窗口已关闭，如需继续提供反馈，请重新打开反馈通道。
        `;

    // 插入到表单前面
    const form = this.getElement('feedbackForm', 'feedbackForm');
    if (form && form.parentNode) {
      // 避免重复添加通知
      const existingNotification = form.parentNode.querySelector('.alert-warning');
      if (!existingNotification || !existingNotification.textContent.includes('时间到了')) {
        form.parentNode.insertBefore(notification, form);
      }
    }
  }

  /**
   * 禁用提交按钮
   */
  disableSubmitButton() {
    const submitBtn = this.getElement('submitBtn', 'submitBtn');
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = '⏰ 已超时';
      submitBtn.className = submitBtn.className.replace('btn-success', 'btn-secondary');
    }
  }

  /**
   * 启用提交按钮
   */
  enableSubmitButton() {
    const submitBtn = this.getElement('submitBtn', 'submitBtn');
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.textContent = '提交反馈';
      submitBtn.className = submitBtn.className.replace('btn-secondary', 'btn-success');
    }
  }

  /**
   * 更新提交按钮文本
   * @param {string} text - 新的按钮文本
   */
  updateSubmitButtonText(text) {
    const submitBtn = this.getElement('submitBtn', 'submitBtn');
    if (submitBtn) {
      submitBtn.textContent = text;
    }
  }

  /**
   * 显示加载状态
   * @param {string} message - 加载消息
   */
  showLoadingState(message = '处理中...') {
    const submitBtn = this.getElement('submitBtn', 'submitBtn');
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = message;
    }
  }

  /**
   * 隐藏加载状态
   */
  hideLoadingState() {
    this.enableSubmitButton();
  }

  /**
   * 获取表单数据
   * @returns {Object} 表单数据对象
   */
  getFormData() {
    const textFeedbackElement = this.getElement('textFeedback', 'textFeedback');
    const csrfTokenElement = this.getElement('csrfToken', 'csrfToken');

    return {
      textFeedback: textFeedbackElement ? textFeedbackElement.value.trim() : '',
      csrfToken: csrfTokenElement ? csrfTokenElement.value : ''
    };
  }

  /**
   * 清空表单
   */
  clearForm() {
    const textFeedbackElement = this.getElement('textFeedback', 'textFeedback');
    if (textFeedbackElement) {
      textFeedbackElement.value = '';
    }
  }

  /**
   * 设置表单只读状态
   * @param {boolean} readonly - 是否只读
   */
  setFormReadonly(readonly = true) {
    const textFeedbackElement = this.getElement('textFeedback', 'textFeedback');
    if (textFeedbackElement) {
      textFeedbackElement.readOnly = readonly;
    }
  }

  /**
   * 添加表单验证错误提示
   * @param {string} fieldName - 字段名
   * @param {string} message - 错误消息
   */
  addFieldError(fieldName, message) {
    const field = this.getElement(fieldName, fieldName);
    if (field) {
      field.classList.add('is-invalid');

      // 创建或更新错误提示
      let errorDiv = field.parentNode.querySelector('.invalid-feedback');
      if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        field.parentNode.appendChild(errorDiv);
      }
      errorDiv.textContent = message;
    }
  }

  /**
   * 清除表单验证错误
   */
  clearFieldErrors() {
    const form = this.getElement('feedbackForm', 'feedbackForm');
    if (form) {
      form.querySelectorAll('.is-invalid').forEach(field => {
        field.classList.remove('is-invalid');
      });
      form.querySelectorAll('.invalid-feedback').forEach(errorDiv => {
        errorDiv.remove();
      });
    }
  }
}
