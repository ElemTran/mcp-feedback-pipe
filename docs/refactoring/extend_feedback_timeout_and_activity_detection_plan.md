# 扩展反馈收集超时及用户活动检测功能实现计划

## 核心目标

1.  允许用户在前端界面动态修改反馈收集的超时时间。
2.  将用户在前端设置的新超时时间同步到后端，并影响后端实际的等待超时。
3.  当检测到用户在反馈页面活动时，前端倒计时暂停；用户不活动或页面不可见一段时间后，前端倒计时恢复。

## 阶段一：前端修改

### 1. 修改 HTML 模板 (`src/mcp_feedback_pipe/templates/feedback.html`)

*   **操作**: 在超时信息显示区域附近（例如 `id="timeoutInfo"` 的元素内部或紧随其后）添加一个新的数字输入框和“应用”按钮。
    ```html
    <div class="custom-timeout-controls" style="margin-top: 8px; display: flex; align-items: center; gap: 8px;">
        <label for="customTimeoutInput" style="font-size: 0.9em;">设置新超时 (秒):</label>
        <input type="number" id="customTimeoutInput" name="customTimeoutInput" min="30" style="width: 70px; padding: 4px;" value="{{ timeout_seconds }}">
        <button type="button" id="applyCustomTimeoutBtn" class="btn btn-small">应用</button>
    </div>
    ```

### 2. 修改 JavaScript (`src/mcp_feedback_pipe/static/js/modules/timeout-handler.js`)

*   **新增变量**:
    *   `isPaused = false;`
    *   `remainingTimeOnPause = 0;`
    *   `activityTimeout = null;` // 用于不活动检测的计时器
    *   `INACTIVITY_THRESHOLD = 60000;` // 例如，1分钟不活动则暂停 (可配置)
*   **修改 `initializeTimeoutHandler()`**:
    *   读取后端传入的初始超时值，启动倒计时。
    *   为 `applyCustomTimeoutBtn` 添加事件监听：
        *   点击时，读取并验证 `customTimeoutInput` 的值。
        *   更新前端的 `timeoutSeconds`, `initialTimeoutSeconds`。
        *   调用 `resetAndStartCountdown()` (新函数) 以应用新时间。
        *   使用 `fetch` API 向后端发送 POST 请求到 `/api/update_timeout`，请求体中包含新的超时秒数 (例如: `{ "new_timeout_seconds": newTimeoutValue }`) 和 CSRF 令牌。
    *   **新增用户活动检测逻辑**:
        *   监听 `mousemove`, `keydown`, `mousedown`, `scroll` 事件。在事件处理函数中：
            *   如果 `isPaused` 为 `true`，调用 `resumeCountdown()`。
            *   重置不活动计时器: `clearTimeout(activityTimeout); activityTimeout = setTimeout(pauseDueToInactivity, INACTIVITY_THRESHOLD);`
        *   监听 `visibilitychange` 事件：
            *   如果 `document.hidden` 为 `true`，调用 `pauseCountdown()`。
            *   如果 `document.hidden` 为 `false` 且之前是暂停的，调用 `resumeCountdown()` 并重置不活动计时器。
        *   初始启动不活动计时器: `activityTimeout = setTimeout(pauseDueToInactivity, INACTIVITY_THRESHOLD);`
*   **修改 `startCountdown()` (或重命名为 `updateIntervalCallback`)**:
    *   `setInterval` 的回调函数。
    *   在执行倒计时逻辑前检查 `if (isPaused) return;`。
    *   (原有逻辑) 计算剩余时间，更新界面，处理超时。
*   **新增 `resetAndStartCountdown()`**:
    *   `isPaused = false;`
    *   `startTime = Date.now();` // 重置开始时间
    *   `initialTimeoutSeconds = timeoutSeconds;` // 确保进度条基于新的总时长
    *   清除旧的 `timeoutInterval` (如果存在)。
    *   重新启动 `timeoutInterval = setInterval(updateIntervalCallback, 1000);`
    *   重置不活动计时器。
*   **新增 `pauseCountdown()`**:
    *   `if (isPaused) return;`
    *   `isPaused = true;`
    *   `remainingTimeOnPause = getRemainingTime();` // 保存当前剩余时间
    *   `clearInterval(timeoutInterval);`
    *   `timeoutInterval = null;`
    *   `clearTimeout(activityTimeout);`
    *   更新界面，例如显示“已暂停”。
*   **新增 `resumeCountdown()`**:
    *   `if (!isPaused) return;`
    *   `isPaused = false;`
    *   `startTime = Date.now() - (timeoutSeconds - remainingTimeOnPause) * 1000;` // 根据暂停时的剩余时间调整开始时间
    *   `initialTimeoutSeconds = timeoutSeconds;` // 确保进度条基于当前总时长
    *   `if (!timeoutInterval) { timeoutInterval = setInterval(updateIntervalCallback, 1000); }`
    *   重置不活动计时器: `activityTimeout = setTimeout(pauseDueToInactivity, INACTIVITY_THRESHOLD);`
    *   更新界面。
*   **新增 `pauseDueToInactivity()`**:
    *   调用 `pauseCountdown()`。
    *   可以添加一个提示，告知用户因为不活动已暂停。

## 阶段二：后端修改

### 3. 修改 `FeedbackApp` (`src/mcp_feedback_pipe/app.py`)

*   **操作**:
    *   在 `FeedbackApp.__init__` 中增加一个参数来接收 `ServerManager` 实例的引用，例如 `self.server_manager_ref = server_manager_instance`。
    *   添加一个新的 Flask 路由 `@app.route('/api/update_timeout', methods=['POST'])`：
        *   从 `request.get_json()` 获取 `new_timeout_seconds`。
        *   验证 CSRF 令牌 (可以使用 `self.csrf_protection.validate_token(request.headers.get('X-CSRF-Token'))`)。
        *   进行基本的超时值验证（例如，确保是正整数）。
        *   如果验证通过，调用 `self.server_manager_ref.update_active_timeout(new_timeout_seconds)`。
        *   返回 JSON 响应给前端，表明操作成功或失败。

### 4. 修改 `ServerManager` (`src/mcp_feedback_pipe/server_manager.py`)

*   **操作**:
    *   在 `ServerManager.__init__` 中添加新属性：
        *   `self.active_timeout_seconds = None` (用于存储当前会话的动态超时值)
        *   `self.timeout_update_event = threading.Event()` (用于通知 `wait_for_feedback` 超时已更新)
    *   在 `ServerManager.start_server` 方法中：
        *   将从工具参数传入的 `timeout_seconds` 初始化到 `self.active_timeout_seconds`。
        *   创建 `FeedbackApp` 实例时，将 `self` (即 `ServerManager` 实例) 传递过去: `FeedbackApp(..., server_manager_instance=self)`。
    *   新增方法 `update_active_timeout(self, new_timeout: int)`:
        *   `self.active_timeout_seconds = new_timeout`
        *   `self.timeout_update_event.set()` (发出事件信号，通知等待的线程)
    *   **核心修改**: 重写 `wait_for_feedback(self, timeout_seconds: int)` 方法 (原 `timeout_seconds` 参数可作为初始/默认值，但主要依赖 `self.active_timeout_seconds`):
        *   该方法将不再是一次性长阻塞。它会进入一个循环。
        *   循环的每次迭代：
            1.  清除 `self.timeout_update_event`。
            2.  计算当前迭代应该等待的短时间间隔 (例如1秒)。
            3.  调用 `self.feedback_handler.get_result(timeout=short_interval)`。
            4.  如果获取到结果，则返回结果。
            5.  检查 `self.timeout_update_event` 是否被设置。如果被设置，说明 `self.active_timeout_seconds` 可能已更新，需要重新计算总的剩余等待时间，并继续下一次迭代。
            6.  如果未获取结果且事件未设置，则从总的剩余等待时间中减去 `short_interval`。
            7.  如果总剩余等待时间耗尽，则循环结束，返回 `None` (超时)。
        *   需要仔细管理总的剩余等待时间，确保它能正确响应 `self.active_timeout_seconds` 的变化。

### 5. `FeedbackHandler` (`src/mcp_feedback_pipe/feedback_handler.py`)

*   **操作**: `get_result(self, timeout: int = 300)` 方法的 `timeout` 参数现在将被 `ServerManager` 的轮询逻辑以较小的值（如1秒）传入。其内部的 `self.result_queue.get(timeout=timeout)` 将因此成为短时阻塞。这部分不需要大改，只需确保它能正确处理短超时即可（目前实现已符合）。

## 最终版美人鱼流程图

```mermaid
graph TD
    subgraph "Frontend Interaction"
        A["用户打开反馈页"] --> B["HTML加载, JS初始化"];
        B --> C["显示初始倒计时 (基于 initial_timeout_from_backend)"];
        C --> C1["启动用户不活动检测计时器"];
        C1 --> D{"用户修改超时值?"};
        
        D -- "是" --> E["输入新值, 点击“应用”"];
        E --> F["JS: 更新前端倒计时显示, 重启倒计时"];
        F --> G["JS: fetch POST /api/update_timeout (新超时值 + CSRF)"];
        
        D -- "否" --> D1{"用户活动? (mousemove, keydown等)"};
        D1 -- "是" --> D2["JS: resumeCountdown (如果已暂停)"];
        D2 --> C1;
        D1 -- "否 (等待不活动计时器)" --> D3{"不活动超时?"};
        D3 -- "是" --> D4["JS: pauseCountdown"];
        D4 --> D1;
        
        D1 -- "页面可见性改变" --> D5{"页面是否隐藏?"};
        D5 -- "是 (隐藏)" --> D6["JS: pauseCountdown"];
        D6 --> D1;
        D5 -- "否 (可见)" --> D7["JS: resumeCountdown (如果已暂停)"];
        D7 --> C1;
    end

    subgraph "Backend API (app.py)"
        H["Flask: /api/update_timeout 接收请求"] --> I{"CSRF & 值验证"};
        I -- "通过" --> J["调用 ServerManager.update_active_timeout(新超时值)"];
        J --> K["返回成功/失败JSON给前端"];
        I -- "失败" --> L["返回错误JSON给前端"];
    end

    subgraph "Backend Logic (server_manager.py)"
        M["start_server: 初始化 active_timeout_seconds, 创建FeedbackApp(self)"]
        N["update_active_timeout(新超时值)被调用"] --> O["更新 self.active_timeout_seconds"];
        O --> P["设置 self.timeout_update_event"];
        
        Q["wait_for_feedback 开始"] --> R{"轮询循环 (基于 active_timeout_seconds)"};
        R -- "计算短轮询间隔" --> S["feedback_handler.get_result(short_interval)"];
        S -- "收到反馈" --> T["返回反馈结果"];
        S -- "短超时/无反馈" --> U{"timeout_update_event 被设置?"};
        U -- "是" --> V["清除事件, 重新计算总剩余时间 (基于更新后的 active_timeout_seconds)"];
        V --> R;
        U -- "否" --> W{"总剩余时间 > 0?"};
        W -- "是" --> X["减少总剩余时间"] --> R;
        W -- "否 (真超时)" --> Y["返回 None"];
    end
    
    G --> H;
    M --> Q;