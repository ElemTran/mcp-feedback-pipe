/**
 * UI状态管理模块 - 遵循SOLID原则
 * 单一职责：专门处理UI状态更新和用户反馈显示
 * 依赖倒置：依赖抽象的状态接口，而非具体实现
 */

export class UIStatusManager {
    constructor(options = {}) {
        this.elements = {
            connectionStatus: options.connectionStatusId || 'connection-status',
            messageArea: options.messageAreaId || 'message-area'
        };
        
        this.statusClasses = {
            connecting: 'connecting',
            connected: 'connected',
            disconnected: 'disconnected',
            error: 'error'
        };

        this.messageTypes = {
            info: 'info',
            success: 'success',
            warning: 'warning',
            error: 'error'
        };

        this.messageTimeout = options.messageTimeout || 3000;
        this.currentMessageTimer = null;
        
        this.init();
    }

    /**
     * 初始化UI状态管理器
     */
    init() {
        this.validateElements();
    }

    /**
     * 验证必需的DOM元素是否存在
     */
    validateElements() {
        Object.entries(this.elements).forEach(([key, elementId]) => {
            const element = document.getElementById(elementId);
            if (!element) {
                console.warn(`UI元素未找到: ${elementId}`);
            }
        });
    }

    /**
     * 更新连接状态显示
     */
    updateConnectionStatus(status, message) {
        const element = document.getElementById(this.elements.connectionStatus);
        if (!element) return;

        // 清除所有状态类
        Object.values(this.statusClasses).forEach(cls => {
            element.classList.remove(cls);
        });

        // 添加新状态类
        if (this.statusClasses[status]) {
            element.classList.add(this.statusClasses[status]);
        }

        // 更新文本内容
        element.textContent = message || this.getDefaultStatusMessage(status);
        
        console.log(`📊 连接状态更新: ${status} - ${message}`);
    }

    /**
     * 获取默认状态消息
     */
    getDefaultStatusMessage(status) {
        const messages = {
            connecting: '连接中...',
            connected: '已连接',
            disconnected: '已断开',
            error: '连接错误'
        };
        return messages[status] || '未知状态';
    }

    /**
     * 显示消息
     */
    showMessage(message, type = 'info', duration = null) {
        console.log(`[${type.toUpperCase()}] ${message}`);
        
        const element = document.getElementById(this.elements.messageArea);
        if (!element) return;

        // 清除现有消息计时器
        if (this.currentMessageTimer) {
            clearTimeout(this.currentMessageTimer);
        }

        // 创建消息HTML
        const messageHtml = this.createMessageHTML(message, type);
        element.innerHTML = messageHtml;

        // 设置自动清除计时器
        const clearDuration = duration !== null ? duration : this.messageTimeout;
        if (clearDuration > 0) {
            this.currentMessageTimer = setTimeout(() => {
                this.clearMessage();
            }, clearDuration);
        }
    }

    /**
     * 创建消息HTML
     */
    createMessageHTML(message, type) {
        const iconMap = {
            info: 'ℹ️',
            success: '✅',
            warning: '⚠️',
            error: '❌'
        };

        const icon = iconMap[type] || iconMap.info;
        return `<div class="message ${type}">${icon} ${message}</div>`;
    }

    /**
     * 清除消息
     */
    clearMessage() {
        const element = document.getElementById(this.elements.messageArea);
        if (element) {
            element.innerHTML = '';
        }
        
        if (this.currentMessageTimer) {
            clearTimeout(this.currentMessageTimer);
            this.currentMessageTimer = null;
        }
    }

    /**
     * 显示成功消息
     */
    showSuccess(message, duration = null) {
        this.showMessage(message, this.messageTypes.success, duration);
    }

    /**
     * 显示错误消息
     */
    showError(message, duration = null) {
        this.showMessage(message, this.messageTypes.error, duration);
    }

    /**
     * 显示警告消息
     */
    showWarning(message, duration = null) {
        this.showMessage(message, this.messageTypes.warning, duration);
    }

    /**
     * 显示信息消息
     */
    showInfo(message, duration = null) {
        this.showMessage(message, this.messageTypes.info, duration);
    }

    /**
     * 设置按钮状态
     */
    setButtonState(buttonId, state, text = null) {
        const button = document.getElementById(buttonId);
        if (!button) return;

        // 移除所有状态类
        button.classList.remove('loading', 'disabled', 'success', 'error');
        
        // 添加新状态类
        if (state !== 'normal') {
            button.classList.add(state);
        }

        // 更新文本
        if (text) {
            button.textContent = text;
        }

        // 设置disabled属性
        button.disabled = (state === 'loading' || state === 'disabled');
    }

    /**
     * 更新提交按钮状态
     */
    updateSubmitButton(state) {
        const states = {
            ready: { text: '✅ 提交反馈', class: 'normal' },
            submitting: { text: '📤 提交中...', class: 'loading' },
            success: { text: '✅ 提交成功', class: 'success' },
            error: { text: '❌ 提交失败', class: 'error' },
            offline: { text: '📡 离线状态', class: 'disabled' }
        };

        const config = states[state];
        if (config) {
            this.setButtonState('submitBtn', config.class, config.text);
        }
    }

    /**
     * 显示加载状态
     */
    showLoading(message = '处理中...') {
        this.showMessage(message, 'info', 0); // 0表示不自动清除
    }

    /**
     * 隐藏加载状态
     */
    hideLoading() {
        this.clearMessage();
    }

    /**
     * 批量更新UI状态
     */
    updateBatchStatus(updates) {
        Object.entries(updates).forEach(([method, args]) => {
            if (typeof this[method] === 'function') {
                this[method](...(Array.isArray(args) ? args : [args]));
            }
        });
    }

    /**
     * 重置所有UI状态
     */
    reset() {
        this.updateConnectionStatus('disconnected');
        this.clearMessage();
        this.updateSubmitButton('offline');
    }
} 