/**
 * 建议选项处理模块
 * 负责建议选项的初始化、渲染和交互功能
 */

import { showAlert, autoResizeTextarea } from './utils.js';

/**
 * 初始化建议选项功能
 */
export function initializeSuggestOptions() {
  const suggestDataElement = document.getElementById('suggestData');
  if (!suggestDataElement) return;

  const suggestText = suggestDataElement.textContent.trim();
  if (!suggestText) return;

  try {
    const suggestions = JSON.parse(suggestText);
    if (Array.isArray(suggestions) && suggestions.length > 0) {
      renderSuggestOptions(suggestions);
    }
  } catch (error) {
    console.error('解析建议选项失败:', error);
  }
}

/**
 * 渲染建议选项列表
 * @param {Array<string>} suggestions - 建议选项数组
 */
function renderSuggestOptions(suggestions) {
  const suggestOptions = document.getElementById('suggestOptions');
  const suggestList = document.getElementById('suggestList');

  if (!suggestOptions || !suggestList) return;

  suggestList.innerHTML = '';

  suggestions.forEach((suggestion, index) => {
    const item = document.createElement('div');
    item.className = 'suggest-item';
    item.setAttribute('role', 'option');
    item.setAttribute('tabindex', '0');

    // 创建建议文本元素
    const textDiv = document.createElement('div');
    textDiv.className = 'suggest-text';
    textDiv.textContent = suggestion;
    textDiv.onclick = () => submitSuggestion(suggestion);

    // 创建操作按钮容器
    const actionsDiv = document.createElement('div');
    actionsDiv.className = 'suggest-actions';

    // 创建复制按钮
    const copyBtn = document.createElement('button');
    copyBtn.type = 'button';
    copyBtn.className = 'suggest-btn suggest-btn-copy';
    copyBtn.title = '插入到光标位置';
    copyBtn.setAttribute('aria-label', `将建议"${suggestion}"插入到文本框`);
    copyBtn.textContent = '📋';
    copyBtn.onclick = () => copySuggestion(suggestion);

    // 创建提交按钮
    const submitBtn = document.createElement('button');
    submitBtn.type = 'button';
    submitBtn.className = 'suggest-btn suggest-btn-submit';
    submitBtn.title = '直接提交';
    submitBtn.setAttribute('aria-label', `直接提交建议"${suggestion}"`);
    submitBtn.textContent = '✅';
    submitBtn.onclick = () => submitSuggestion(suggestion);

    // 键盘导航支持
    item.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        submitSuggestion(suggestion);
      }
    });

    // 组装元素
    actionsDiv.appendChild(copyBtn);
    actionsDiv.appendChild(submitBtn);
    item.appendChild(textDiv);
    item.appendChild(actionsDiv);

    suggestList.appendChild(item);
  });

  suggestOptions.style.display = 'block';
}

/**
 * 复制建议文本到输入框的光标位置
 * @param {string} suggestion - 要插入的建议文本
 */
function copySuggestion(suggestion) {
  const textarea = document.getElementById('textFeedback');

  // 验证输入
  if (!_validateCopyInput(textarea, suggestion)) {
    return;
  }

  // 确保文本框获得焦点
  textarea.focus();

  // 获取当前光标位置和文本内容
  const { start, end, currentValue } = _getCursorPosition(textarea);

  // 插入建议文本
  const insertText = _prepareInsertText(suggestion, currentValue, start, end);
  const newValue = _insertTextAtCursor(currentValue, insertText, start, end);

  // 更新文本框内容和光标位置
  _updateTextareaContent(textarea, newValue, start, insertText);

  showAlert('建议已插入到光标位置', 'success');
}

/**
 * 验证复制输入
 * @private
 * @param {HTMLElement} textarea - 文本框元素
 * @param {string} suggestion - 建议文本
 * @returns {boolean} 验证是否通过
 */
function _validateCopyInput(textarea, suggestion) {
  if (!textarea) {
    showAlert('未找到文本输入框', 'warning');
    return false;
  }

  if (!suggestion || typeof suggestion !== 'string') {
    showAlert('无效的建议内容', 'warning');
    return false;
  }

  return true;
}

/**
 * 获取光标位置
 * @private
 * @param {HTMLElement} textarea - 文本框元素
 * @returns {Object} 光标位置信息
 */
function _getCursorPosition(textarea) {
  return {
    start: textarea.selectionStart || 0,
    end: textarea.selectionEnd || 0,
    currentValue: textarea.value || ''
  };
}

/**
 * 准备插入文本（添加必要的空格分隔）
 * @private
 * @param {string} suggestion - 原始建议文本
 * @param {string} currentValue - 当前文本框内容
 * @param {number} start - 光标开始位置
 * @param {number} end - 光标结束位置
 * @returns {string} 准备好的插入文本
 */
function _prepareInsertText(suggestion, currentValue, start, end) {
  let insertText = suggestion;

  // 如果光标前有内容且不是空格，添加空格分隔
  if (_needsSpaceBefore(currentValue, start)) {
    insertText = ' ' + insertText;
  }

  // 如果光标后有内容且不是空格，添加空格分隔
  if (_needsSpaceAfter(currentValue, end)) {
    insertText = insertText + ' ';
  }

  return insertText;
}

/**
 * 检查是否需要在前面添加空格
 * @private
 */
function _needsSpaceBefore(currentValue, start) {
  return start > 0 && currentValue[start - 1] !== ' ' && currentValue[start - 1] !== '\n';
}

/**
 * 检查是否需要在后面添加空格
 * @private
 */
function _needsSpaceAfter(currentValue, end) {
  return end < currentValue.length && currentValue[end] !== ' ' && currentValue[end] !== '\n';
}

/**
 * 在光标位置插入文本
 * @private
 */
function _insertTextAtCursor(currentValue, insertText, start, end) {
  return currentValue.substring(0, start) + insertText + currentValue.substring(end);
}

/**
 * 更新文本框内容和光标位置
 * @private
 */
function _updateTextareaContent(textarea, newValue, start, insertText) {
  textarea.value = newValue;

  // 设置光标位置到插入文本的末尾
  const newCursorPos = start + insertText.length;
  textarea.setSelectionRange(newCursorPos, newCursorPos);

  // 触发输入事件以更新文本框高度
  textarea.dispatchEvent(new Event('input', { bubbles: true }));
  autoResizeTextarea.call(textarea);
}

/**
 * 直接提交建议作为反馈
 * @param {string} suggestion - 要提交的建议文本
 */
export async function submitSuggestion(suggestion) {
  if (!suggestion || typeof suggestion !== 'string') {
    showAlert('无效的建议内容', 'warning');
    return;
  }

  const textarea = document.getElementById('textFeedback');
  if (textarea) {
    // 检查文本框是否为空，如果为空则直接设置，否则询问用户意图
    if (!textarea.value.trim()) {
      textarea.value = suggestion;
      // 触发输入事件以更新文本框高度
      textarea.dispatchEvent(new Event('input', { bubbles: true }));
      autoResizeTextarea.call(textarea);
    } else {
      // 如果有内容，询问用户是要替换还是追加
      const userChoice = confirm(
        '文本框中已有内容。\n\n点击"确定"追加到光标位置\n点击"取消"替换全部内容'
      );

      if (userChoice) {
        // 用户选择追加到光标位置
        copySuggestion(suggestion);
        // 等待插入完成后再提交
        setTimeout(() => {
          const form = document.getElementById('feedbackForm');
          if (form) {
            const event = new Event('submit', { bubbles: true, cancelable: true });
            form.dispatchEvent(event);
          }
        }, 100);
        return; // 提前返回，避免重复提交
      } else {
        // 用户选择替换全部内容
        textarea.value = suggestion;
        // 触发输入事件以更新文本框高度
        textarea.dispatchEvent(new Event('input', { bubbles: true }));
        autoResizeTextarea.call(textarea);
      }
    }
  }

  // 触发表单提交
  const form = document.getElementById('feedbackForm');
  if (form) {
    const event = new Event('submit', { bubbles: true, cancelable: true });
    form.dispatchEvent(event);
  }
}
