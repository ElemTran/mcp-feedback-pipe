# 外部依赖版本管理

本文档记录了MCP反馈通道使用的所有外部依赖及其版本信息。

## 当前使用的依赖版本

### JavaScript库

| 库名称 | 当前版本 | 最新版本 | 用途 | CDN源 |
|--------|----------|----------|------|-------|
| Marked.js | 15.0.12 | 15.0.12 | Markdown解析和渲染 | jsDelivr, unpkg |
| Mermaid.js | 11.6.0 | 11.6.0 | 图表和流程图渲染 | jsDelivr, unpkg |
| Prism.js | 1.30.0 | 1.30.0 | 代码语法高亮 | jsDelivr, unpkg |

### 版本更新历史

#### 2025-01-31
- **Marked.js**: 9.1.6 → 15.0.12
  - 重大版本升级，性能提升
  - 改进了安全性和兼容性
  - 更好的TypeScript支持

- **Mermaid.js**: 10.6.1 → 11.6.0
  - 新增多种图表类型支持
  - 改进了渲染性能
  - 修复了多个安全漏洞

- **Prism.js**: 1.29.0 → 1.30.0
  - 新增语言支持
  - 改进了主题系统
  - 修复了XSS安全问题

## 安全改进

### 1. 多CDN备用机制
- 主CDN: jsDelivr (`cdn.jsdelivr.net`)
- 备用CDN: unpkg (`unpkg.com`)
- 自动故障转移，提高可用性

### 2. 安全属性
- `crossorigin="anonymous"`: 启用CORS安全检查
- `referrerpolicy="no-referrer"`: 防止引用信息泄露
- CSP策略: 限制资源加载来源

### 3. 动态加载
- 异步加载，不阻塞页面渲染
- 错误处理和降级机制
- 加载状态监控和日志

## 版本更新策略

### 自动检查
使用脚本定期检查依赖更新：
```bash
python tools/check_dependency_updates.py
```

### 更新原则
1. **安全更新**: 立即应用安全补丁
2. **主版本更新**: 谨慎评估，充分测试
3. **次版本更新**: 定期更新，保持功能最新
4. **补丁更新**: 及时应用，修复bug

### 测试要求
- 功能测试: 确保所有功能正常
- 兼容性测试: 验证浏览器兼容性
- 性能测试: 确保加载性能不降低
- 安全测试: 验证安全性改进

## 备用方案

### 离线模式
如果CDN不可用，系统会：
1. 显示警告信息
2. 禁用相关功能
3. 保持基本功能可用

### 本地化部署
可以将依赖下载到本地：
```bash
# 下载依赖到本地
python scripts/download_dependencies.py
```

## 监控和维护

### 依赖健康检查
- 定期检查CDN可用性
- 监控加载性能
- 跟踪错误率

### 更新通知
- GitHub Dependabot自动PR
- 安全漏洞通知
- 版本发布订阅

## 相关文件

- `src/mcp_feedback_pipe/templates/feedback.html` - 依赖加载配置
- `tools/update_sri_hashes.py` - SRI哈希值更新脚本
- `tools/check_dependency_updates.py` - 依赖更新检查脚本
- `tools/test_security_fixes.py` - 安全修复验证测试

## 注意事项

1. **版本锁定**: 使用具体版本号，避免自动更新
2. **安全验证**: 虽然暂时没有SRI验证，但保留了安全属性
3. **性能优化**: 使用压缩版本，减少加载时间
4. **兼容性**: 确保支持目标浏览器版本

## 未来计划

1. **SRI验证**: 实现完整的子资源完整性验证
2. **本地缓存**: 添加Service Worker缓存机制
3. **版本自动化**: 完全自动化的依赖更新流程
4. **性能监控**: 实时监控依赖加载性能 