/**
 * 用户活动检测模块
 * 负责监控用户活动状态，并相应地暂停或恢复倒计时
 */

import { INACTIVITY_THRESHOLD } from '../config/app-config.js';

/**
 * 用户活动检测处理器类
 */
export class TimeoutActivity {
  constructor(countdownHandler) {
    this.countdownHandler = countdownHandler;
    this.activityTimeout = null;
    this.activityEvents = [
      'mousemove',
      'keydown',
      'keyup',
      'mousedown',
      'mouseup',
      'click',
      'scroll',
      'touchstart',
      'touchmove',
      'focus',
      'input'
    ];
    this.boundResetActivityTimer = this.resetActivityTimer.bind(this);
    this.boundHandleVisibilityChange = this.handleVisibilityChange.bind(this);
  }

  /**
   * 启动用户活动监控
   */
  startActivityMonitoring() {
    // 初始启动不活动计时器（页面加载后开始监控用户活动）
    this.activityTimeout = setTimeout(() => {
      // 如果用户在初始期间没有活动，继续正常倒计时（什么都不做）
      console.log('📝 用户在初始60秒内无活动，继续正常倒计时');
    }, INACTIVITY_THRESHOLD);

    // 注册活动事件监听器
    this.activityEvents.forEach(event => {
      window.addEventListener(event, this.boundResetActivityTimer, { passive: true });
    });

    // 注册页面可见性变化监听器
    document.addEventListener('visibilitychange', this.boundHandleVisibilityChange);

    console.log('🔍 用户活动监控已启动');
  }

  /**
   * 停止用户活动监控
   */
  stopActivityMonitoring() {
    // 清除计时器
    if (this.activityTimeout) {
      clearTimeout(this.activityTimeout);
      this.activityTimeout = null;
    }

    // 移除活动事件监听器
    this.activityEvents.forEach(event => {
      window.removeEventListener(event, this.boundResetActivityTimer);
    });

    // 移除页面可见性变化监听器
    document.removeEventListener('visibilitychange', this.boundHandleVisibilityChange);

    console.log('🛑 用户活动监控已停止');
  }

  /**
   * 重置活动计时器
   * 当检测到用户活动时调用
   */
  resetActivityTimer() {
    // 用户有活动时暂停倒计时
    if (!this.countdownHandler.paused) {
      this.countdownHandler.pauseDueToActivity();
    }

    // 重置不活动计时器：用户停止活动后一段时间恢复倒计时
    if (this.activityTimeout) {
      clearTimeout(this.activityTimeout);
    }
    this.activityTimeout = setTimeout(() => this.resumeAfterInactivity(), INACTIVITY_THRESHOLD);
  }

  /**
   * 不活动后恢复倒计时
   */
  resumeAfterInactivity() {
    if (this.countdownHandler.paused) {
      this.countdownHandler.resumeAfterInactivity();
    }

    // 重新设置不活动计时器，继续监控
    this.activityTimeout = setTimeout(() => this.resumeAfterInactivity(), INACTIVITY_THRESHOLD);
  }

  /**
   * 处理页面可见性变化
   */
  handleVisibilityChange() {
    if (document.hidden) {
      // 页面隐藏时恢复倒计时（用户离开了页面）
      const messageElement = this.countdownHandler.uiHandler.getElement(
        'timeoutMessage',
        'timeoutMessage'
      );
      if (this.countdownHandler.paused && messageElement?.textContent.includes('用户活动中')) {
        this.countdownHandler.resumeAfterInactivity();
      }
    } else {
      // 页面可见时暂停倒计时（用户回到了页面）
      if (!this.countdownHandler.paused) {
        this.countdownHandler.pauseDueToActivity();
      }
      this.resetActivityTimer(); // 页面可见也算一种活动
    }
  }

  /**
   * 手动触发活动检测（用于外部调用）
   */
  triggerActivity() {
    this.resetActivityTimer();
  }

  /**
   * 获取当前不活动阈值
   */
  get inactivityThreshold() {
    return INACTIVITY_THRESHOLD;
  }

  /**
   * 检查是否正在监控活动
   */
  get isMonitoring() {
    return this.activityTimeout !== null;
  }
}
