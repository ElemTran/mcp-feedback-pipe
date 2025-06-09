/**
 * 超时倒计时模块
 * 负责核心倒计时逻辑，包括启动、暂停、恢复、时间格式化等
 */

import { TimeoutSubmission } from './submission.js';
import { COUNTDOWN_UPDATE_INTERVAL } from '../config/app-config.js';

/**
 * 倒计时处理器类
 */
export class TimeoutCountdown {
  constructor(timeoutSeconds, initialTimeoutSeconds, uiHandler) {
    this.timeoutSeconds = timeoutSeconds;
    this.initialTimeoutSeconds = initialTimeoutSeconds;
    this.uiHandler = uiHandler;

    // 倒计时状态
    this.timeoutInterval = null;
    this.startTime = null;
    this.isPaused = false;
    this.remainingTimeOnPause = 0;

    // 初始化提交处理器
    this.submissionHandler = new TimeoutSubmission(uiHandler);
  }

  /**
   * 更新超时时间配置
   * @param {number} timeoutSeconds - 新的超时时间
   * @param {number} initialTimeoutSeconds - 新的初始超时时间
   */
  updateTimeout(timeoutSeconds, initialTimeoutSeconds) {
    this.timeoutSeconds = timeoutSeconds;
    this.initialTimeoutSeconds = initialTimeoutSeconds;
  }

  /**
   * 重置并开始倒计时
   */
  resetAndStart() {
    this.isPaused = false;
    this.startTime = Date.now();
    this.initialTimeoutSeconds = this.timeoutSeconds; // 进度条基于新的总时长

    if (this.timeoutInterval) {
      clearInterval(this.timeoutInterval);
      this.timeoutInterval = null;
    }
    this.start(); // 重新启动 interval

    // 确保UI状态正确
    const messageElement = this.uiHandler.getElement('timeoutMessage', 'timeoutMessage');
    const countdownElement = this.uiHandler.getElement('timeoutCountdown', 'timeoutCountdown');
    const progressBar = this.uiHandler.getElement('timeoutProgressBar', 'timeoutProgressBar');
    if (messageElement && countdownElement && progressBar) {
      this.uiHandler.updateCountdownDisplay(
        this.timeoutSeconds,
        countdownElement,
        progressBar,
        messageElement,
        this.isPaused,
        this.remainingTimeOnPause,
        this.initialTimeoutSeconds
      );
    }
  }

  /**
   * 启动倒计时 (现在主要用于设置 interval)
   */
  start() {
    // 清除之前的定时器
    if (this.timeoutInterval) {
      clearInterval(this.timeoutInterval);
      this.timeoutInterval = null;
    }
    // 确保 startTime 已设置
    if (this.startTime === null) {
      this.startTime = Date.now();
    }

    this.timeoutInterval = setInterval(
      () => this.updateIntervalCallback(),
      COUNTDOWN_UPDATE_INTERVAL
    );
  }

  /**
   * setInterval 的回调函数
   */
  updateIntervalCallback() {
    if (this.isPaused) return;

    const countdownElement = this.uiHandler.getElement('timeoutCountdown', 'timeoutCountdown');
    const progressBar = this.uiHandler.getElement('timeoutProgressBar', 'timeoutProgressBar');
    const messageElement = this.uiHandler.getElement('timeoutMessage', 'timeoutMessage');

    if (!countdownElement) return; // 如果元素不存在，则不继续

    const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
    const remaining = Math.max(0, this.timeoutSeconds - elapsed);

    this.uiHandler.updateCountdownDisplay(
      remaining,
      countdownElement,
      progressBar,
      messageElement,
      this.isPaused,
      this.remainingTimeOnPause,
      this.initialTimeoutSeconds
    );

    // 超时处理 - P2.1 修复：确保超时时立即调用handleTimeout
    if (remaining <= 0) {
      this.handleTimeout();
      // 超时后立即返回，避免重复处理
    }
  }

  /**
   * 暂停倒计时
   */
  pause() {
    if (this.isPaused) return;
    this.isPaused = true;
    this.remainingTimeOnPause = this.getRemainingTime();

    if (this.timeoutInterval) {
      clearInterval(this.timeoutInterval);
      this.timeoutInterval = null;
    }

    const messageElement = this.uiHandler.getElement('timeoutMessage', 'timeoutMessage');
    if (messageElement) {
      messageElement.innerHTML = `<span id="timeoutCountdown" class="timeout-countdown paused">已暂停</span> (剩余: ${this.formatFriendlyTime(this.remainingTimeOnPause)})`;
    }
  }

  /**
   * 恢复倒计时
   */
  resume() {
    if (!this.isPaused) return;
    this.isPaused = false;

    // 根据 remainingTimeOnPause 调整 startTime
    this.startTime = Date.now() - (this.timeoutSeconds - this.remainingTimeOnPause) * 1000;

    if (!this.timeoutInterval) {
      this.start(); // 重新启动 interval
    }

    const messageElement = this.uiHandler.getElement('timeoutMessage', 'timeoutMessage');
    const countdownElement = this.uiHandler.getElement('timeoutCountdown', 'timeoutCountdown');
    const progressBar = this.uiHandler.getElement('timeoutProgressBar', 'timeoutProgressBar');
    if (messageElement && countdownElement && progressBar) {
      // 恢复时立即更新一次显示
      this.uiHandler.updateCountdownDisplay(
        this.remainingTimeOnPause,
        countdownElement,
        progressBar,
        messageElement,
        this.isPaused,
        this.remainingTimeOnPause,
        this.initialTimeoutSeconds
      );
    }
  }

  /**
   * 因用户活动而暂停倒计时
   */
  pauseDueToActivity() {
    if (this.isPaused) return; // 如果已经暂停了，则不再重复操作
    this.pause();
    const messageElement = this.uiHandler.getElement('timeoutMessage', 'timeoutMessage');
    if (messageElement) {
      messageElement.innerHTML = `<span id="timeoutCountdown" class="timeout-countdown paused">已暂停 (用户活动中)</span> (剩余: ${this.formatFriendlyTime(this.remainingTimeOnPause)})`;
    }
  }

  /**
   * 因不活动而恢复倒计时
   */
  resumeAfterInactivity() {
    if (!this.isPaused) return; // 如果没有暂停，则不需要恢复
    this.resume();
    const messageElement = this.uiHandler.getElement('timeoutMessage', 'timeoutMessage');
    if (messageElement) {
      messageElement.innerHTML = `此窗口将在 <span id="timeoutCountdown" class="timeout-countdown">${this.formatFriendlyTime(this.getRemainingTime())}</span> 后自动关闭`;
    }
  }

  /**
   * 处理超时情况
   */
  handleTimeout() {
    if (this.timeoutInterval) {
      clearInterval(this.timeoutInterval);
      this.timeoutInterval = null;
    }
    this.isPaused = true; // 超时后也标记为暂停状态，防止意外恢复

    // 超时时尝试收集用户已输入的数据并发送
    this.submissionHandler.captureDataOnTimeout();

    // 显示超时提示
    this.uiHandler.showTimeoutNotification();

    // 禁用提交按钮
    this.uiHandler.disableSubmitButton();
  }

  /**
   * 停止倒计时（用于提交成功后）
   */
  stop() {
    if (this.timeoutInterval) {
      clearInterval(this.timeoutInterval);
      this.timeoutInterval = null;
    }
    this.isPaused = true; // 提交后也标记为暂停

    const countdownElement = this.uiHandler.getElement('timeoutCountdown', 'timeoutCountdown');
    const messageElement = this.uiHandler.getElement('timeoutMessage', 'timeoutMessage');

    if (messageElement) {
      messageElement.innerHTML =
        '<span id="timeoutCountdown" class="timeout-countdown completed">已完成</span>';
    } else if (countdownElement) {
      countdownElement.textContent = '已完成';
      countdownElement.className = 'timeout-countdown completed';
    }
  }

  /**
   * 获取剩余时间（秒）
   */
  getRemainingTime() {
    if (this.isPaused) {
      return this.remainingTimeOnPause;
    }
    if (!this.startTime) return this.timeoutSeconds; // 如果计时器未启动，返回总时长
    const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
    return Math.max(0, this.timeoutSeconds - elapsed);
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
   * 获取当前的暂停状态
   */
  get paused() {
    return this.isPaused;
  }

  /**
   * 获取当前超时时间设置
   */
  get currentTimeoutSeconds() {
    return this.timeoutSeconds;
  }

  /**
   * 获取初始超时时间设置
   */
  get currentInitialTimeoutSeconds() {
    return this.initialTimeoutSeconds;
  }
}
