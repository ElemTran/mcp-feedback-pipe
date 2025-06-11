# 统一待办事项列表 (Unified TODO List)

本文件整合了 `refactoring-improvement-todo.md` 和原始 `TODO.md` 的内容，并根据当前代码库的分析结果更新了各项任务的状态。

**最后更新日期:** 2025-06-06

## I. 代码重构与质量提升 (Refactoring & Code Quality)

### A. 函数与模块重构
- [ ] **任务1.1 (高优):** 重构 `frontend/static/js/modules/timeout-handler.js` 中的 `captureDataOnTimeout()` 函数
    - **描述:** 函数过长 (约150行)，逻辑复杂，违反了项目80行函数长度限制。
    - **原始来源:** `refactoring-improvement-todo.md` (函数复杂度优化), `TODO.md` (重构大型函数)
    - **当前状态:** 未完成。
    - **建议:** 拆分为数据收集、FormData准备、图片处理、重试提交、失败处理等多个独立小函数。
    - **后续:** 完成后需添加单元测试。
- [ ] **任务1.2 (中优):** 完善 `backend/server_manager.py` 的类型注解
    - **描述:** 确保所有公共和私有方法都有完整的类型注解。
    - **原始来源:** `refactoring-improvement-todo.md` (类型注解完善)
    - **当前状态:** 主要方法已完成，但需全面复查。
    - **建议:** 检查所有方法，特别是辅助方法和新添加的逻辑。

### B. DOM 操作优化 (Frontend)
- [ ] **任务1.3 (高优):** 优化 `frontend/static/js/modules/timeout-handler.js` 中的 DOM 查询
    - **描述:** 多处直接使用 `document.getElementById`，未缓存DOM元素。
    - **原始来源:** `refactoring-improvement-todo.md` (DOM查询优化), `TODO.md` (减少不必要的DOM操作)
    - **当前状态:** 未完成。
    - **建议:** 在 `timeout-handler.js` 中创建统一的 DOM 元素缓存对象 (如 `TimeoutElements`)。

### C. 配置管理
- [ ] **任务1.4 (中优):** 提取 `frontend/static/js/modules/timeout-handler.js` 中的硬编码常量
    - **描述:** 如 `MAX_RETRY_ATTEMPTS`, `NETWORK_TIMEOUT`, `RETRY_DELAYS`, `INACTIVITY_THRESHOLD` 等应移至配置文件。
    - **原始来源:** `refactoring-improvement-todo.md` (配置常量提取)
    - **当前状态:** 未完成。
    - **建议:** 在 `frontend/static/js/config/` (或类似路径)下创建 `timeout-config.js` 或 `app-config.js`。
- [ ] **任务1.5 (低优):** 将 `backend/server_manager.py` 中的类级别常量移至 `backend/config.py`
    - **描述:** 如 `SERVER_READY_MAX_ATTEMPTS`, `CONNECTION_CHECK_MAX_RETRIES` 等。
    - **原始来源:** `refactoring-improvement-todo.md` (配置常量提取 - 后端部分分析)
    - **当前状态:** 部分完成 (已有 `config.py`，但这些常量未提取)。
    - **建议:** 将这些常量纳入 `ServerConfig` 或新建的配置类中，并从 `ConfigManager` 读取。

### D. 代码规范与测试
- [ ] **任务1.6 (持续):** 统一代码风格和命名规范
    - **描述:** 遵循项目定义的代码规范 (见全局规则内存)。
    - **原始来源:** `TODO.md`
    - **当前状态:** 进行中/部分符合。
    - **建议:** 定期审查，使用自动化工具辅助。
- [ ] **任务1.7 (中优):** 增加单元测试覆盖率
    - **描述:** 特别是针对重构后的函数和核心业务逻辑。
    - **原始来源:** `TODO.md`, `refactoring-improvement-todo.md` (针对 `captureDataOnTimeout` 重构后)
    - **当前状态:** 需要确认/可能未完成。

## II. 性能优化 (Performance Optimization)

### A. 前端性能
- [x] **任务2.1 (中优):** 添加静态资源缓存机制 (CSS、JS文件)
    - **描述:** 减少重复加载，提升加载速度。
    - **原始来源:** `TODO.md`
    - **当前状态:** ✅ 已完成 (实现了完整的HTTP缓存机制，包括ETag、Cache-Control、304响应等) - 验证人：Roo - 日期：2025-06-07
    - **实现方案:** 创建了 `backend/utils/static_cache.py` 模块，集成Flask中间件，支持ETag、Cache-Control、Expires、Last-Modified等HTTP缓存头。
- [x] **任务2.2 (中优):** 实现图片等资源懒加载策略 (Frontend) - `image-handler.js`
    - **描述:** 提升首屏加载速度。
    - **原始来源:** `TODO.md`
    - **当前状态:** ✅ 已完成 (通过 `loading="lazy"` 属性实现) - 验证人：Cascade - 日期：{{TODAY}}
- [ ] **任务2.3 (高优):** 添加前端页面加载和关键操作性能监控
    - **描述:** 收集性能数据，定位瓶颈。
    - **原始来源:** `refactoring-improvement-todo.md`, `TODO.md`
    - **当前状态:** 未完成。
    - **建议:** 使用 `performance.now()`, `console.time/timeEnd` 或集成第三方监控工具。

### B. 后端性能
- [ ] **任务2.4 (中优):** 添加后端关键路径性能监控
    - **描述:** 如服务器启动时间、请求处理耗时、数据库交互等。
    - **原始来源:** `refactoring-improvement-todo.md`
    - **当前状态:** 未完成。
    - **建议:** 使用 `time.perf_counter()` 装饰器或中间件记录。

## III. 功能增强与用户体验 (Feature Enhancement & UX)

### A. 界面优化 (Frontend)
- [x] **任务3.1 (低优):** 考虑添加加载动画或进度指示器
    - **原始来源:** `TODO.md`
    - **当前状态:** ✅ 已完成 (通过按钮 `aria-busy` 状态及 `.loading` CSS 类实现) - 验证人：Cascade - 日期：{{TODAY}}
- [x] **任务3.2 (低优):** 确保响应式设计，适配不同屏幕尺寸 (CSS)
    - **原始来源:** `TODO.md`
    - **当前状态:** ✅ 已完成 (通过 `@media` 查询实现) - 验证人：Cascade - 日期：{{TODAY}}
- [ ] **任务3.3 (低优):** 增加键盘快捷键支持 (例如 Ctrl+Enter 提交)
    - **原始来源:** `TODO.md`
    - **当前状态:** 🟡 待办 (`form-handler.js` 中未发现相关实现) - 验证人：Cascade - 日期：{{TODAY}}

### B. 错误处理
- [ ] **任务3.4 (持续):** 改进网络错误处理机制
    - **描述:** 当前已有重试和本地备份。可进一步优化用户提示和恢复流程。
    - **原始来源:** `TODO.md`
    - **当前状态:** 部分完成/进行中。
    - **`captureDataOnTimeout` 中的自动重试机制已实现。**
- [ ] **任务3.5 (持续):** 添加更友好的错误提示信息
    - **描述:** `showUserNotification` 已提供基础。可根据具体场景细化。
    - **原始来源:** `TODO.md`
    - **当前状态:** 部分完成/进行中。

## IV. 文档 (Documentation)

- [ ] **任务4.1 (持续):** 完善API文档
    - **原始来源:** `TODO.md`
    - **当前状态:** 进行中。
    - **建议:** 遵循项目文档规范，使用Sphinx/Doxygen等工具。
- [ ] **任务4.2 (持续):** 添加/更新开发者指南
    - **原始来源:** `TODO.md`
    - **当前状态:** 进行中。
- [ ] **任务4.3 (持续):** 添加/更新用户手册
    - **原始来源:** `TODO.md`
    - **当前状态:** 进行中。

## V. 已完成事项 (Completed Items from previous TODOs)

- 修复120秒超时显示问题（显示为2分钟）
- 修复调整大小按钮右对齐问题
- 修复建议选项显示问题
- 发布v3.0.5版本到PyPI
- `backend/server_manager.py` 中 `_check_client_disconnection()`, `_is_server_healthy()`, `_cleanup_on_disconnection()`, `stop_server()` 等关键方法已添加类型注解。
- `frontend/static/js/modules/timeout-handler.js` 中的 `captureDataOnTimeout` 函数已实现网络请求的自动重试机制。
- 后端已建立 `config.py` 用于配置管理。
- **任务2.1:** 添加静态资源缓存机制 (CSS、JS文件) - 完成日期：2025-06-07
  - 实现了完整的HTTP缓存机制，包括ETag、Cache-Control、304响应等
  - 创建了 `backend/utils/static_cache.py` 模块
  - 集成Flask中间件，支持所有静态文件类型的缓存
  - 通过自动化测试验证功能正常

---
**注意:** 请在完成任务后及时更新本文件的状态，并将已完成任务移至 "V. 已完成事项" 部分，并注明完成日期。
