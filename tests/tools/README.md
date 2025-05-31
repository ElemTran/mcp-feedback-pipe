# 测试和开发工具

本目录包含用于测试、验证和维护MCP反馈通道的各种工具脚本。

## 📁 文件说明

### 安全测试工具
- `test_security_fixes.py` - 安全修复验证测试
  - 测试CSRF保护功能
  - 验证内存安全检查
  - 检查队列限制机制
  - 验证配置管理系统

### 依赖管理工具
- `update_sri_hashes.py` - SRI哈希值更新脚本
  - 自动获取CDN资源的SRI哈希值
  - 更新HTML模板中的完整性验证
  - 生成SRI报告文档

- `check_dependency_updates.py` - 依赖更新检查脚本
  - 检查NPM包的最新版本
  - 比较当前版本与最新版本
  - 生成更新建议报告

## 🚀 使用方法

### 运行安全测试
```bash
# 从项目根目录运行
python tests/tools/test_security_fixes.py
```

### 检查依赖更新
```bash
# 从项目根目录运行
python tests/tools/check_dependency_updates.py
```

### 更新SRI哈希值
```bash
# 从项目根目录运行
python tests/tools/update_sri_hashes.py
```

## 📋 依赖要求

这些工具需要以下Python包：
- `requests` - HTTP请求
- `packaging` - 版本比较
- 项目的核心依赖

## 🔧 开发说明

### 添加新工具
1. 在此目录创建新的Python脚本
2. 添加适当的文档字符串
3. 更新此README文件
4. 确保脚本可以从项目根目录运行

### 路径处理
所有脚本都应该：
- 使用相对于项目根目录的路径
- 正确处理不同操作系统的路径分隔符
- 包含错误处理和用户友好的输出

### 测试集成
工具脚本可以集成到CI/CD流程中：
- 安全测试可以作为PR检查的一部分
- 依赖检查可以定期运行
- SRI更新可以在依赖升级时自动执行

## 📚 相关文档

- [依赖版本管理](../../docs/dev_guide/dependencies/DEPENDENCY_VERSIONS.md)
- [开发指南](../../docs/dev_guide/)
- [测试指南](../README.md) 