/**
 * 应用配置常量
 * 用于集中管理超时处理模块的配置参数
 */

// 用户活动监控配置
export const INACTIVITY_THRESHOLD = 60000; // 1分钟不活动则暂停倒计时 (毫秒)

// 超时验证配置
export const MIN_CUSTOM_TIMEOUT = 30; // 自定义超时的最小值 (秒)
export const DEFAULT_TIMEOUT_SECONDS = 300; // 默认超时时间 (秒，5分钟)

// 网络重试配置
export const MAX_RETRY_ATTEMPTS = 3; // 最大重试次数
export const NETWORK_TIMEOUT = 10000; // 网络请求超时时间 (毫秒)
export const RETRY_DELAYS = [1000, 2000, 4000]; // 重试延迟数组：指数退避 (毫秒)

// UI 更新配置
export const COUNTDOWN_UPDATE_INTERVAL = 1000; // 倒计时更新间隔 (毫秒)

// 进度条和样式配置
export const DANGER_THRESHOLD = 30; // 危险状态阈值 (秒)
export const WARNING_THRESHOLD = 60; // 警告状态阈值 (秒)

// 本地存储配置
export const MAX_LOCAL_BACKUPS = 10; // 最大本地备份数量

// 通知配置
export const NOTIFICATION_AUTO_HIDE_DELAY = 5000; // 通知自动隐藏延迟 (毫秒)
