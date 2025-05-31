/**
 * Markdown渲染模块
 * 负责处理Markdown内容的渲染、Mermaid图表处理等
 */

import { escapeHtml, showAlert } from './utils.js';

/**
 * 简化的HTML清理函数，防止XSS攻击
 * @param {string} html - 需要清理的HTML字符串
 * @returns {string} 清理后的安全HTML
 */
function sanitizeHTML(html) {
    // 允许的标签和属性
    const allowedTags = [
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'p', 'br', 'hr', 'div', 'span',
        'strong', 'b', 'em', 'i', 'u', 'del', 's',
        'ul', 'ol', 'li',
        'blockquote', 'pre', 'code',
        'table', 'thead', 'tbody', 'tr', 'th', 'td',
        'a', 'img'
    ];
    
    const allowedAttributes = {
        'a': ['href', 'title', 'target'],
        'img': ['src', 'alt', 'title', 'width', 'height'],
        'pre': ['class'],
        'code': ['class'],
        'div': ['class'],
        'span': ['class']
    };
    
    // 创建临时DOM元素进行清理
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;
    
    // 递归清理函数
    function cleanElement(element) {
        const tagName = element.tagName.toLowerCase();
        
        // 检查标签是否允许
        if (!allowedTags.includes(tagName)) {
            // 不允许的标签，保留文本内容
            const textNode = document.createTextNode(element.textContent || '');
            element.parentNode.replaceChild(textNode, element);
            return;
        }
        
        // 清理属性
        const allowedAttrs = allowedAttributes[tagName] || [];
        const attributes = Array.from(element.attributes);
        
        attributes.forEach(attr => {
            if (!allowedAttrs.includes(attr.name)) {
                element.removeAttribute(attr.name);
            } else {
                // 特殊处理href属性，防止javascript:协议
                if (attr.name === 'href') {
                    const href = attr.value.toLowerCase().trim();
                    if (href.startsWith('javascript:') || href.startsWith('data:') || href.startsWith('vbscript:')) {
                        element.removeAttribute(attr.name);
                    }
                }
                // 特殊处理src属性
                if (attr.name === 'src') {
                    const src = attr.value.toLowerCase().trim();
                    if (src.startsWith('javascript:') || src.startsWith('vbscript:')) {
                        element.removeAttribute(attr.name);
                    }
                }
            }
        });
        
        // 递归处理子元素
        Array.from(element.children).forEach(child => {
            cleanElement(child);
        });
    }
    
    // 清理所有子元素
    Array.from(tempDiv.children).forEach(child => {
        cleanElement(child);
    });
    
    return tempDiv.innerHTML;
}

/**
 * 初始化Markdown渲染
 */
export function initializeMarkdownRendering() {
    const workSummary = document.getElementById('workSummary');
    if (!workSummary) return;
    
    // 优先从data-raw-content属性获取原始内容，避免HTML转义问题
    let content = workSummary.getAttribute('data-raw-content');
    
    // 如果没有data属性，则从文本内容获取
    if (!content) {
        content = workSummary.textContent || workSummary.innerText;
    }
    
    // 修复：即使是默认文本也要检查是否包含Markdown语法
    if (content && content.trim()) {
        renderMarkdown(content, workSummary);
    }
}

/**
 * 初始化Mermaid图表库
 */
export function initializeMermaid() {
    if (typeof mermaid !== 'undefined') {
        mermaid.initialize({
            startOnLoad: true,
            theme: 'default',
            securityLevel: 'loose',
            fontFamily: 'Microsoft YaHei, Arial, sans-serif'
        });
    }
}

/**
 * 渲染Markdown内容
 * @param {string} content - Markdown内容
 * @param {HTMLElement} container - 容器元素
 */
export function renderMarkdown(content, container) {
    try {
        // 检查是否包含Markdown语法
        if (!hasMarkdownSyntax(content)) {
            // 如果没有Markdown语法，保持原样但应用基本格式
            container.innerHTML = `<p>${escapeHtml(content)}</p>`;
            return;
        }
        
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
        
        // XSS防护：清理HTML内容
        const cleanHtml = sanitizeHTML(html);
        container.innerHTML = cleanHtml;
        
        // 处理Mermaid图表
        processMermaidDiagrams(container);
        
        // 高亮代码块
        if (typeof Prism !== 'undefined') {
            Prism.highlightAllUnder(container);
        }
        
    } catch (error) {
        console.error('Markdown渲染错误:', error);
        container.innerHTML = `<pre>${escapeHtml(content)}</pre>`;
        showAlert('Markdown渲染出现问题，已切换到纯文本显示', 'warning');
    }
}

/**
 * 检查文本是否包含Markdown语法
 * @param {string} text - 要检查的文本
 * @returns {boolean} 是否包含Markdown语法
 */
function hasMarkdownSyntax(text) {
    const markdownPatterns = [
        /^#{1,6}\s/m,           // 标题
        /\*\*.*?\*\*/,          // 粗体
        /\*.*?\*/,              // 斜体
        /`.*?`/,                // 行内代码
        /```[\s\S]*?```/,       // 代码块
        /^\s*[-*+]\s/m,         // 无序列表
        /^\s*\d+\.\s/m,         // 有序列表
        /^\s*>\s/m,             // 引用
        /\[.*?\]\(.*?\)/,       // 链接
        /!\[.*?\]\(.*?\)/,      // 图片
        /^\s*\|.*\|/m,          // 表格
        /^---+$/m,              // 分隔线
    ];
    
    return markdownPatterns.some(pattern => pattern.test(text));
}

/**
 * 处理Mermaid图表
 * @param {HTMLElement} container - 容器元素
 */
export function processMermaidDiagrams(container) {
    const codeBlocks = container.querySelectorAll('pre code');
    codeBlocks.forEach((block, index) => {
        const text = block.textContent;
        if (isMermaidDiagram(text)) {
            const mermaidDiv = document.createElement('div');
            mermaidDiv.className = 'mermaid';
            mermaidDiv.textContent = text;
            mermaidDiv.id = `mermaid-${Date.now()}-${index}`;
            
            block.parentElement.replaceWith(mermaidDiv);
            
            // 渲染Mermaid图表
            if (typeof mermaid !== 'undefined') {
                try {
                    mermaid.init(undefined, mermaidDiv);
                } catch (error) {
                    console.error('Mermaid图表渲染失败:', error);
                    mermaidDiv.innerHTML = `<pre>图表渲染失败: ${escapeHtml(text)}</pre>`;
                }
            }
        }
    });
}

/**
 * 检查文本是否为Mermaid图表
 * @param {string} text - 要检查的文本
 * @returns {boolean} 是否为Mermaid图表
 */
function isMermaidDiagram(text) {
    const trimmedText = text.trim();
    const mermaidKeywords = [
        'graph', 'flowchart', 'sequenceDiagram', 'classDiagram',
        'gitgraph', 'pie', 'journey', 'gantt', 'stateDiagram',
        'erDiagram', 'userJourney', 'requirement'
    ];
    
    return mermaidKeywords.some(keyword => trimmedText.startsWith(keyword));
}

/**
 * 更新工作汇报内容
 * @param {string} content - 新的汇报内容
 */
export function updateWorkSummary(content) {
    const workSummary = document.getElementById('workSummary');
    if (content && content.trim()) {
        renderMarkdown(content, workSummary);
    }
} 