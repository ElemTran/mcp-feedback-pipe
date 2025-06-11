/**
 * 表单处理模块
 * 负责表单提交、UI控制和用户交互功能
 */

import { showAlert, autoResizeTextarea } from './utils.js';
import { getSelectedImages, hasSelectedImages } from './image-handler.js';

// 全局标志位：标记反馈是否已成功提交
let isFeedbackSuccessfullySubmitted = false;

/**
 * 设置反馈成功提交标志位
 * @param {boolean} value - 标志位值
 */
export function setFeedbackSuccessfullySubmitted(value) {
  isFeedbackSuccessfullySubmitted = value;
}

/**
 * 获取反馈成功提交标志位
 * @returns {boolean} 标志位值
 */
export function getFeedbackSuccessfullySubmitted() {
  return isFeedbackSuccessfullySubmitted;
}

/**
 * 初始化表单处理相关的事件监听器
 */
export function initializeFormHandlers() {
  const form = document.getElementById('feedbackForm');
  const textarea = document.getElementById('textFeedback');

  if (form) {
    form.addEventListener('submit', handleSubmit);
  }

  if (textarea) {
    textarea.classList.add('auto-resize');
    textarea.addEventListener('input', autoResizeTextarea);
    // 初始调整
    autoResizeTextarea.call(textarea);
  }
}

/**
 * 处理表单提交
 * @param {Event} e - 提交事件
 */
async function handleSubmit(e) {
  e.preventDefault();

  // 验证表单数据
  const validationResult = _validateFormData();
  if (!validationResult.isValid) {
    showAlert(validationResult.message, 'warning');
    return;
  }

  const submitBtn = document.getElementById('submitBtn');
  const originalText = submitBtn.innerHTML;
  _setSubmitButtonLoading(submitBtn);

  try {
    const formData = _prepareFormData(validationResult.data);
    const result = await _submitFormData(formData);

    if (result.success) {
      await _handleSubmissionSuccess();
    } else {
      showAlert('提交失败：' + (result.message || '未知错误'), 'warning');
    }
  } catch (error) {
    showAlert('提交失败：' + (error.message || '网络错误'), 'warning');
  } finally {
    _resetSubmitButton(submitBtn, originalText);
  }
}

/**
 * 验证表单数据
 * @private
 * @returns {Object} 验证结果对象
 */
function _validateFormData() {
  const textFeedback = document.getElementById('textFeedback').value.trim();
  const hasText = textFeedback.length > 0;
  const hasImages = hasSelectedImages();

  if (!hasText && !hasImages) {
    return {
      isValid: false,
      message: '请至少提供文字反馈或图片反馈'
    };
  }

  return {
    isValid: true,
    data: {
      textFeedback,
      hasText,
      images: getSelectedImages()
    }
  };
}

/**
 * 设置提交按钮为加载状态
 * @private
 */
function _setSubmitButtonLoading(submitBtn) {
  submitBtn.innerHTML = '<span class="loading"></span>提交中...';
  submitBtn.disabled = true;
  submitBtn.setAttribute('aria-busy', 'true');
}

/**
 * 重置提交按钮状态
 * @private
 */
function _resetSubmitButton(submitBtn, originalText) {
  submitBtn.innerHTML = originalText;
  submitBtn.disabled = false;
  submitBtn.removeAttribute('aria-busy');
}

/**
 * 准备表单数据
 * @private
 * @param {Object} data - 表单数据
 * @returns {FormData} 准备好的FormData对象
 */
function _prepareFormData(data) {
  const formData = new FormData();

  // 添加CSRF令牌
  const csrfToken = document.getElementById('csrfToken').value;
  if (csrfToken) {
    formData.append('csrf_token', csrfToken);
  }

  // 添加文本反馈
  if (data.hasText) {
    formData.append('textFeedback', data.textFeedback);
  }

  // 添加时间戳
  formData.append('timestamp', new Date().toISOString());

  // 添加图片文件
  _addImagesToFormData(formData, data.images);

  return formData;
}

/**
 * 添加图片到FormData
 * @private
 */
function _addImagesToFormData(formData, images) {
  for (let i = 0; i < images.length; i++) {
    const imageData = images[i];
    const file = _convertImageDataToFile(imageData, i);
    formData.append('images', file);
  }
}

/**
 * 将图片数据转换为File对象
 * @private
 */
function _convertImageDataToFile(imageData, index) {
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
  const fileName = imageData.name || `image_${index}${extension}`;

  return new File([blob], fileName, { type: mimeType });
}

/**
 * 提交表单数据
 * @private
 * @param {FormData} formData - 要提交的表单数据
 * @returns {Promise<Object>} 提交结果
 */
async function _submitFormData(formData) {
  const response = await fetch('/submit_feedback', {
    method: 'POST',
    body: formData
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * 处理提交成功
 * @private
 */
async function _handleSubmissionSuccess() {
  showAlert('反馈提交成功！感谢您的反馈。', 'success');

  // 设置反馈成功提交标志位
  setFeedbackSuccessfullySubmitted(true);

  // 停止倒计时
  if (window.MCPFeedback && window.MCPFeedback.stopCountdown) {
    window.MCPFeedback.stopCountdown();
  }

  setTimeout(() => {
    window.close();
  }, 2000);
}

/**
 * 切换汇报区域大小
 */
export function toggleReportSize() {
  const reportSection = document.querySelector('.work-report-section');
  const feedbackForm = document.getElementById('feedbackForm');
  const toggleBtn = document.getElementById('toggleReportBtn');

  if (reportSection.classList.contains('maximized')) {
    // 恢复默认大小
    reportSection.classList.remove('maximized');
    feedbackForm.style.display = 'block';
    toggleBtn.innerHTML = '📏 调整大小';
    toggleBtn.setAttribute('aria-label', '最大化汇报区域');
  } else {
    // 最大化汇报区域
    reportSection.classList.add('maximized');
    feedbackForm.style.display = 'none';
    toggleBtn.innerHTML = '📏 恢复大小';
    toggleBtn.setAttribute('aria-label', '恢复汇报区域大小');
  }
}

/**
 * 切换反馈输入区域
 */
export function toggleFeedbackSize() {
  const feedbackContent = document.getElementById('feedbackContent');
  const textarea = document.getElementById('textFeedback');

  if (feedbackContent.style.display === 'none') {
    feedbackContent.style.display = 'block';
    textarea.focus();
  } else {
    feedbackContent.style.display = 'none';
  }
}

/**
 * 切换图片上传区域
 */
export function toggleImageSection() {
  const imageContent = document.getElementById('imageContent');

  if (imageContent.style.display === 'none') {
    imageContent.style.display = 'block';
  } else {
    imageContent.style.display = 'none';
  }
}
