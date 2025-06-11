# 项目开发者指南

## 1. 项目概述

### 1.1 项目目标与核心功能
本项目旨在提供一个用户友好的反馈收集与管理系统。核心功能包括：
*   用户通过 Web 界面提交文本和图片反馈。
*   前端具备超时自动捕获和提交反馈机制。
*   后端负责接收、处理和存储反馈数据。
*   提供 API 接口供前端调用。

### 1.2 主要技术栈
*   **后端:** Python, Flask (Web 框架), Pydantic (数据校验)
*   **前端:** 原生 JavaScript (ES6+ 模块化), HTML5, CSS3
*   **测试:** Pytest (后端测试), Selenium (E2E 测试)
*   **版本控制:** Git

## 2. 开发环境搭建

### 2.1 系统要求
*   **操作系统:** Windows, macOS, Linux
*   **Python 版本:** 建议 Python 3.9+ (项目当前依赖兼容)
*   **Node.js 版本:** 前端不涉及复杂的构建流程，无需特定 Node.js 版本，但如果开发者习惯使用 npm/yarn 管理辅助工具，可自行安装。
*   **Git:** 用于代码版本控制。

### 2.2 获取代码
```bash
git clone <项目仓库地址>
cd <项目目录>
```
*(请将 `<项目仓库地址>` 替换为实际的 Git 仓库 URL)*

### 2.3 Python 虚拟环境
强烈建议在 Python 虚拟环境中进行开发，以隔离项目依赖。

**创建虚拟环境 (例如，使用 `.venv`):**
```bash
python -m venv .venv
```

**激活虚拟环境:**
*   Windows (PowerShell):
    ```powershell
    .\.venv\Scripts\Activate.ps1
    ```
*   Windows (cmd.exe):
    ```bash
    .\.venv\Scripts\activate.bat
    ```
*   macOS/Linux (bash/zsh):
    ```bash
    source .venv/bin/activate
    ```
激活成功后，命令行提示符前通常会显示 `(.venv)`。

### 2.4 后端依赖安装
确保虚拟环境已激活。
```bash
pip install -r requirements.txt
```
这将安装项目运行所需的所有后端 Python 包，如 Flask, Pydantic, Pillow 等。

### 2.5 前端依赖安装
本项目前端主要使用原生 JavaScript、HTML 和 CSS，不依赖 npm/yarn 进行包管理或构建。所有前端资源直接由后端 Flask 应用提供。因此，通常无需额外的前端依赖安装步骤。

如果将来引入需要构建的前端工具链 (如 Sass, Webpack, Parcel 等)，此部分需要更新。

## 3. 项目目录结构

以下是项目主要顶层目录及其核心职责的简要说明：

*   `backend/`: 包含所有后端 Python 代码。
    *   `app.py`: Flask 应用的入口和主要配置文件。
    *   `config.py`: 后端应用的详细配置模块 ([`backend/config.py`](../../backend/config.py))，定义了如 `SecurityConfig`, `ServerConfig`, `WebConfig`, `FeedbackConfig` 等，可通过 `ConfigManager` 访问。
    *   `feedback_handler.py`: 处理反馈提交的核心逻辑。
    *   `server_manager.py`: 管理后端服务器实例的生命周期。
    *   `routes/`: 存放 Flask 路由定义文件。
    *   `security/`: 包含安全相关的模块，如 CSRF 保护。
    *   `utils/`: 存放后端工具函数和辅助模块。
    *   `request_processing/`: 包含请求数据提取和处理相关的模块。
*   `frontend/`: 包含所有前端资源。
    *   `static/`: 存放静态文件。
        *   `css/`: 存放 CSS 样式文件。
        *   `js/`: 存放 JavaScript 文件。
            *   `feedback-main.js`: 前端应用的主要 JavaScript 入口。
            *   `config/app-config.js`: 前端应用的配置文件 ([`frontend/static/js/config/app-config.js`](../../frontend/static/js/config/app-config.js))，包含超时、重试等相关常量。
            *   `modules/`: 存放旧的或通用的前端 JS 模块 (例如，原 `timeout-handler.js` 的部分功能可能在此)。
            *   `timeout/`: 包含重构后的模块化超时处理逻辑，如 `index.js` (主入口), `countdown.js`, `activity.js`, `submission.js`, `backup.js`, `ui.js`。
    *   `templates/`: 存放 Flask 使用的 HTML 模板文件 (例如 `feedback.html`)。
*   `tests/`: 包含所有测试代码。
    *   `run_tests.py`: 用于执行测试套件的脚本。
    *   `test_requirements.txt`: 测试环境所需的 Python 依赖 ([`tests/test_requirements.txt`](../../tests/test_requirements.txt))。
    *   `conftest.py`: Pytest 的配置文件，用于定义 fixtures 等。
    *   `e2e/`: 存放端到端 (End-to-End) 测试脚本，例如使用 Selenium 进行 UI 测试 (`test_session_behavior_ui.py`)。
    *   `integration/`: 存放集成测试脚本。
    *   `unit/`: 存放单元测试脚本，覆盖前后端模块。
    *   `project_validation/`: 存放项目结构、规范等相关的验证脚本。
*   `docs/`: 包含所有项目文档。
    *   `api/reference.md`: 详细的后端 API 参考文档 ([`docs/api/reference.md`](../api/reference.md))。
    *   `guides/developer_guide.md`: 本开发者指南。
    *   `refactoring/`: 包含重构相关的计划和报告，如 `approved_execution_plan.md`。
    *   `Unified TODO List.md`: 项目统一的待办事项列表。
*   `requirements.txt`: 项目后端运行所需的 Python 依赖列表 ([`requirements.txt`](../../requirements.txt))。
*   `.venv/`: (通常在 `.gitignore` 中) Python 虚拟环境目录。

**关键配置文件:**
*   后端配置: [`backend/config.py`](../../backend/config.py)
*   前端配置: [`frontend/static/js/config/app-config.js`](../../frontend/static/js/config/app-config.js)

## 4. 后端开发指引

### 4.1 后端架构简介
项目后端基于 Flask 框架构建。主要组件包括：
*   **应用入口:** [`backend/app.py`](../../backend/app.py) 初始化 Flask 应用，加载配置，注册蓝图或路由。
*   **路由定义:** 通常在 `backend/routes/` 目录下的模块中定义，将 HTTP 请求映射到相应的处理函数。
*   **请求处理:** 例如 [`backend/feedback_handler.py`](../../backend/feedback_handler.py) 负责处理核心的反馈提交逻辑。
*   **服务器管理:** [`backend/server_manager.py`](../../backend/server_manager.py) 和 [`backend/server_pool.py`](../../backend/server_pool.py) (如果存在) 可能用于管理服务器实例或连接池。
*   **配置管理:** 通过 [`backend/config.py`](../../backend/config.py) 中的 `ConfigManager` 统一管理应用配置。

### 4.2 启动后端开发服务器
通常，可以通过直接运行 Flask 应用的入口文件来启动开发服务器。
在项目根目录下，并确保虚拟环境已激活：
```bash
python backend/app.py
```
或者，如果项目配置了 Flask CLI 命令 (例如通过 `FLASK_APP` 环境变量)：
```bash
flask run
```
请查阅 [`backend/app.py`](../../backend/app.py) 或项目根目录下的 `README.md` (如果存在) 获取确切的启动命令。服务器默认可能运行在 `http://127.0.0.1:5000/` (具体端口和主机请参考 [`backend/config.py`](../../backend/config.py) 中的 `WebConfig`)。

### 4.3 主要后端模块
*   [`app.py`](../../backend/app.py): Flask 应用实例和主配置。
*   [`server_manager.py`](../../backend/server_manager.py): 负责管理服务器的启动、停止和健康检查等。
*   [`feedback_handler.py`](../../backend/feedback_handler.py): 实现处理用户反馈的核心逻辑，包括数据验证、文件保存等。
*   `routes/` (目录): 包含各个功能的路由定义，例如处理 `/submit_feedback`, `/ping` 等请求。
*   [`config.py`](../../backend/config.py): 定义和管理所有后端配置。
*   `security/` (目录): 包含 CSRF 防护等安全相关实现。

### 4.4 API 接口信息
详细的后端 API 接口信息（包括端点、请求/响应格式、参数等）请参阅：
*   **API 参考文档:** [`docs/api/reference.md`](../api/reference.md)

## 5. 前端开发指引

### 5.1 前端代码组织结构
前端代码主要位于 `frontend/` 目录下：
*   **HTML 模板:** 存放在 `frontend/templates/`，由 Flask 后端渲染。主页面通常是 `feedback.html`。
*   **静态资源:** 存放在 `frontend/static/`。
    *   `css/`: 存放项目的 CSS 样式表。
    *   `js/`: 存放 JavaScript 代码。
        *   `feedback-main.js`: 作为主要的 JavaScript 文件，负责初始化页面功能、事件绑定和协调各个模块。
        *   `config/app-config.js`: 存储前端应用的配置常量，如 API 端点、超时时间、重试次数等。
        *   `modules/`: 可能包含一些通用的 UI 组件、工具函数或旧版模块。
        *   `timeout/`: 存放经过模块化重构的超时处理逻辑。该目录下的文件 (如 `index.js`, `countdown.js`, `activity.js`, `submission.js`, `backup.js`, `ui.js`) 各司其职，共同实现复杂的超时捕获和数据提交流程。这种模块化设计旨在提高代码的可维护性和可测试性。

### 5.2 前端资源服务方式
所有前端静态资源（CSS, JavaScript, 图片等）均由后端 Flask 应用通过其静态文件处理机制提供。Flask 会自动处理 `frontend/static/` 目录下的文件请求。

### 5.3 前端构建/编译
当前项目的前端部分不涉及复杂的构建或编译步骤 (如 Babel 转译、Webpack 打包、Sass/Less 编译等)。JavaScript 代码直接以 ES6+ 模块的形式编写并在现代浏览器中运行。

如果将来引入这些工具，本节需要更新相关命令和说明。

## 6. 测试指南

### 6.1 运行单元测试
项目使用 Pytest 进行单元测试。
1.  **安装测试依赖:** 确保虚拟环境已激活，并安装测试所需的额外包：
    ```bash
    pip install -r tests/test_requirements.txt
    ```
    这会安装 `pytest`, `pytest-cov`, `pytest-mock` 等。
2.  **运行测试:** 在项目根目录下执行：
    ```bash
    pytest
    ```
    或者，若要包含覆盖率报告：
    ```bash
    pytest --cov=backend --cov=frontend tests/unit/
    ```
    (请根据实际需要调整 `--cov` 参数以指定覆盖率报告的范围)

单元测试脚本位于 `tests/unit/` 目录下，分别针对后端和前端的模块。

### 6.2 运行端到端 (E2E) 测试
项目使用 Pytest 和 Selenium 进行端到端测试，模拟用户在浏览器中的操作。
1.  **环境准备:**
    *   确保已安装测试依赖 (见 6.1)。
    *   确保已安装合适的 WebDriver (如 ChromeDriver, GeckoDriver) 并已将其路径添加到系统 PATH，或者在测试配置中指定其路径。WebDriver 的版本需要与你本地安装的浏览器版本兼容。
    *   确保后端开发服务器正在运行 (见 4.2)。
2.  **运行测试:** 在项目根目录下，并确保虚拟环境已激活，执行特定的 E2E 测试脚本，例如：
    ```bash
    pytest tests/e2e/test_session_behavior_ui.py
    ```
    或者运行所有 E2E 测试：
    ```bash
    pytest tests/e2e/
    ```
    **重要:** E2E 测试通常需要在已激活的 `.venv` Python 虚拟环境下执行，以确保测试脚本能正确找到项目代码和依赖。

## 7. 编码规范与贡献流程 (待补充)

*   **代码风格:**
    *   Python: 遵循 PEP 8。建议使用 Black, Flake8, Pylint 等工具进行格式化和检查。
    *   JavaScript: 遵循一致的风格 (例如，Prettier 或 ESLint 配置)。
*   **分支管理:** (例如，Gitflow: `main`, `develop`, `feature/xxx`, `fix/xxx`, `release/xxx`)
*   **代码审查:** (例如，所有合并到 `develop` 或 `main` 分支的代码都需要至少一个其他开发者的审查批准)
*   **提交信息规范:** (例如，遵循 Conventional Commits)

*(此部分内容待项目组讨论并确定具体规范后补充。)*

## 8. 常见问题解答 (FAQ) / 调试技巧 (待补充)

*(此部分内容将在开发过程中根据遇到的常见问题和有用的调试经验逐步补充。)*