# JavaScript模块化架构说明

## 模块结构

本项目采用ES6模块化架构，遵循单一职责原则，将原来的单一大文件拆分为多个功能模块：

### 1. `utils.js` - 工具函数模块
- **职责**: 提供通用的工具函数
- **功能**:
  - `debounce()` - 防抖函数
  - `compressImage()` - 图片压缩
  - `escapeHtml()` - HTML转义
  - `showAlert()` - 显示提示消息
  - `autoResizeTextarea()` - 自动调整文本框高度

### 2. `markdown-renderer.js` - Markdown渲染模块
- **职责**: 处理Markdown内容渲染和图表
- **功能**:
  - `initializeMarkdownRendering()` - 初始化Markdown渲染
  - `initializeMermaid()` - 初始化Mermaid图表库
  - `renderMarkdown()` - 渲染Markdown内容
  - `processMermaidDiagrams()` - 处理Mermaid图表
  - `updateWorkSummary()` - 更新工作汇报内容

### 3. `image-handler.js` - 图片处理模块
- **职责**: 处理图片上传、压缩、预览等
- **功能**:
  - `initializeImageHandlers()` - 初始化图片处理事件
  - 文件选择、拖拽、粘贴处理
  - 图片压缩和验证
  - 图片预览和删除
  - `getSelectedImages()` - 获取选中图片
  - `hasSelectedImages()` - 检查是否有图片

### 4. `suggestion-handler.js` - 建议选项模块
- **职责**: 处理建议选项的渲染和交互
- **功能**:
  - `initializeSuggestOptions()` - 初始化建议选项
  - 建议选项渲染
  - 复制建议到光标位置
  - `submitSuggestion()` - 直接提交建议

### 5. `form-handler.js` - 表单处理模块
- **职责**: 处理表单提交和UI控制
- **功能**:
  - `initializeFormHandlers()` - 初始化表单事件
  - 表单提交处理
  - `toggleReportSize()` - 切换汇报区域大小
  - `toggleFeedbackSize()` - 切换反馈区域
  - `toggleImageSection()` - 切换图片区域

### 6. `error-handler.js` - 错误处理模块
- **职责**: 全局错误处理和服务器监控
- **功能**:
  - `initializeGlobalErrorHandling()` - 全局错误处理
  - `startServerHealthCheck()` - 服务器健康检查

### 7. `feedback-main.js` - 主入口文件
- **职责**: 整合所有模块，统一初始化
- **功能**:
  - 导入所有模块
  - 统一初始化流程
  - 暴露全局函数到window对象

## 修复的问题

### 1. Markdown渲染问题
- **问题**: AI反馈报告的第一行没有使用Markdown渲染，但有固定背景和居中样式
- **原因**: HTML模板直接输出work_summary内容，JavaScript只在非默认文本时才渲染
- **解决方案**: 
  - 在HTML中添加`data-raw-content`属性存储原始内容
  - 修改渲染逻辑，优先从data属性获取内容
  - 改进Markdown语法检测，确保所有内容都能正确渲染

### 2. 代码结构问题
- **问题**: 原来的`feedback.js`文件过大（765行），违反单一职责原则
- **解决方案**: 按功能拆分为6个模块，每个模块职责明确

## 使用方式

1. HTML模板中使用ES6模块导入：
```html
<script type="module" src="{{ url_for('static', filename='js/feedback-main.js') }}"></script>
```

2. 模块间通过import/export进行依赖管理

3. 全局函数通过window对象暴露，保持向后兼容

## 优势

1. **可维护性**: 每个模块职责单一，易于理解和修改
2. **可测试性**: 模块化便于单元测试
3. **可扩展性**: 新功能可以独立模块形式添加
4. **性能**: 按需加载，减少初始化时间
5. **代码复用**: 工具函数可在多个模块间共享 