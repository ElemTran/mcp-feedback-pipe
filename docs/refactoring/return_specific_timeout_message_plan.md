# 返回特定超时消息的实现计划

## 目标

当用户反馈收集超时时：
1.  客户端浏览器窗口保持打开状态，不自动关闭。
2.  向调用 `collect_feedback` 工具的AI返回一个特定的、信息性的“超时”状态MCP消息，而不是抛出通用异常。

## 修改文件

*   [`src/mcp_feedback_pipe/server.py`](src/mcp_feedback_pipe/server.py)

## 具体修改步骤

1.  **定位 `collect_feedback` 函数**：
    在 `src/mcp_feedback_pipe/server.py` 文件中找到 `collect_feedback` 工具的定义。

2.  **修改超时处理逻辑**：
    *   在 `collect_feedback` 函数内部，找到处理 `server_manager.wait_for_feedback()` 返回结果的逻辑。
    *   当前处理超时的代码（当 `result is None` 时）是：
        ```python
        if result is None:
            raise Exception(f"操作超时（{timeout_seconds}秒），请重试")
        ```
    *   将上述代码块修改为以下逻辑，以返回一个特定的超时消息结构：
        ```python
        if result is None:
            # 返回一个特定的超时消息，而不是抛出异常
            timeout_message = f"操作超时（{timeout_seconds}秒），用户未提交反馈。"
            # 根据当前的返回结构 {"content": mcp_result}，我们需要将此消息放入一个列表中
            return {"content": [timeout_message]} 
        ```

## 修正后的美人鱼流程图

```mermaid
graph LR
    A["collect_feedback 调用 wait_for_feedback"] --> B{"wait_for_feedback 返回结果"};
    B -- "有反馈 (result is not None)" --> C["处理反馈 process_feedback_to_mcp"];
    C --> D["返回正常反馈内容"];
    B -- "超时 (result is None)" --> E["构造特定超时消息文本"];
    E --> F["返回包含超时消息的特定内容"];