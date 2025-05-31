/**
 * 表单处理模块
 * 负责表单提交、UI控制和用户交互功能
 */

import { showAlert, autoResizeTextarea } from './utils.js';
import { getSelectedImages, hasSelectedImages } from './image-handler.js';

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
    
    const textFeedback = document.getElementById('textFeedback').value.trim();
    const hasText = textFeedback.length > 0;
    const hasImages = hasSelectedImages();
    
    if (!hasText && !hasImages) {
        showAlert('请至少提供文字反馈或图片反馈', 'warning');
        return;
    }
    
    const submitBtn = document.getElementById('submitBtn');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<span class="loading"></span>提交中...';
    submitBtn.disabled = true;
    submitBtn.setAttribute('aria-busy', 'true');
    
    try {
        const response = await fetch('/submit_feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                textFeedback: hasText ? textFeedback : null,
                images: getSelectedImages(),
                timestamp: new Date().toISOString()
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('反馈提交成功！感谢您的反馈。', 'success');
            setTimeout(() => {
                window.close();
            }, 2000);
        } else {
            showAlert('提交失败：' + (result.message || '未知错误'), 'warning');
        }
    } catch (error) {
        console.error('提交失败:', error);
        showAlert('提交失败：' + (error.message || '网络错误'), 'warning');
    } finally {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
        submitBtn.removeAttribute('aria-busy');
    }
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