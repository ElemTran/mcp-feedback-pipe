/**
 * 超时数据提交模块
 * 负责超时发生时的数据收集、图片处理、带重试的发送、失败处理等逻辑
 */

import { getSelectedImages } from '../modules/image-handler.js';
import { TimeoutBackup } from './backup.js';
import { MAX_RETRY_ATTEMPTS, NETWORK_TIMEOUT, RETRY_DELAYS } from '../config/app-config.js';

/**
 * 超时数据提交处理器类
 */
export class TimeoutSubmission {
  constructor(uiHandler) {
    this.uiHandler = uiHandler;
    this.backupHandler = new TimeoutBackup();
  }

  /**
   * 超时时收集数据并发送到服务器 - 重构版本
   * 负责协调数据收集、发送和失败处理的主流程
   */
  async captureDataOnTimeout() {
    let feedbackData = null;

    try {
      // 步骤1: 收集表单数据
      feedbackData = this.collectFormData();

      // 步骤2: 尝试发送数据（包含重试逻辑）
      const sendSuccess = await this.sendTimeoutDataWithRetries(feedbackData);

      // 步骤3: 如果发送失败，处理本地备份
      if (!sendSuccess) {
        this.handleFailedTimeoutSubmission(feedbackData);
      }
    } catch (error) {
      // 即使在异常情况下也要尝试本地备份
      if (feedbackData) {
        try {
          this.handleFailedTimeoutSubmission(feedbackData);
          this.uiHandler.showUserNotification('系统错误，但数据已安全保存到本地', 'warning');
        } catch (backupError) {
          this.uiHandler.showUserNotification('数据保存完全失败，请手动复制您的输入内容', 'error');
        }
      } else {
        this.uiHandler.showUserNotification('无法获取数据进行备份', 'error');
      }
    }
  }

  /**
   * 收集表单数据
   * @returns {Object} 包含文本和图片数据的对象
   */
  collectFormData() {
    // 收集当前文本框内容
    const textFeedbackElement = this.uiHandler.getElement('textFeedback', 'textFeedback');
    const currentText = textFeedbackElement ? textFeedbackElement.value.trim() : '';

    // 获取当前已选择的图片数据
    const currentImages = getSelectedImages();

    // 准备反馈数据
    const feedbackData = {
      text: currentText,
      images: currentImages,
      timestamp: new Date().toISOString(),
      source: 'frontend_timeout'
    };

    return feedbackData;
  }

  /**
   * 准备图片数据用于上传
   * @param {Array} images - 图片数据数组
   * @param {FormData} formData - 要添加图片的FormData对象
   */
  prepareImageDataForUpload(images, formData) {
    if (!images || images.length === 0) {
      return;
    }

    for (let i = 0; i < images.length; i++) {
      const imageData = images[i];

      // 从base64数据中提取MIME类型
      const dataUrlParts = imageData.data.split(',');
      const mimeMatch = dataUrlParts[0].match(/data:([^;]+);base64/);
      const mimeType = mimeMatch ? mimeMatch[1] : 'image/jpeg';

      // 根据MIME类型确定文件扩展名
      const extensionMap = {
        'image/jpeg': '.jpg',
        'image/png': '.png',
        'image/gif': '.gif',
        'image/webp': '.webp'
      };
      const extension = extensionMap[mimeType] || '.jpg';

      // 将base64数据转换为Blob，然后转换为File
      const byteCharacters = atob(dataUrlParts[1]);
      const byteNumbers = new Array(byteCharacters.length);
      for (let j = 0; j < byteCharacters.length; j++) {
        byteNumbers[j] = byteCharacters.charCodeAt(j);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: mimeType });
      const fileName = imageData.name || `timeout_capture_${i}${extension}`;
      const file = new File([blob], fileName, { type: mimeType });
      formData.append('images', file);
    }
  }

  /**
   * 发送超时数据并执行重试逻辑
   * @param {Object} feedbackData - 收集的反馈数据
   * @returns {Promise<boolean>} 发送是否成功
   */
  async sendTimeoutDataWithRetries(feedbackData) {
    // R3.1: 性能监控 - 记录sendTimeoutDataWithRetries函数执行时间
    const perfStart = performance.now();

    const formData = this._prepareTimeoutFormData(feedbackData);
    const csrfToken = this._getCsrfToken();

    // 多重重试机制
    for (let attempt = 0; attempt < MAX_RETRY_ATTEMPTS; attempt++) {
      try {
        const result = await this._attemptSubmission(formData, csrfToken, attempt);
        if (result.success) {
          this._handleSuccessfulSubmission(perfStart);
          return true;
        } else {
          throw new Error(`服务器返回错误: ${result.message || '未知错误'}`);
        }
      } catch (error) {
        this._handleSubmissionError(error, attempt);

        // 如果不是最后一次尝试，等待后重试
        if (attempt < MAX_RETRY_ATTEMPTS - 1) {
          await this._waitForRetry(attempt);
        }
      }
    }

    this._logFailureMetrics(perfStart);
    return false; // 所有重试都失败
  }

  /**
   * 准备超时表单数据
   * @private
   */
  _prepareTimeoutFormData(feedbackData) {
    const formData = new FormData();
    formData.append('is_timeout_capture', 'true');
    formData.append('source_event', 'frontend_timeout');

    // 获取CSRF令牌
    const csrfTokenElement = this.uiHandler.getElement('csrfToken', 'csrfToken');
    const csrfToken = csrfTokenElement ? csrfTokenElement.value : '';
    if (csrfToken) {
      formData.append('csrf_token', csrfToken);
    }

    // 添加文本内容（如果有）
    if (feedbackData.text && feedbackData.text.length > 0) {
      formData.append('textFeedback', feedbackData.text);
    }

    // 添加时间戳
    formData.append('timestamp', feedbackData.timestamp);

    // 处理图片数据（如果有）
    if (feedbackData.images && feedbackData.images.length > 0) {
      this.prepareImageDataForUpload(feedbackData.images, formData);
    }

    return formData;
  }

  /**
   * 获取CSRF令牌
   * @private
   */
  _getCsrfToken() {
    const csrfTokenElement = this.uiHandler.getElement('csrfToken', 'csrfToken');
    return csrfTokenElement ? csrfTokenElement.value : '';
  }

  /**
   * 尝试单次提交
   * @private
   */
  async _attemptSubmission(formData, csrfToken, attempt) {
    // 创建带超时控制的fetch请求
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), NETWORK_TIMEOUT);

    const response = await fetch('/submit_feedback', {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken
      },
      body: formData,
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`HTTP错误: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  }

  /**
   * 处理成功提交
   * @private
   */
  _handleSuccessfulSubmission(perfStart) {
    // 成功发送后清除本地备份
    this.backupHandler.clearLocalBackup();
    this.uiHandler.showUserNotification('数据已成功保存', 'success');
  }

  /**
   * 处理提交错误
   * @private
   */
  _handleSubmissionError(error, attempt) {
    // P2.3 修复：在每次失败时显示网络错误提示
    const isNetworkError = this._isNetworkError(error);

    if (isNetworkError) {
      this.uiHandler.showUserNotification(`网络连接失败 (第${attempt + 1}次尝试)`, 'warning');
    } else {
      this.uiHandler.showUserNotification(
        `提交失败: ${error.message} (第${attempt + 1}次尝试)`,
        'error'
      );
    }
  }

  /**
   * 判断是否为网络错误
   * @private
   */
  _isNetworkError(error) {
    return (
      error.name === 'AbortError' ||
      error.message.includes('Failed to fetch') ||
      error.message.includes('NetworkError') ||
      error.message.includes('network')
    );
  }

  /**
   * 等待重试
   * @private
   */
  async _waitForRetry(attempt) {
    const delay = RETRY_DELAYS[attempt];
    await new Promise(resolve => setTimeout(resolve, delay));
  }

  /**
   * 记录失败指标
   * @private
   */
  _logFailureMetrics(perfStart) {
  }

  /**
   * 处理发送失败后的本地备份
   * @param {Object} feedbackData - 需要备份的反馈数据
   */
  handleFailedTimeoutSubmission(feedbackData) {
    if (feedbackData && (feedbackData.text || feedbackData.images.length > 0)) {
      try {
        this.backupHandler.saveToLocalBackup(feedbackData);
        this.uiHandler.showUserNotification('网络连接失败，您的数据已安全保存到本地', 'warning');
      } catch (backupError) {
        this.uiHandler.showUserNotification('数据保存完全失败，请手动复制您的输入内容', 'error');
      }
    } else {
      this.uiHandler.showUserNotification('网络连接失败，但没有数据需要保存', 'info');
    }
  }
}
