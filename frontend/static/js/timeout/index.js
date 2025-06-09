/**
 * 超时处理模块 - 主入口和协调器
 * 负责初始化超时处理功能和协调各个子模块
 */

import { TimeoutCountdown } from './countdown.js';
import { TimeoutActivity } from './activity.js';
import { TimeoutUI } from './ui.js';
import { DEFAULT_TIMEOUT_SECONDS, MIN_CUSTOM_TIMEOUT } from '../config/app-config.js';

// 超时处理器的主要组件实例
let countdownHandler = null;
let activityHandler = null;
let uiHandler = null;

// 超时相关状态
let timeoutSeconds = DEFAULT_TIMEOUT_SECONDS;
let initialTimeoutSeconds = DEFAULT_TIMEOUT_SECONDS;

/**
 * 初始化超时处理
 * 这是超时处理功能的主要入口点
 */
export function initializeTimeoutHandler() {
  try {
    uiHandler = new TimeoutUI();

    const timeoutData = uiHandler.getElement('timeoutData', 'timeoutData');
    if (timeoutData) {
      const rawTimeoutValue = timeoutData.textContent.trim();
      if (rawTimeoutValue) {
        const parsedTimeoutValue = parseInt(rawTimeoutValue, 10);
        if (!isNaN(parsedTimeoutValue) && parsedTimeoutValue > 0) {
          timeoutSeconds = parsedTimeoutValue;
          initialTimeoutSeconds = parsedTimeoutValue;
        }
      }
    }

    countdownHandler = new TimeoutCountdown(
      timeoutSeconds,
      initialTimeoutSeconds,
      uiHandler
    );
    activityHandler = new TimeoutActivity(countdownHandler);

    setupCustomTimeoutControls();

    countdownHandler.resetAndStart();
    activityHandler.startActivityMonitoring();
  } catch (error) {
    // No action needed for initialization errors, as they are not critical.
  }
}

/**
 * 设置自定义超时控制UI
 */
function setupCustomTimeoutControls() {
  const customTimeoutInput = uiHandler.getElement('customTimeoutInput', 'customTimeoutInput');
  const applyCustomTimeoutBtn = uiHandler.getElement(
    'applyCustomTimeoutBtn',
    'applyCustomTimeoutBtn'
  );

  if (applyCustomTimeoutBtn && customTimeoutInput) {
    applyCustomTimeoutBtn.addEventListener('click', () => {
      const newTimeoutValueStr = customTimeoutInput.value;
      const newTimeoutValue = parseInt(newTimeoutValueStr);

      if (!isNaN(newTimeoutValue) && newTimeoutValue >= MIN_CUSTOM_TIMEOUT) {
        timeoutSeconds = newTimeoutValue;
        initialTimeoutSeconds = newTimeoutValue;

        // 更新倒计时处理器的超时时间
        countdownHandler.updateTimeout(timeoutSeconds, initialTimeoutSeconds);
        countdownHandler.resetAndStart();
      } else {
        alert('请输入一个有效的超时时间（数字，且大于等于30秒）。');
        customTimeoutInput.value = timeoutSeconds; // 重置为当前值
      }
    });
  }
}

/**
 * 停止倒计时（用于提交成功后）
 */
export function stopCountdown() {
  if (countdownHandler) {
    countdownHandler.stop();
  }
  if (activityHandler) {
    activityHandler.stopActivityMonitoring();
  }
}

/**
 * 获取剩余时间（秒）
 */
export function getRemainingTime() {
  return countdownHandler ? countdownHandler.getRemainingTime() : timeoutSeconds;
}

/**
 * 重置倒计时（用于重新开始）
 * 保留此函数以兼容旧代码
 */
export function resetCountdown() {
  if (countdownHandler) {
    countdownHandler.resetAndStart();
  }
}
