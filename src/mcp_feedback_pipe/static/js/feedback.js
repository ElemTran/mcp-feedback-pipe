// 反馈通道前端脚本
let selectedImages = [];

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
});

function initializeEventListeners() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const pasteArea = document.getElementById('pasteArea');
    const form = document.getElementById('feedbackForm');
    
    // 文件选择
    uploadArea.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);
    
    // 拖拽上传
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('drop', handleDrop);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    
    // 粘贴图片
    document.addEventListener('paste', handlePaste);
    pasteArea.addEventListener('click', () => pasteArea.focus());
    
    // 表单提交
    form.addEventListener('submit', handleSubmit);
}

function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    files.forEach(file => {
        if (file.type.startsWith('image/')) {
            addImage(file);
        }
    });
}

function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add('dragover');
}

function handleDragLeave(e) {
    e.currentTarget.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
    
    const files = Array.from(e.dataTransfer.files);
    files.forEach(file => {
        if (file.type.startsWith('image/')) {
            addImage(file);
        }
    });
}

function handlePaste(e) {
    const items = Array.from(e.clipboardData.items);
    items.forEach(item => {
        if (item.type.startsWith('image/')) {
            const file = item.getAsFile();
            addImage(file, '剪贴板');
        }
    });
}

function addImage(file, source = '文件') {
    const reader = new FileReader();
    reader.onload = function(e) {
        const imageData = {
            data: e.target.result,
            source: source,
            name: file.name || '剪贴板图片',
            size: file.size
        };
        
        selectedImages.push(imageData);
        updateImagePreview();
    };
    reader.readAsDataURL(file);
}

function updateImagePreview() {
    const preview = document.getElementById('imagePreview');
    preview.innerHTML = '';
    
    selectedImages.forEach((img, index) => {
        const item = document.createElement('div');
        item.className = 'image-item';
        item.innerHTML = `
            <img src="${img.data}" alt="${img.name}">
            <button type="button" class="image-remove" onclick="removeImage(${index})">×</button>
        `;
        preview.appendChild(item);
    });
}

function removeImage(index) {
    selectedImages.splice(index, 1);
    updateImagePreview();
}

async function handleSubmit(e) {
    e.preventDefault();
    
    const textFeedback = document.getElementById('textFeedback').value.trim();
    const hasText = textFeedback.length > 0;
    const hasImages = selectedImages.length > 0;
    
    if (!hasText && !hasImages) {
        showAlert('请至少提供文字反馈或图片反馈', 'warning');
        return;
    }
    
    const submitBtn = document.getElementById('submitBtn');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<span class="loading"></span>提交中...';
    submitBtn.disabled = true;
    
    try {
        const response = await fetch('/submit_feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                textFeedback: hasText ? textFeedback : null,
                images: selectedImages.map(img => ({
                    data: img.data,
                    source: img.source,
                    name: img.name
                })),
                timestamp: new Date().toISOString()
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('反馈提交成功！感谢您的反馈。', 'success');
            setTimeout(() => {
                window.close();
            }, 2000);
        } else {
            showAlert('提交失败：' + result.message, 'warning');
        }
    } catch (error) {
        showAlert('提交失败：网络错误', 'warning');
    } finally {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

function showAlert(message, type) {
    const existingAlert = document.querySelector('.alert');
    if (existingAlert) {
        existingAlert.remove();
    }
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    
    const content = document.querySelector('.content');
    content.insertBefore(alert, content.firstChild);
    
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

// 定期检查服务器状态
setInterval(async () => {
    try {
        await fetch('/ping');
    } catch (error) {
        showAlert('与服务器连接中断', 'warning');
    }
}, 30000); 