# API 参考文档

本文档详细描述了项目后端提供的所有HTTP API端点。

## 1. 提交反馈

此API端点用于接收用户提交的反馈信息，包括文本和图片。

*   **功能描述:** 接收并处理用户通过前端界面提交的反馈数据，或由前端超时机制自动捕获的数据。
*   **HTTP方法:** `POST`
*   **URL路径:** `/submit_feedback`

### 请求

#### 请求头 (Request Headers)

| Header        | 类型   | 是否必需 | 描述                                     |
|---------------|--------|----------|------------------------------------------|
| `Content-Type`| string | 是       | 通常为 `multipart/form-data` (当包含图片时) 或 `application/json` (当仅有文本或特殊通知时)。服务器会根据实际情况处理。 |
| `X-CSRFToken` | string | 是       | 用于防止跨站请求伪造的CSRF令牌。此令牌通常在加载主页面时由服务器提供。 |

#### 请求体 (Request Body)

根据 `Content-Type`，请求体可以是 `multipart/form-data` 或 `application/json`。

**1. 当 `Content-Type` 为 `multipart/form-data` (主要用于前端表单提交，包括超时捕获):**

| 字段名                 | 类型        | 是否必需 | 描述                                                                 |
|------------------------|-------------|----------|----------------------------------------------------------------------|
| `textFeedback`         | string      | 否       | 用户输入的文本反馈内容。                                                     |
| `images`               | File array  | 否       | 用户上传的图片文件列表。服务器端会验证文件类型和大小。允许的图片类型包括: `png`, `jpg`, `jpeg`, `gif`, `bmp`, `webp`。 |
| `is_timeout_capture`   | string      | 否       | 指示此反馈是否由前端超时机制自动捕获。如果存在且值为 `"true"`，则标记为超时捕获。        |
| `source_event`         | string      | 否       | 触发反馈提交的事件来源描述，例如 `"frontend_timeout"`。                             |
| `csrf_token`           | string      | 是       | CSRF令牌，与 `X-CSRFToken` 请求头中的值相同，用于表单提交时的CSRF验证。             |
| `timestamp`            | string      | 否       | 客户端生成的时间戳 (ISO 8601格式)，例如 `2025-06-07T10:00:00.000Z`。服务器也会记录接收时间。 |

**2. 当 `Content-Type` 为 `application/json` (主要用于特殊通知，如会话关闭):**

*   **会话关闭通知:**
    ```json
    {
        "status": "session_closed"
    }
    ```
    当服务器收到此格式的JSON请求时，会触发会话关闭处理逻辑，例如释放相关资源。

*   **纯文本反馈 (理论上支持，但前端主要使用form-data):**
    ```json
    {
        "textFeedback": "用户的纯文本反馈内容。",
        "images": [
            {
                "filename": "image1.png",
                "data": "base64_encoded_image_data_string",
                "size": 102400
            }
        ]
    }
    ```
    *   `textFeedback` (string, optional): 文本反馈。
    *   `images` (array of objects, optional): 图片对象列表。每个对象包含:
        *   `filename` (string): 图片文件名。
        *   `data` (string): Base64编码的图片数据。
        *   `size` (number): 图片大小（字节）。

### 响应

#### 成功响应 (Success Response)

*   **HTTP状态码:** `200 OK`
*   **响应体 (Response Body):** `application/json`
    ```json
    {
        "success": true,
        "message": "反馈提交成功！感谢您的反馈。"
    }
    ```
    或者，如果是会话关闭通知被成功处理：
    ```json
    {
        "success": true,
        "message": "窗口关闭处理完成"
    }
    ```

#### 错误响应 (Error Responses)

| HTTP状态码 | 描述                                       | 响应体示例 (`application/json`)                                                                 |
|------------|--------------------------------------------|-------------------------------------------------------------------------------------------------|
| `400 Bad Request` | 请求体解析失败或缺少必要参数 (具体错误信息在message中)。 | `{"success": false, "message": "提交失败: 无效的请求数据"}` (示例)                               |
| `403 Forbidden` | 请求来源验证失败 (非本地IP) 或 CSRF令牌无效。 | `{"success": false, "message": "请求来源验证失败"}` 或 `{"success": false, "message": "CSRF token missing or invalid"}` (后者为通用CSRF错误，具体由CSRF中间件决定) |
| `413 Payload Too Large` | 提交的数据总体积超过服务器限制 (默认为50MB)，或单个文件大小超过限制 (默认为16MB)。 | `{"success": false, "message": "数据大小超出限制"}`                                                  |
| `500 Internal Server Error` | 服务器内部处理错误。                         | `{"success": false, "message": "提交失败: [具体错误描述]"}`                                        |

### 使用示例 (curl - 表单数据)

```bash
curl -X POST http://localhost:5000/submit_feedback \
  -H "X-CSRFToken: <your_csrf_token_here>" \
  -F "textFeedback=这是一个测试反馈" \
  -F "images=@/path/to/your/image.png" \
  -F "csrf_token=<your_csrf_token_here>" \
  -F "is_timeout_capture=false" \
  -F "source_event=manual_submission"
```

## 2. 健康检查

此API端点用于检查后端服务的健康状态。

*   **功能描述:** 返回服务器当前状态和时间戳，用于监控和健康检查。
*   **HTTP方法:** `GET`
*   **URL路径:** `/ping`

### 请求

无特定请求参数或请求体。

### 响应

#### 成功响应 (Success Response)

*   **HTTP状态码:** `200 OK`
*   **响应体 (Response Body):** `application/json`
    ```json
    {
        "status": "ok",
        "timestamp": 1678886400.123456
    }
    ```
    *   `status` (string): 固定为 "ok" 表示服务正常。
    *   `timestamp` (number): 服务器当前时间的Unix时间戳。

#### 错误响应 (Error Responses)

通常情况下此接口不应返回错误，除非服务器完全无法响应。

## 3. 主页面

此端点提供反馈应用的前端界面。

*   **功能描述:** 返回渲染后的HTML主页面，用户可在此页面提交反馈。
*   **HTTP方法:** `GET`
*   **URL路径:** `/`

### 请求

无特定请求参数或请求体。

### 响应

#### 成功响应 (Success Response)

*   **HTTP状态码:** `200 OK`
*   **响应体 (Response Body):** `text/html`
    返回 `feedback.html` 页面的内容。页面中会内嵌一个CSRF令牌，用于后续的POST请求。

#### 错误响应 (Error Responses)

| HTTP状态码 | 描述                 |
|------------|----------------------|
| `404 Not Found` | 如果模板文件丢失。     |
| `500 Internal Server Error` | 服务器渲染模板时发生错误。 |