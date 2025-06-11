# MCP反馈服务器使用指南

## 🚀 快速开始

### 问题解决方案

✅ **解决了您提到的所有问题：**

1. **MCP工具互斥问题** - 使用轻量级端口查询工具
2. **服务器状态检测失效** - 使用独立的状态查看器
3. **端口信息缺失** - 提供多种端口信息获取方式
4. **MCP资源持久化** - 支持状态保存、恢复和跨会话访问
5. **标准MCP Resources** - 符合MCP协议的资源访问接口

## 🔧 可用工具

### 1. 启动反馈服务器
```python
# MCP工具
collect_feedback(
    work_summary="您的任务描述",
    timeout_seconds=300,
    suggest=["选项1", "选项2", "选项3"]
)
```

### 2. 快速查看端口信息（推荐）
```python
# MCP工具 - 超轻量级，不影响现有服务器
list_server_ports()
```

### 3. 详细服务器状态（资源持久化模式）
```python
# MCP工具 - 增强版状态查看，支持持久化
get_server_status()
```

### 4. MCP资源持久化管理
```python
# 保存当前状态到持久化文件
manage_mcp_resource_persistence("save")

# 从持久化文件加载并验证状态
manage_mcp_resource_persistence("load")

# 清理无效的持久化数据
manage_mcp_resource_persistence("clean")

# 创建状态备份
manage_mcp_resource_persistence("backup", "my_backup.json")

# 从备份恢复
manage_mcp_resource_persistence("restore", "my_backup.json")

# 导出配置为可分享格式
manage_mcp_resource_persistence("export", "shared_config.json")

# 导入外部配置
manage_mcp_resource_persistence("import", "shared_config.json")
```

### 5. 独立命令行工具
```bash
# 在终端中直接运行，不会影响任何MCP服务器
python3 mcp_server_status.py
```

## 🔗 MCP标准资源访问（推荐）

### 📊 核心资源

#### 1. 服务器状态资源
```
URI: mcp://feedback-server/status
```
- **描述**: 完整的服务器池状态信息
- **特性**: 持久化、跨会话、多客户端共享
- **内容**: JSON格式，包含服务器列表、端口信息、SSH命令等
- **优势**: 符合MCP标准，可被任何MCP客户端访问

#### 2. 活跃端口资源
```
URI: mcp://feedback-server/ports
```
- **描述**: 当前运行的端口信息
- **特性**: 轻量级、实时更新
- **内容**: 端口列表、访问URL、SSH转发命令
- **用途**: 快速获取可用服务器

#### 3. 动态配置资源（模板）
```
URI: mcp://feedback-server/config/{config_type}
```
- **参数**: `config_type` 可以是 `server`、`ssh`、`backup`
- **描述**: 根据类型提供不同的配置信息
- **示例**:
  - `mcp://feedback-server/config/server` - 服务器配置
  - `mcp://feedback-server/config/ssh` - SSH转发配置  
  - `mcp://feedback-server/config/backup` - 备份文件信息

### 🎯 MCP Resources优势

#### vs 传统工具调用
| 特性 | MCP Resources | 传统Tools |
|------|---------------|-----------|
| **访问方式** | URI标准化访问 | 函数调用 |
| **缓存支持** | 客户端可缓存 | 每次重新执行 |
| **跨会话** | 天然支持 | 需要持久化机制 |
| **多客户端** | 原生共享 | 需要额外同步 |
| **错误处理** | 统一格式 | 各自实现 |
| **性能** | 可优化缓存 | 实时计算 |

#### 实际使用场景

1. **开发调试**
   ```python
   # LLM可以直接访问资源，无需调用工具
   "请访问 mcp://feedback-server/status 获取当前服务器状态"
   ```

2. **自动化脚本**
   ```python
   # 其他MCP客户端可以直接读取资源
   import mcp_client
   status = mcp_client.get_resource("mcp://feedback-server/status")
   ```

3. **监控面板**
   ```python
   # 定期轮询资源获取状态
   ports = mcp_client.get_resource("mcp://feedback-server/ports")
   ```

## 📋 典型使用流程

### 场景1：单个反馈任务
1. 运行 `collect_feedback` 启动服务器
2. 注意输出中的端口信息
3. 在本地终端设置SSH转发
4. 在浏览器中访问反馈界面

### 场景2：多个并发任务  
1. 使用 `create_server_pool` 创建多个服务器
2. 使用 `list_server_ports` 快速获取所有端口
3. 设置多个SSH转发
4. 在不同浏览器标签页中同时工作

### 场景3：查看现有服务器
1. 使用 `list_server_ports` 快速查看活跃端口
2. 或运行 `python3 mcp_server_status.py` 获取详细信息
3. 根据输出设置SSH转发

### 场景4：跨会话工作（新增）
1. 使用 `get_server_status` 查看持久化状态
2. 即使MCP工具异常，状态信息仍可访问
3. 使用 `manage_mcp_resource_persistence("load")` 验证服务器
4. 通过备份/恢复功能保护重要配置

### 场景5：团队协作（新增）
1. 使用 `manage_mcp_resource_persistence("export")` 导出配置
2. 分享配置文件给团队成员
3. 团队成员使用 `manage_mcp_resource_persistence("import")` 导入
4. 使用 `create_server_pool` 重建相同的服务器环境

### 场景6：标准MCP Resources访问（推荐）
1. **LLM直接访问**: "请检查 mcp://feedback-server/status 的服务器状态"
2. **客户端轮询**: 定期访问 `mcp://feedback-server/ports` 监控服务器
3. **配置管理**: 访问 `mcp://feedback-server/config/ssh` 获取SSH配置
4. **跨工具共享**: 多个MCP工具可以访问相同的资源URI

## 🔗 SSH端口转发设置

### 基本命令格式
```bash
ssh -L 本地端口:127.0.0.1:远程端口 用户名@服务器地址
```

### 示例
```bash
# 单个服务器
ssh -L 8888:127.0.0.1:8765 yjb@your_server

# 多个服务器（使用不同本地端口）
ssh -L 8888:127.0.0.1:8765 yjb@your_server
ssh -L 8889:127.0.0.1:8766 yjb@your_server  
ssh -L 8890:127.0.0.1:8767 yjb@your_server
```

### 访问地址
- 第一个服务器: http://127.0.0.1:8888/
- 第二个服务器: http://127.0.0.1:8889/
- 第三个服务器: http://127.0.0.1:8890/

## 💾 MCP资源持久化特性

### 🔄 自动持久化
- 服务器启动时自动保存状态
- 服务器停止时自动更新状态
- 状态文件：`.mcp_server_pool_status.json`

### 📊 持久化数据包含
- 服务器配置信息（session_id、work_summary、timeout等）
- 端口分配情况
- 服务器运行状态
- 时间戳和元数据

### 🛡️ 数据可靠性
- 支持状态验证（检查服务器是否真正运行）
- 自动清理无效数据
- 备份和恢复功能
- 数据导出/导入功能

### 🏗️ MCP标准化实现

#### 资源结构设计
```json
{
  "mcp_resource": {
    "uri": "mcp://feedback-server/status",
    "name": "服务器池状态",
    "description": "MCP反馈服务器池的完整状态信息",
    "mimeType": "application/json",
    "generated_at": 1749609556.838,
    "generated_at_readable": "2025-06-11 10:39:16"
  },
  "persistence": {
    "enabled": true,
    "last_saved": "2025-06-11 10:39:16",
    "file_path": ".mcp_server_pool_status.json",
    "auto_save": true
  },
  "data_sources": {
    "persistent": {
      "available": true,
      "servers_count": 1,
      "ports": [8765]
    },
    "runtime": {
      "available": true,
      "servers_count": 1,
      "active_count": 1,
      "ports": [8765]
    }
  },
  "servers": [...],
  "ssh_commands": [...],
  "access_urls": [...],
  "statistics": {...}
}
```

#### 资源访问模式
1. **静态资源**: 直接通过URI访问，如 `mcp://feedback-server/status`
2. **动态资源**: 参数化URI，如 `mcp://feedback-server/config/{config_type}`
3. **轻量级资源**: 快速访问，如 `mcp://feedback-server/ports`

### 🔧 实际应用场景

#### 开发调试
```python
# 开发期间保存当前配置
manage_mcp_resource_persistence("save")

# 开发完成后导出配置
manage_mcp_resource_persistence("export", "dev_config.json")

# 或直接访问MCP资源
"请访问 mcp://feedback-server/config/server 查看服务器配置"
```

#### 生产部署
```python
# 导入开发配置
manage_mcp_resource_persistence("import", "dev_config.json")

# 重建服务器
create_server_pool([...])  # 根据导入的配置

# 或通过MCP资源获取SSH配置
"从 mcp://feedback-server/config/ssh 获取SSH转发命令"
```

#### 故障恢复
```python
# 系统异常后检查状态
get_server_status()

# 清理无效服务器
manage_mcp_resource_persistence("clean")

# 从备份恢复（如需要）
manage_mcp_resource_persistence("restore", "backup_file.json")

# 或通过MCP资源持续监控
"定期检查 mcp://feedback-server/status 的服务器状态"
```

## ⚙️ 配置选项

### 环境变量
```bash
# 浏览器连接宽限期（默认15秒）
export MCP_BROWSER_GRACE_PERIOD=20

# 默认超时时间（默认300秒）
export MCP_DEFAULT_TIMEOUT=180

# 首选远程端口（默认8765）
export MCP_FEEDBACK_PREFERRED_PORT=9000

# 推荐本地转发端口（默认8888）
export MCP_FEEDBACK_LOCAL_FORWARD_PORT=9888
```

### 超时时间设置
- **图片选择**: 120秒（2分钟）
- **文字反馈**: 300秒（5分钟）  
- **自定义**: 通过 `timeout_seconds` 参数设置

## 🛠️ 故障排除

### 1. 找不到服务器端口
```bash
# 使用独立状态查看器
python3 mcp_server_status.py

# 或使用轻量级MCP工具
list_server_ports()

# 或使用持久化资源查看
get_server_status()

# 或直接访问MCP资源（推荐）
"访问 mcp://feedback-server/ports 获取活跃端口"
```

### 2. MCP工具卡住或异常
```python
# 使用持久化资源查看（不依赖运行时状态）
get_server_status()

# 从持久化文件验证状态
manage_mcp_resource_persistence("load")

# 或直接访问MCP资源（最可靠）
"访问 mcp://feedback-server/status 获取完整状态信息"
```

### 3. 端口被占用
- 系统会自动分配下一个可用端口
- 第一个服务器通常使用8765
- 后续服务器使用8766、8767等

### 4. SSH转发失败
```bash
# 检查服务器是否运行
curl http://127.0.0.1:8765/ping

# 测试SSH连接
ssh -v your_user@your_server

# 或通过MCP资源获取正确的SSH命令
"从 mcp://feedback-server/config/ssh 获取SSH转发命令"
```

### 5. 浏览器无法访问
- 确认SSH转发命令正确执行
- 检查本地端口是否被占用
- 尝试使用不同的本地端口

### 6. 状态文件损坏
```python
# 验证状态文件
manage_mcp_resource_persistence("load")

# 清理无效数据
manage_mcp_resource_persistence("clean")

# 从备份恢复
manage_mcp_resource_persistence("restore", "backup_file.json")

# 或检查备份文件信息
"访问 mcp://feedback-server/config/backup 查看备份状态"
```

## 💡 最佳实践

### 开发阶段
1. **状态管理**: 定期使用 `manage_mcp_resource_persistence("save")` 保存状态
2. **配置备份**: 重要配置使用 `backup` 操作创建备份
3. **开发协作**: 使用 `export/import` 功能分享配置
4. **MCP资源**: 优先使用标准MCP资源访问状态信息

### 生产环境
1. **端口查询**: 优先使用 `list_server_ports()` 获取端口信息
2. **状态监控**: 使用独立命令行工具 `mcp_server_status.py`
3. **故障恢复**: 建立定期备份机制
4. **资源监控**: 通过MCP资源进行系统监控

### 团队协作
1. **配置标准化**: 使用导出/导入功能统一配置
2. **版本控制**: 将配置文件纳入版本控制
3. **环境同步**: 使用相同的配置文件部署开发/测试环境
4. **资源共享**: 团队成员可通过MCP资源URI共享状态

### MCP资源管理
1. **持久化优先**: 利用持久化功能减少对实时工具的依赖
2. **定期清理**: 使用 `clean` 操作清理无效数据
3. **备份策略**: 重要工作前创建备份
4. **标准化访问**: 优先使用MCP Resources而非传统工具调用

### 资源访问策略
1. **性能优化**: MCP Resources支持客户端缓存，减少重复查询
2. **错误处理**: 统一的资源格式便于错误诊断
3. **扩展性**: 新增资源类型无需修改客户端代码
4. **兼容性**: 同时支持传统工具和标准资源访问

## 📄 状态文件

### 自动维护文件
- **主状态文件**: `.mcp_server_pool_status.json`
- **备份文件**: `mcp_status_backup_*.json`
- **配置导出**: `mcp_config_export_*.json`

### 文件内容
```json
{
  "mcp_resource_type": "server_pool_status",
  "total_servers": 1,
  "active_servers": 1,
  "ports_in_use": [8765],
  "servers": [
    {
      "session_id": "test_server",
      "port": 8765,
      "status": "running",
      "work_summary": "轻量级状态测试",
      "timeout_seconds": 300,
      "url": "http://127.0.0.1:8765"
    }
  ],
  "last_updated": 1749609556.8380816,
  "last_updated_readable": "2025-06-11 10:39:16"
}
```

### MCP资源URI列表

#### 核心资源
- `mcp://feedback-server/status` - 完整服务器状态
- `mcp://feedback-server/ports` - 活跃端口列表

#### 配置资源（动态模板）
- `mcp://feedback-server/config/server` - 服务器配置参数
- `mcp://feedback-server/config/ssh` - SSH转发配置
- `mcp://feedback-server/config/backup` - 备份文件管理

#### 资源特性
- **持久化**: 所有资源都基于持久化文件，确保跨会话访问
- **实时性**: 资源内容反映当前实际状态
- **标准化**: 符合MCP协议，可被任何MCP客户端访问
- **缓存友好**: 客户端可以安全缓存资源内容

### 持久化优势
- **跨会话访问**: MCP工具重启后仍可访问历史状态
- **故障恢复**: 系统异常后可快速恢复服务器信息
- **多客户端共享**: 多个MCP客户端可共享状态信息
- **离线查询**: 即使服务器停止，仍可查看历史配置
- **标准兼容**: 符合MCP Resources标准，提供统一访问接口

此文件可用于故障恢复和状态持久化，是MCP资源管理的核心组件。通过标准化的MCP Resources接口，为LLM和客户端应用程序提供了强大的只读数据访问能力。 