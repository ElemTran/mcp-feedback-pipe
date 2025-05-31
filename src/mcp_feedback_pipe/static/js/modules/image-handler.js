/**
 * 图片处理模块
 * 负责图片上传、压缩、预览、拖拽等功能
 */

import { compressImage, showAlert } from './utils.js';

// 全局变量存储选中的图片
let selectedImages = [];

/**
 * 初始化图片处理相关的事件监听器
 */
export function initializeImageHandlers() {
    const uploadBtn = document.getElementById('uploadBtn');
    const fileInput = document.getElementById('fileInput');
    const textFeedback = document.getElementById('textFeedback');
    
    if (uploadBtn && fileInput) {
        uploadBtn.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', handleFileSelect);
    }
    
    if (textFeedback) {
        // 文本框拖拽上传
        textFeedback.addEventListener('dragover', handleDragOver);
        textFeedback.addEventListener('drop', handleDrop);
        textFeedback.addEventListener('dragleave', handleDragLeave);
        
        // 文本框粘贴图片
        textFeedback.addEventListener('paste', handlePaste);
    }
}

/**
 * 处理文件选择
 * @param {Event} e - 文件选择事件
 */
function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    files.forEach(file => {
        if (file.type.startsWith('image/')) {
            addImage(file);
        } else {
            showAlert(`文件 "${file.name}" 不是图片格式，已跳过`, 'warning');
        }
    });
}

/**
 * 处理拖拽悬停
 * @param {Event} e - 拖拽事件
 */
function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.style.backgroundColor = '#f0f4ff';
    e.currentTarget.style.borderColor = '#667eea';
}

/**
 * 处理拖拽离开
 * @param {Event} e - 拖拽事件
 */
function handleDragLeave(e) {
    e.currentTarget.style.backgroundColor = '';
    e.currentTarget.style.borderColor = '';
}

/**
 * 处理拖拽放置
 * @param {Event} e - 拖拽事件
 */
function handleDrop(e) {
    e.preventDefault();
    e.currentTarget.style.backgroundColor = '';
    e.currentTarget.style.borderColor = '';
    
    const files = Array.from(e.dataTransfer.files);
    files.forEach(file => {
        if (file.type.startsWith('image/')) {
            addImage(file, '拖拽');
        } else {
            showAlert(`文件 "${file.name}" 不是图片格式，已跳过`, 'warning');
        }
    });
}

/**
 * 处理粘贴事件
 * @param {Event} e - 粘贴事件
 */
function handlePaste(e) {
    const items = Array.from(e.clipboardData.items);
    let hasImage = false;
    
    items.forEach(item => {
        if (item.type.startsWith('image/')) {
            e.preventDefault(); // 阻止默认粘贴行为
            const file = item.getAsFile();
            if (file) {
                addImage(file, '粘贴');
                hasImage = true;
            }
        }
    });
    
    if (hasImage) {
        showAlert('图片已添加到反馈中', 'success');
    }
}

/**
 * 添加图片到反馈中（包含压缩和验证）
 * @param {File} file - 图片文件
 * @param {string} source - 图片来源
 */
async function addImage(file, source = '文件') {
    // 文件大小检查
    const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
    if (file.size > MAX_FILE_SIZE) {
        showAlert('图片文件过大，请选择小于10MB的图片', 'warning');
        return;
    }
    
    // 文件类型检查
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
        showAlert('不支持的图片格式，请选择 JPEG、PNG、GIF 或 WebP 格式', 'warning');
        return;
    }
    
    try {
        // 显示压缩进度
        showAlert('正在处理图片...', 'info');
        
        // 压缩图片
        const compressedFile = await compressImage(file);
        
        const reader = new FileReader();
        reader.onload = function(e) {
            const imageData = {
                data: e.target.result,
                source: source,
                name: file.name || '粘贴图片',
                size: compressedFile.size || file.size,
                originalSize: file.size
            };
            
            selectedImages.push(imageData);
            updateImagePreview();
            
            // 显示压缩结果
            const compressionRatio = ((file.size - (compressedFile.size || file.size)) / file.size * 100).toFixed(1);
            if (compressionRatio > 0) {
                showAlert(`图片已添加并压缩 ${compressionRatio}%`, 'success');
            } else {
                showAlert('图片已添加', 'success');
            }
        };
        
        reader.onerror = function() {
            showAlert('图片读取失败，请重试', 'warning');
        };
        
        reader.readAsDataURL(compressedFile);
        
    } catch (error) {
        console.error('图片处理失败:', error);
        showAlert('图片处理失败，请重试', 'warning');
    }
}

/**
 * 更新图片预览区域
 */
function updateImagePreview() {
    const preview = document.getElementById('imagePreview');
    if (!preview) return;
    
    preview.innerHTML = '';
    
    selectedImages.forEach((img, index) => {
        const item = document.createElement('div');
        item.className = 'image-item';
        
        // 使用DOM操作替代innerHTML提升安全性
        const imgElement = document.createElement('img');
        imgElement.src = img.data;
        imgElement.alt = img.name;
        imgElement.loading = 'lazy'; // 懒加载优化
        
        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'image-remove';
        removeBtn.textContent = '×';
        removeBtn.setAttribute('aria-label', `删除图片 ${img.name}`);
        removeBtn.onclick = () => removeImage(index);
        
        item.appendChild(imgElement);
        item.appendChild(removeBtn);
        preview.appendChild(item);
    });
}

/**
 * 删除指定索引的图片
 * @param {number} index - 图片索引
 */
function removeImage(index) {
    if (index >= 0 && index < selectedImages.length) {
        selectedImages.splice(index, 1);
        updateImagePreview();
        showAlert('图片已删除', 'info');
    }
}

/**
 * 获取选中的图片数据
 * @returns {Array} 图片数据数组
 */
export function getSelectedImages() {
    return selectedImages.map(img => ({
        data: img.data,
        source: img.source,
        name: img.name,
        size: img.size,
        originalSize: img.originalSize
    }));
}

/**
 * 检查是否有选中的图片
 * @returns {boolean} 是否有图片
 */
export function hasSelectedImages() {
    return selectedImages.length > 0;
}

/**
 * 清空选中的图片
 */
export function clearSelectedImages() {
    selectedImages = [];
    updateImagePreview();
} 