/**
 * 超时管理模块 - 遵循SOLID原则
 * 单一职责：专门处理前端超时倒计时和相关事件
 * 开闭原则：通过事件系统支持扩展，对修改关闭
 */

export class TimeoutManager {
    constructor(config = {}) {
        // 超时配置
        this.config = {
            timeout_seconds: config.timeout_seconds || 300,
            warning_threshold: config.warning_threshold || 30,
            server_time: config.server_time || null,
            ...config
        };

        // 时间状态
        this.remainingSeconds = this.config.timeout_seconds;
        this.startTime = Date.now();
        this.serverTimeOffset = 0;
        this.countdownInterval = null;
        this.isRunning = false;
        this.hasWarned = false;

        // 事件处理器
        this.eventHandlers = new Map();

        // 计算服务器时间偏移（如果提供了服务器时间）
        if (this.config.server_time) {
            this.calculateServerTimeOffset(this.config.server_time);
        }
    }

    /**
     * 计算服务器时间偏移量，用于时间同步
     */
    calculateServerTimeOffset(serverTime) {
        const serverTimestamp = new Date(serverTime).getTime();
        const clientTimestamp = Date.now();
        this.serverTimeOffset = serverTimestamp - clientTimestamp;
        
        console.log(`⏰ 服务器时间同步: 偏移 ${this.serverTimeOffset}ms`);
    }

    /**
     * 获取同步后的当前时间
     */
    getCurrentTime() {
        return Date.now() + this.serverTimeOffset;
    }

    /**
     * 开始超时倒计时
     */
    start() {
        if (this.isRunning) {
            console.warn('⚠️ 超时管理器已在运行中');
            return;
        }

        this.isRunning = true;
        this.startTime = this.getCurrentTime();
        this.remainingSeconds = this.config.timeout_seconds;
        this.hasWarned = false;

        console.log(`⏱️ 超时倒计时开始: ${this.config.timeout_seconds}秒`);
        
        // 启动倒计时
        this.countdownInterval = setInterval(() => {
            this.updateCountdown();
        }, 1000);

        // 触发开始事件
        this.emit('started', {
            timeout_seconds: this.config.timeout_seconds,
            remaining_seconds: this.remainingSeconds
        });
    }

    /**
     * 停止超时倒计时
     */
    stop() {
        if (!this.isRunning) {
            return;
        }

        this.isRunning = false;
        
        if (this.countdownInterval) {
            clearInterval(this.countdownInterval);
            this.countdownInterval = null;
        }

        console.log('⏹️ 超时倒计时已停止');
        
        // 触发停止事件
        this.emit('stopped', {
            remaining_seconds: this.remainingSeconds
        });
    }

    /**
     * 更新倒计时
     */
    updateCountdown() {
        if (!this.isRunning) {
            return;
        }

        const currentTime = this.getCurrentTime();
        const elapsedSeconds = Math.floor((currentTime - this.startTime) / 1000);
        this.remainingSeconds = Math.max(0, this.config.timeout_seconds - elapsedSeconds);

        // 触发倒计时更新事件
        this.emit('countdown_update', {
            remaining_seconds: this.remainingSeconds,
            elapsed_seconds: elapsedSeconds,
            total_seconds: this.config.timeout_seconds
        });

        // 检查是否需要发出警告
        if (!this.hasWarned && this.remainingSeconds <= this.config.warning_threshold && this.remainingSeconds > 0) {
            this.hasWarned = true;
            this.emit('warning', {
                remaining_seconds: this.remainingSeconds,
                warning_threshold: this.config.warning_threshold
            });
            console.log(`⚠️ 倒计时警告: 剩余 ${this.remainingSeconds} 秒`);
        }

        // 检查是否超时
        if (this.remainingSeconds <= 0) {
            this.handleTimeout();
        }
    }

    /**
     * 处理超时事件
     */
    handleTimeout() {
        this.stop();
        
        console.log('⏰ 倒计时超时');
        
        // 触发超时事件
        this.emit('timeout', {
            timeout_seconds: this.config.timeout_seconds,
            server_time_offset: this.serverTimeOffset
        });
    }

    /**
     * 重置倒计时
     */
    reset(newConfig = null) {
        this.stop();
        
        if (newConfig) {
            this.config = { ...this.config, ...newConfig };
        }
        
        this.remainingSeconds = this.config.timeout_seconds;
        this.hasWarned = false;
        
        console.log(`🔄 倒计时已重置: ${this.config.timeout_seconds}秒`);
        
        // 触发重置事件
        this.emit('reset', {
            timeout_seconds: this.config.timeout_seconds
        });
    }

    /**
     * 格式化剩余时间为可读字符串
     */
    formatRemainingTime() {
        if (this.remainingSeconds <= 0) {
            return '已超时';
        }
        
        const minutes = Math.floor(this.remainingSeconds / 60);
        const seconds = this.remainingSeconds % 60;
        return `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }

    /**
     * 获取当前状态
     */
    getStatus() {
        return {
            is_running: this.isRunning,
            remaining_seconds: this.remainingSeconds,
            has_warned: this.hasWarned,
            formatted_time: this.formatRemainingTime(),
            server_time_offset: this.serverTimeOffset
        };
    }

    /**
     * 事件系统 - 注册事件处理器
     */
    on(event, handler) {
        if (!this.eventHandlers.has(event)) {
            this.eventHandlers.set(event, []);
        }
        this.eventHandlers.get(event).push(handler);
    }

    /**
     * 移除事件处理器
     */
    off(event, handler) {
        if (!this.eventHandlers.has(event)) return;
        
        const handlers = this.eventHandlers.get(event);
        const index = handlers.indexOf(handler);
        if (index > -1) {
            handlers.splice(index, 1);
        }
    }

    /**
     * 触发事件
     */
    emit(event, data) {
        if (!this.eventHandlers.has(event)) return;
        
        this.eventHandlers.get(event).forEach(handler => {
            try {
                handler(data);
            } catch (error) {
                console.error(`超时管理器事件处理器错误 [${event}]:`, error);
            }
        });
    }

    /**
     * 清理资源
     */
    destroy() {
        this.stop();
        this.eventHandlers.clear();
        console.log('🧹 超时管理器资源已清理');
    }
}