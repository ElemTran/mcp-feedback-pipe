/**
 * 反馈通道主入口文件
 * 整合所有模块，遵循单一职责原则
 */

// 导入所有模块
import { initializeGlobalErrorHandling, startServerHealthCheck } from './modules/error-handler.js';
import {
  initializeMarkdownRendering,
  initializeMermaid,
  updateWorkSummary
} from './modules/markdown-renderer.js';
import { initializeImageHandlers } from './modules/image-handler.js';
import { initializeSuggestOptions, submitSuggestion } from './modules/suggestion-handler.js';
import {
  initializeFormHandlers,
  toggleReportSize,
  toggleFeedbackSize,
  toggleImageSection,
  getFeedbackSuccessfullySubmitted
} from './modules/form-handler.js';
import {
  initializeTimeoutHandler,
  stopCountdown,
  getRemainingTime
} from './timeout/index.js';

// 使用命名空间模式避免全局变量污染
window.MCPFeedback = {
  toggleReportSize,
  toggleFeedbackSize,
  toggleImageSection,
  submitSuggestion,
  updateWorkSummary,
  stopCountdown,
  getRemainingTime
};

// 页面加载完成后初始化所有模块
document.addEventListener('DOMContentLoaded', function () {
  console.log('🎯 MCP反馈通道初始化开始...');

  try {
    // 1. 初始化错误处理
    initializeGlobalErrorHandling();
    console.log('✅ 错误处理模块初始化完成');

    // 2. 初始化Mermaid图表库
    initializeMermaid();
    console.log('✅ Mermaid图表库初始化完成');

    // 3. 初始化Markdown渲染（修复渲染问题）
    initializeMarkdownRendering();
    console.log('✅ Markdown渲染模块初始化完成');

    // 4. 初始化图片处理
    initializeImageHandlers();
    console.log('✅ 图片处理模块初始化完成');

    // 5. 初始化建议选项
    initializeSuggestOptions();
    console.log('✅ 建议选项模块初始化完成');

    // 6. 初始化表单处理
    initializeFormHandlers();
    console.log('✅ 表单处理模块初始化完成');

    // 7. 初始化超时处理
    initializeTimeoutHandler();
    console.log('✅ 超时处理模块初始化完成');

    // 8. 启动服务器健康检查
    startServerHealthCheck();
    console.log('✅ 服务器健康检查启动完成');

    console.log('🎉 MCP反馈通道初始化完成！');

    // 9. 初始化窗口关闭处理
    initializeWindowCloseHandler();
    console.log('✅ 窗口关闭处理初始化完成');
  } catch (error) {
    console.error('❌ 初始化过程中出现错误:', error);
  }
});

/**
 * 初始化窗口关闭处理
 * 在窗口关闭时通知后端释放资源
 */
function initializeWindowCloseHandler() {
  window.addEventListener('beforeunload', function (event) {
    // 检查反馈是否已成功提交，如果已提交则不再发送session_closed通知
    if (getFeedbackSuccessfullySubmitted()) {
      console.debug('反馈已成功提交，无需发送窗口关闭通知');
      return;
    }

    // 发送会话关闭通知到后端
    try {
      fetch('/submit_feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          status: 'session_closed'
        }),
        keepalive: true // 确保在页面卸载时请求仍能发送
      }).catch(() => {
        // 忽略发送失败的情况，按要求设计
        console.debug('窗口关闭通知发送失败（忽略）');
      });
    } catch (error) {
      // 忽略任何错误，确保不影响正常的页面关闭流程
      console.debug('窗口关闭处理出错（忽略）:', error);
    }
  });
}
