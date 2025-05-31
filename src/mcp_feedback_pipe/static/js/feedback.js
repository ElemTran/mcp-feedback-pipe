// 反馈通道前端脚本
let selectedImages = [];

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    initializeMarkdownRendering();
    initializeMermaid();
    initializeAutoResize();
    initializeSuggestOptions();
});

function initializeEventListeners() {
    const uploadBtn = document.getElementById('uploadBtn');
    const fileInput = document.getElementById('fileInput');
    const textFeedback = document.getElementById('textFeedback');
    const form = document.getElementById('feedbackForm');
    
    // 文件选择按钮
    uploadBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);
    
    // 文本框拖拽上传
    textFeedback.addEventListener('dragover', handleDragOver);
    textFeedback.addEventListener('drop', handleDrop);
    textFeedback.addEventListener('dragleave', handleDragLeave);
    
    // 文本框粘贴图片
    textFeedback.addEventListener('paste', handlePaste);
    
    // 表单提交
    form.addEventListener('submit', handleSubmit);
}

// 初始化Markdown渲染
function initializeMarkdownRendering() {
    const workSummary = document.getElementById('workSummary');
    const content = workSummary.textContent || workSummary.innerText;
    
    if (content && content.trim() !== "等待AI汇报工作内容...") {
        renderMarkdown(content, workSummary);
    }
}

// 初始化Mermaid
function initializeMermaid() {
    if (typeof mermaid !== 'undefined') {
        mermaid.initialize({
            startOnLoad: true,
            theme: 'default',
            securityLevel: 'loose',
            fontFamily: 'Microsoft YaHei, Arial, sans-serif'
        });
    }
}

// 初始化自动伸缩文本框
function initializeAutoResize() {
    const textarea = document.getElementById('textFeedback');
    if (textarea) {
        textarea.classList.add('auto-resize');
        textarea.addEventListener('input', autoResizeTextarea);
        // 初始调整
        autoResizeTextarea.call(textarea);
    }
}

// 渲染Markdown内容
function renderMarkdown(content, container) {
    try {
        // 配置marked选项
        marked.setOptions({
            highlight: function(code, lang) {
                if (typeof Prism !== 'undefined' && lang && Prism.languages[lang]) {
                    return Prism.highlight(code, Prism.languages[lang], lang);
                }
                return code;
            },
            breaks: true,
            gfm: true
        });
        
        // 渲染Markdown
        const html = marked.parse(content);
        container.innerHTML = html;
        
        // 处理Mermaid图表
        processMermaidDiagrams(container);
        
        // 高亮代码块
        if (typeof Prism !== 'undefined') {
            Prism.highlightAllUnder(container);
        }
        
    } catch (error) {
        console.error('Markdown渲染错误:', error);
        container.innerHTML = `<pre>${escapeHtml(content)}</pre>`;
    }
}

// 处理Mermaid图表
function processMermaidDiagrams(container) {
    const codeBlocks = container.querySelectorAll('pre code');
    codeBlocks.forEach((block, index) => {
        const text = block.textContent;
        if (text.trim().startsWith('graph') || 
            text.trim().startsWith('flowchart') ||
            text.trim().startsWith('sequenceDiagram') ||
            text.trim().startsWith('classDiagram') ||
            text.trim().startsWith('gitgraph') ||
            text.trim().startsWith('pie') ||
            text.trim().startsWith('journey') ||
            text.trim().startsWith('gantt')) {
            
            const mermaidDiv = document.createElement('div');
            mermaidDiv.className = 'mermaid';
            mermaidDiv.textContent = text;
            mermaidDiv.id = `mermaid-${Date.now()}-${index}`;
            
            block.parentElement.replaceWith(mermaidDiv);
            
            // 渲染Mermaid图表
            if (typeof mermaid !== 'undefined') {
                mermaid.init(undefined, mermaidDiv);
            }
        }
    });
}

// HTML转义
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 自动调整文本框高度
function autoResizeTextarea() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 300) + 'px';
}

// 切换汇报区域大小
function toggleReportSize() {
    const reportSection = document.querySelector('.work-report-section');
    const feedbackForm = document.getElementById('feedbackForm');
    const toggleBtn = document.getElementById('toggleReportBtn');
    
    if (reportSection.classList.contains('maximized')) {
        // 恢复默认大小
        reportSection.classList.remove('maximized');
        feedbackForm.style.display = 'block';
        toggleBtn.innerHTML = '📏 调整大小';
    } else {
        // 最大化汇报区域
        reportSection.classList.add('maximized');
        feedbackForm.style.display = 'none';
        toggleBtn.innerHTML = '📏 恢复大小';
    }
}

// 切换反馈输入区域
function toggleFeedbackSize() {
    const feedbackContent = document.getElementById('feedbackContent');
    const textarea = document.getElementById('textFeedback');
    
    if (feedbackContent.style.display === 'none') {
        feedbackContent.style.display = 'block';
        textarea.focus();
    } else {
        feedbackContent.style.display = 'none';
    }
}

// 切换图片上传区域
function toggleImageSection() {
    const imageContent = document.getElementById('imageContent');
    
    if (imageContent.style.display === 'none') {
        imageContent.style.display = 'block';
    } else {
        imageContent.style.display = 'none';
    }
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
    e.currentTarget.style.backgroundColor = '#f0f4ff';
    e.currentTarget.style.borderColor = '#667eea';
}

function handleDragLeave(e) {
    e.currentTarget.style.backgroundColor = '';
    e.currentTarget.style.borderColor = '';
}

function handleDrop(e) {
    e.preventDefault();
    e.currentTarget.style.backgroundColor = '';
    e.currentTarget.style.borderColor = '';
    
    const files = Array.from(e.dataTransfer.files);
    files.forEach(file => {
        if (file.type.startsWith('image/')) {
            addImage(file, '拖拽');
        }
    });
}

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
        // 显示提示信息
        showAlert('图片已添加到反馈中', 'success');
    }
}

function addImage(file, source = '文件') {
    const reader = new FileReader();
    reader.onload = function(e) {
        const imageData = {
            data: e.target.result,
            source: source,
            name: file.name || '粘贴图片',
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

// 初始化建议选项
function initializeSuggestOptions() {
    const suggestDataElement = document.getElementById('suggestData');
    if (!suggestDataElement) return;
    
    const suggestText = suggestDataElement.textContent.trim();
    if (!suggestText) return;
    
    try {
        const suggestions = JSON.parse(suggestText);
        if (Array.isArray(suggestions) && suggestions.length > 0) {
            renderSuggestOptions(suggestions);
        }
    } catch (error) {
        console.error('解析建议选项失败:', error);
    }
}

// 渲染建议选项
function renderSuggestOptions(suggestions) {
    const suggestOptions = document.getElementById('suggestOptions');
    const suggestList = document.getElementById('suggestList');
    
    if (!suggestOptions || !suggestList) return;
    
    suggestList.innerHTML = '';
    
    suggestions.forEach((suggestion, index) => {
        const item = document.createElement('div');
        item.className = 'suggest-item';
        item.innerHTML = `
            <div class="suggest-text" onclick="submitSuggestion('${escapeHtml(suggestion)}')">${escapeHtml(suggestion)}</div>
            <div class="suggest-actions">
                <button type="button" class="suggest-btn suggest-btn-copy" onclick="copySuggestion('${escapeHtml(suggestion)}')" title="复制到输入框">
                    📋
                </button>
                <button type="button" class="suggest-btn suggest-btn-submit" onclick="submitSuggestion('${escapeHtml(suggestion)}')" title="直接提交">
                    ✅
                </button>
            </div>
        `;
        suggestList.appendChild(item);
    });
    
    suggestOptions.style.display = 'block';
}

// 复制建议到输入框
function copySuggestion(suggestion) {
    const textarea = document.getElementById('textFeedback');
    if (textarea) {
        textarea.value = suggestion;
        textarea.focus();
        autoResizeTextarea.call(textarea);
        showAlert('建议已复制到输入框', 'success');
    }
}

// 直接提交建议
async function submitSuggestion(suggestion) {
    const textarea = document.getElementById('textFeedback');
    if (textarea) {
        textarea.value = suggestion;
    }
    
    // 触发表单提交
    const form = document.getElementById('feedbackForm');
    if (form) {
        const event = new Event('submit', { bubbles: true, cancelable: true });
        form.dispatchEvent(event);
    }
}

// 监听工作汇报内容更新
function updateWorkSummary(content) {
    const workSummary = document.getElementById('workSummary');
    if (content && content.trim()) {
        renderMarkdown(content, workSummary);
    }
} 