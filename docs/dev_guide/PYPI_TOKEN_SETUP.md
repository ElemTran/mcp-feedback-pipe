# PyPI Token 配置指南

## 📋 概述

为了简化发布流程，您可以将PyPI和TestPyPI的API token保存到环境变量中，这样就不需要每次发布时都手动输入token。

## 🔧 设置步骤

### 1. 获取API Token

#### TestPyPI Token
1. 访问 [TestPyPI Token管理页面](https://test.pypi.org/manage/account/token/)
2. 登录您的TestPyPI账户
3. 点击 "Add API token"
4. 输入token名称（如：`mcp-feedback-pipe-dev`）
5. 选择范围：
   - **首次发布**: 选择 "Entire account"
   - **后续发布**: 选择 "Scope to project" 并选择 `mcp-feedback-pipe`
6. 点击 "Add token"
7. **重要**: 复制生成的token（格式：`pypi-xxxxxxxx...`）

#### PyPI Token
1. 访问 [PyPI Token管理页面](https://pypi.org/manage/account/token/)
2. 登录您的PyPI账户
3. 重复上述相同步骤

### 2. 配置环境变量

#### 方法一：使用.env文件（推荐）

1. 复制示例文件：
```bash
cp .env.example .env
```

2. 编辑`.env`文件，填入您的token：
```bash
# TestPyPI API Token
TESTPYPI_TOKEN=pypi-your-actual-testpypi-token

# PyPI API Token  
PYPI_TOKEN=pypi-your-actual-pypi-token

# 可选配置
PUBLISH_TIMEOUT=300
AUTO_CONFIRM_PYPI=false
```

#### 方法二：系统环境变量

```bash
# 临时设置（当前会话有效）
export TESTPYPI_TOKEN="pypi-your-testpypi-token"
export PYPI_TOKEN="pypi-your-pypi-token"

# 永久设置（添加到~/.bashrc或~/.zshrc）
echo 'export TESTPYPI_TOKEN="pypi-your-testpypi-token"' >> ~/.bashrc
echo 'export PYPI_TOKEN="pypi-your-pypi-token"' >> ~/.bashrc
source ~/.bashrc
```

## 🚀 使用发布脚本

配置完成后，运行发布脚本：

```bash
cd /path/to/mcp-feedback-collector
python scripts/publish_to_pypi.py
```

脚本会自动：
1. ✅ 检测并加载`.env`文件
2. ✅ 使用环境变量中的token（如果可用）
3. ✅ 跳过token输入步骤
4. ✅ 直接进行发布流程

## 🔒 安全注意事项

### ⚠️ 重要安全提醒

1. **永远不要提交.env文件到Git仓库**
   - `.env`文件已添加到`.gitignore`
   - 确保不要意外提交包含真实token的文件

2. **Token权限管理**
   - 使用最小权限原则
   - 定期轮换token
   - 不再使用时及时删除token

3. **环境隔离**
   - 开发环境使用TestPyPI token
   - 生产发布使用PyPI token
   - 不要在公共环境中设置token

## 📝 配置选项说明

| 环境变量 | 说明 | 默认值 | 示例 |
|---------|------|--------|------|
| `TESTPYPI_TOKEN` | TestPyPI API token | 无 | `pypi-AgEIcHl...` |
| `PYPI_TOKEN` | PyPI API token | 无 | `pypi-AgEIcHl...` |
| `PUBLISH_TIMEOUT` | 发布超时时间（秒） | 300 | `600` |
| `AUTO_CONFIRM_PYPI` | 自动确认发布到PyPI | false | `true` |

## 🔄 回退方案

如果环境变量未设置或token无效，脚本会自动回退到交互式输入模式：

```
⚠️  未找到.env文件，将使用交互式输入

🔑 TestPyPI认证配置
请访问 https://test.pypi.org/manage/account/token/ 创建TestPyPI API token
💡 提示: 您可以将token保存到.env文件中的TESTPYPI_TOKEN变量
请输入TestPyPI API token (格式: pypi-...): 
```

## 🧪 测试配置

验证配置是否正确：

```bash
# 检查环境变量
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
testpypi = os.getenv('TESTPYPI_TOKEN', 'Not set')
pypi = os.getenv('PYPI_TOKEN', 'Not set')
print(f'TestPyPI Token: {testpypi[:20]}...' if testpypi != 'Not set' else 'TestPyPI Token: Not set')
print(f'PyPI Token: {pypi[:20]}...' if pypi != 'Not set' else 'PyPI Token: Not set')
"
```

## 🆘 故障排除

### 常见问题

1. **Token格式错误**
   ```
   ❌ Token格式错误，应该以 'pypi-' 开头
   ```
   **解决**: 确保token以`pypi-`开头

2. **权限不足**
   ```
   ❌ 403 Forbidden
   ```
   **解决**: 检查token权限，确保有发布权限

3. **环境变量未加载**
   ```
   ⚠️  未找到.env文件，将使用交互式输入
   ```
   **解决**: 确保`.env`文件存在且格式正确

4. **依赖缺失**
   ```
   ModuleNotFoundError: No module named 'dotenv'
   ```
   **解决**: 安装依赖 `pip install python-dotenv`

---

**配置完成后，您就可以享受无缝的自动化发布体验了！** 🎉 