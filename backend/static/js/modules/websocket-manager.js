/**
 * WebSocket管理模块 - 遵循SOLID原则
 * 单一职责：专门处理WebSocket连接和通信
 * 开闭原则：通过事件系统支持扩展，对修改关闭
 */

export class WebSocketManager {
    constructor(options = {}) {
        // 连接配置
        this.config = {
            reconnectAttempts: options.maxReconnectAttempts || 5,
            reconnectDelay: options.initialReconnectDelay || 1000,
            maxReconnectDelay: options.maxReconnectDelay || 30000,
            heartbeatInterval: options.heartbeatInterval || 30000,
            connectionTimeout: options.connectionTimeout || 20000,
            ...options
        };

        // 连接状态
        this.socket = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.heartbeatTimer = null;
        this.clientId = null;

        // 事件处理器（依赖注入）
        this.eventHandlers = new Map();
        
        // 初始化
        this.init();
    }

    /**
     * 初始化WebSocket管理器
     */
    init() {
        this.setupPageHandlers();
        this.connect();
    }

    /**
     * 建立WebSocket连接
     */
    connect() {
        if (this.isConnected || !window.io) {
            return;
        }

        try {
            console.log('🔗 建立WebSocket连接...');
            
            this.socket = io({
                transports: ['websocket', 'polling'],
                timeout: this.config.connectionTimeout,
                forceNew: true,
                autoConnect: true
            });

            this.setupSocketEvents();

        } catch (error) {
            console.error('❌ WebSocket连接失败:', error);
            this.handleConnectionError(error);
        }
    }

    /**
     * 设置Socket事件处理器
     */
    setupSocketEvents() {
        // 连接成功
        this.socket.on('connect', () => {
            this.isConnected = true;
            this.reconnectAttempts = 0;
            
            console.log('✅ WebSocket连接已建立');
            this.emit('connected');
        });

        // 连接确认
        this.socket.on('connection_established', (data) => {
            this.clientId = data.client_id;
            
            console.log('🎯 连接确认:', data);
            
            // 启动心跳
            this.startHeartbeat();
            this.emit('ready', data);
        });

        // 断开连接
        this.socket.on('disconnect', (reason) => {
            this.handleDisconnection(reason);
        });

        // 心跳响应
        this.socket.on('heartbeat_response', (data) => {
            this.emit('heartbeat', data);
        });

        // 反馈接收确认
        this.socket.on('feedback_received', (data) => {
            this.emit('feedback_received', data);
        });

        // 连接错误
        this.socket.on('connect_error', (error) => {
            console.error('🚫 WebSocket连接错误:', error);
            this.handleConnectionError(error);
        });
    }

    /**
     * 处理连接断开
     */
    handleDisconnection(reason) {
        this.isConnected = false;
        this.stopHeartbeat();
        
        console.log('💔 WebSocket连接断开:', reason);
        this.emit('disconnected', reason);

        // 自动重连（除非是主动断开）
        if (reason !== 'io client disconnect') {
            this.scheduleReconnect();
        }
    }

    /**
     * 处理连接错误
     */
    handleConnectionError(error) {
        this.emit('error', error);
        this.scheduleReconnect();
    }

    /**
     * 计划重连
     */
    scheduleReconnect() {
        if (this.reconnectAttempts >= this.config.reconnectAttempts) {
            console.error('❌ 达到最大重连次数');
            this.emit('max_reconnect_reached');
            return;
        }

        this.reconnectAttempts++;
        const delay = Math.min(
            this.config.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1),
            this.config.maxReconnectDelay
        );

        console.log(`🔄 ${delay}ms后重连... (第${this.reconnectAttempts}次)`);

        setTimeout(() => {
            if (!this.isConnected) {
                this.connect();
            }
        }, delay);
    }

    /**
     * 启动心跳
     */
    startHeartbeat() {
        this.stopHeartbeat();
        
        this.heartbeatTimer = setInterval(() => {
            if (this.isConnected && this.socket) {
                this.socket.emit('heartbeat', {
                    client_id: this.clientId,
                    timestamp: Date.now(),
                    page_url: window.location.href
                });
            }
        }, this.config.heartbeatInterval);

        console.log(`💓 心跳已启动，间隔: ${this.config.heartbeatInterval}ms`);
    }

    /**
     * 停止心跳
     */
    stopHeartbeat() {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }
    }

    /**
     * 提交反馈数据
     */
    submitFeedback(feedbackData) {
        if (!this.isConnected || !this.socket) {
            throw new Error('WebSocket未连接');
        }

        return new Promise((resolve, reject) => {
            try {
                this.socket.emit('submit_feedback', {
                    text: feedbackData.text || '',
                    images: feedbackData.images || [],
                    user_agent: navigator.userAgent,
                    timestamp: Date.now(),
                    client_id: this.clientId
                });

                console.log('📤 反馈已通过WebSocket提交');
                resolve(true);

            } catch (error) {
                console.error('❌ WebSocket提交反馈失败:', error);
                reject(error);
            }
        });
    }

    /**
     * 设置页面处理器
     */
    setupPageHandlers() {
        // 页面卸载时断开连接
        window.addEventListener('beforeunload', () => {
            this.disconnect();
        });

        // 页面可见性变化
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.stopHeartbeat();
            } else if (this.isConnected) {
                this.startHeartbeat();
            }
        });
    }

    /**
     * 断开连接
     */
    disconnect() {
        this.stopHeartbeat();
        
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
        }
        
        this.isConnected = false;
        console.log('🚪 WebSocket已主动断开');
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
                console.error(`事件处理器错误 [${event}]:`, error);
            }
        });
    }

    /**
     * 获取连接状态
     */
    getStatus() {
        return {
            connected: this.isConnected,
            clientId: this.clientId,
            reconnectAttempts: this.reconnectAttempts
        };
    }

    /**
     * 检查是否可以提交反馈
     */
    canSubmitFeedback() {
        return this.isConnected && this.socket && this.clientId;
    }
} 