/**
 * 错误处理模块
 * 负责全局错误处理、服务器连接检查等功能
 */

import { debounce, showAlert } from './utils.js';

/**
 * 全局错误处理初始化
 */
export function initializeGlobalErrorHandling() {
    // 全局JavaScript错误处理
    window.addEventListener('error', (event) => {
        console.error('全局错误:', event.error);
        showAlert('应用出现错误，请刷新页面重试', 'warning');
    });

    // 未处理的Promise拒绝
    window.addEventListener('unhandledrejection', (event) => {
        console.error('未处理的Promise拒绝:', event.reason);
        showAlert('网络请求失败，请检查连接', 'warning');
        event.preventDefault(); // 阻止默认的控制台错误输出
    });
}

/**
 * 防抖的服务器连接检查
 */
const debouncedPing = debounce(async () => {
    try {
        const response = await fetch('/ping', {
            method: 'GET',
            timeout: 5000
        });
        if (!response.ok) {
            throw new Error('服务器响应异常');
        }
    } catch (error) {
        console.warn('服务器连接检查失败:', error);
        showAlert('与服务器连接可能中断，请检查网络', 'warning');
    }
}, 30000);

/**
 * 启动定期服务器连接检查
 */
export function startServerHealthCheck() {
    // 启动定期连接检查
    setInterval(debouncedPing, 60000); // 每分钟检查一次
} 