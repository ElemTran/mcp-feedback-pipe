/**
 * 工具函数模块
 * 提供通用的工具函数，如防抖、图片压缩、HTML转义等
 */

/**
 * 防抖函数 - 限制函数调用频率
 * @param {Function} func - 要防抖的函数
 * @param {number} wait - 等待时间（毫秒）
 * @returns {Function} 防抖后的函数
 */
export function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * 压缩图片文件
 * @param {File} file - 原始图片文件
 * @param {number} maxWidth - 最大宽度
 * @param {number} quality - 压缩质量 (0-1)
 * @returns {Promise<Blob>} 压缩后的图片Blob
 */
export function compressImage(file, maxWidth = 1920, quality = 0.8) {
    return new Promise((resolve, reject) => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const img = new Image();
        
        img.onload = () => {
            try {
                const ratio = Math.min(maxWidth / img.width, maxWidth / img.height, 1);
                canvas.width = img.width * ratio;
                canvas.height = img.height * ratio;
                
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                canvas.toBlob(resolve, 'image/jpeg', quality);
            } catch (error) {
                console.error('图片压缩失败:', error);
                resolve(file); // 压缩失败时返回原文件
            }
        };
        
        img.onerror = () => {
            console.error('图片加载失败');
            resolve(file); // 加载失败时返回原文件
        };
        
        img.src = URL.createObjectURL(file);
    });
}

/**
 * HTML转义防止XSS攻击
 * @param {string} text - 要转义的文本
 * @returns {string} 转义后的HTML
 */
export function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * 显示提示消息
 * @param {string} message - 消息内容
 * @param {string} type - 消息类型 (success, warning, info, danger)
 */
export function showAlert(message, type) {
    const existingAlert = document.querySelector('.alert');
    if (existingAlert) {
        existingAlert.remove();
    }
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    alert.setAttribute('role', 'alert');
    alert.setAttribute('aria-live', 'polite');
    
    const content = document.querySelector('.content');
    content.insertBefore(alert, content.firstChild);
    
    // 自动消失，但成功消息保持更长时间
    const timeout = type === 'success' ? 3000 : 5000;
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, timeout);
}

/**
 * 自动调整文本框高度
 */
export function autoResizeTextarea() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 300) + 'px';
} 