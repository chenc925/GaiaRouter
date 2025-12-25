# OpenRouter API 文档

## 基础信息

- **Base URL**: `http://localhost:8000`
- **API Version**: `v1`
- **Content-Type**: `application/json`

## 认证

所有 API 请求需要在 Header 中包含 API Key：

```
Authorization: Bearer YOUR_API_KEY
```

**注意**：API Key 需要通过管理接口创建，创建后用于后续请求的认证。

## 端点

### 1. 聊天完成

创建聊天完成请求。支持普通模式和流式模式。

**Endpoint**: `POST /v1/chat/completions`

**请求体**：

```json
{
  "model": "openai/gpt-4",
  "messages": [
    {
      "role": "user",
      "content": "Hello, world!"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 1000,
  "top_p": 1.0,
  "frequency_penalty": 0.0,
  "presence_penalty": 0.0,
  "stream": false
}
```

**参数说明**：

- `model` (string, required): 模型标识符，格式为 `{provider}/{model-name}`
- `messages` (array, required): 消息数组
  - `role` (string, required): 角色，可选值：`system`, `user`, `assistant`
  - `content` (string, required): 消息内容
- `temperature` (number, optional): 温度参数，范围 0-2，默认 1.0
- `max_tokens` (integer, optional): 最大 token 数
- `top_p` (number, optional): Top-p 采样参数
- `frequency_penalty` (number, optional): 频率惩罚
- `presence_penalty` (number, optional): 存在惩罚
- `stream` (boolean, optional): 是否使用流式响应，默认 `false`

#### 1.1 普通模式响应

当 `stream: false` 时，返回完整的响应：

```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "openai/gpt-4",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

#### 1.2 流式模式响应

当 `stream: true` 时，使用 Server-Sent Events (SSE) 格式返回流式响应：

**Content-Type**: `text/event-stream`

**响应格式**：

```
data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1677652288,"model":"openai/gpt-4","choices":[{"index":0,"delta":{"role":"assistant","content":"Hello"},"finish_reason":null}]}

data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1677652288,"model":"openai/gpt-4","choices":[{"index":0,"delta":{"content":"!"},"finish_reason":null}]}

data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1677652288,"model":"openai/gpt-4","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}

data: [DONE]
```

**流式响应说明**：

- 每个 `data:` 行包含一个 JSON 对象
- `delta` 字段包含增量内容
- 最后一个 chunk 的 `finish_reason` 不为 `null`
- 以 `data: [DONE]` 结束流

**状态码**：

- `200`: 成功（普通模式）
- `200`: 成功（流式模式，使用 SSE）
- `400`: 请求错误
- `401`: 认证失败
- `404`: 模型不存在
- `500`: 服务器错误
- `504`: 请求超时

### 2. 模型列表

获取可用的模型列表。

**Endpoint**: `GET /v1/models`

**响应**：

```json
{
  "data": [
    {
      "id": "openai/gpt-4",
      "object": "model",
      "created": 1677610602,
      "owned_by": "openai",
      "provider": "openai"
    },
    {
      "id": "openai/gpt-3.5-turbo",
      "object": "model",
      "created": 1677610602,
      "owned_by": "openai",
      "provider": "openai"
    },
    {
      "id": "anthropic/claude-3-opus",
      "object": "model",
      "created": 1677610602,
      "owned_by": "anthropic",
      "provider": "anthropic"
    }
  ]
}
```

**状态码**：

- `200`: 成功
- `500`: 服务器错误

### 3. 健康检查

检查服务健康状态。

**Endpoint**: `GET /health`

**响应**：

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 4. API Key 管理接口

#### 4.1 创建 API Key

创建新的 API Key。

**Endpoint**: `POST /v1/api-keys`

**请求体**：

```json
{
  "name": "My API Key",
  "description": "API Key for production use",
  "permissions": ["read", "write"],
  "expires_at": "2024-12-31T23:59:59Z"
}
```

**参数说明**：

- `name` (string, required): API Key 名称
- `description` (string, optional): API Key 描述
- `permissions` (array, optional): 权限列表，可选值：`read`, `write`, `admin`，默认 `["read", "write"]`
- `expires_at` (string, optional): 过期时间（ISO 8601 格式），不设置则永不过期

**响应**：

```json
{
  "id": "ak_1234567890abcdef",
  "name": "My API Key",
  "description": "API Key for production use",
  "key": "sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "permissions": ["read", "write"],
  "status": "active",
  "created_at": "2024-01-01T00:00:00Z",
  "expires_at": "2024-12-31T23:59:59Z"
}
```

**注意**：`key` 字段只在创建时返回一次，请妥善保存。

#### 4.2 查询 API Key 列表

获取 API Key 列表。

**Endpoint**: `GET /v1/api-keys`

**查询参数**：

- `page` (integer, optional): 页码，默认 1
- `limit` (integer, optional): 每页数量，默认 20，最大 100
- `status` (string, optional): 状态筛选，可选值：`active`, `inactive`, `expired`
- `search` (string, optional): 名称或描述搜索

**响应**：

```json
{
  "data": [
    {
      "id": "ak_1234567890abcdef",
      "name": "My API Key",
      "description": "API Key for production use",
      "permissions": ["read", "write"],
      "status": "active",
      "created_at": "2024-01-01T00:00:00Z",
      "expires_at": "2024-12-31T23:59:59Z",
      "last_used_at": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1,
    "pages": 1
  }
}
```

#### 4.3 查询单个 API Key

获取单个 API Key 详情。

**Endpoint**: `GET /v1/api-keys/{key_id}`

**响应**：

```json
{
  "id": "ak_1234567890abcdef",
  "name": "My API Key",
  "description": "API Key for production use",
  "permissions": ["read", "write"],
  "status": "active",
  "created_at": "2024-01-01T00:00:00Z",
  "expires_at": "2024-12-31T23:59:59Z",
  "last_used_at": "2024-01-15T10:30:00Z"
}
```

#### 4.4 更新 API Key

更新 API Key 信息。

**Endpoint**: `PATCH /v1/api-keys/{key_id}`

**请求体**：

```json
{
  "name": "Updated API Key Name",
  "description": "Updated description",
  "permissions": ["read"],
  "status": "inactive",
  "expires_at": "2025-12-31T23:59:59Z"
}
```

**参数说明**：所有参数都是可选的，只更新提供的字段。

**响应**：

```json
{
  "id": "ak_1234567890abcdef",
  "name": "Updated API Key Name",
  "description": "Updated description",
  "permissions": ["read"],
  "status": "inactive",
  "created_at": "2024-01-01T00:00:00Z",
  "expires_at": "2025-12-31T23:59:59Z",
  "updated_at": "2024-01-16T10:00:00Z"
}
```

#### 4.5 删除 API Key

删除 API Key。

**Endpoint**: `DELETE /v1/api-keys/{key_id}`

**响应**：

```json
{
  "message": "API Key deleted successfully"
}
```

### 5. 统计接口

#### 5.1 查询 API Key 使用统计

获取 API Key 的使用统计信息。

**Endpoint**: `GET /v1/api-keys/{key_id}/stats`

**查询参数**：

- `start_date` (string, optional): 开始日期（ISO 8601 格式），默认 30 天前
- `end_date` (string, optional): 结束日期（ISO 8601 格式），默认今天
- `group_by` (string, optional): 分组方式，可选值：`day`, `week`, `month`, `model`, `provider`，默认 `day`

**响应**：

```json
{
  "key_id": "ak_1234567890abcdef",
  "period": {
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-01-31T23:59:59Z"
  },
  "summary": {
    "total_requests": 1250,
    "total_prompt_tokens": 50000,
    "total_completion_tokens": 75000,
    "total_tokens": 125000,
    "total_cost": 12.5
  },
  "by_date": [
    {
      "date": "2024-01-01",
      "requests": 50,
      "prompt_tokens": 2000,
      "completion_tokens": 3000,
      "total_tokens": 5000,
      "cost": 0.5
    }
  ],
  "by_model": [
    {
      "model": "openai/gpt-4",
      "requests": 500,
      "prompt_tokens": 20000,
      "completion_tokens": 30000,
      "total_tokens": 50000,
      "cost": 5.0
    }
  ],
  "by_provider": [
    {
      "provider": "openai",
      "requests": 500,
      "prompt_tokens": 20000,
      "completion_tokens": 30000,
      "total_tokens": 50000,
      "cost": 5.0
    }
  ]
}
```

#### 5.2 查询全局统计

获取所有 API Key 的汇总统计。

**Endpoint**: `GET /v1/stats`

**查询参数**：

- `start_date` (string, optional): 开始日期
- `end_date` (string, optional): 结束日期
- `group_by` (string, optional): 分组方式

**响应**：

```json
{
  "period": {
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-01-31T23:59:59Z"
  },
  "summary": {
    "total_keys": 10,
    "active_keys": 8,
    "total_requests": 10000,
    "total_tokens": 1000000,
    "total_cost": 100.0
  },
  "by_provider": [
    {
      "provider": "openai",
      "requests": 5000,
      "tokens": 500000,
      "cost": 50.0
    }
  ]
}
```

## 错误响应

所有错误响应使用统一格式：

```json
{
  "error": {
    "message": "Error message",
    "type": "invalid_request_error",
    "code": "model_not_found"
  }
}
```

**错误类型**：

- `invalid_request_error`: 请求格式错误
- `authentication_error`: 认证错误
- `rate_limit_error`: 频率限制
- `server_error`: 服务器错误
- `timeout_error`: 超时错误

**错误代码**：

- `model_not_found`: 模型不存在
- `invalid_api_key`: API Key 无效
- `missing_required_field`: 缺少必需字段
- `invalid_parameter`: 参数无效

## 示例

### Python 示例

```python
import requests

url = "http://localhost:8000/v1/chat/completions"
headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
}
data = {
    "model": "openai/gpt-4",
    "messages": [
        {"role": "user", "content": "Hello!"}
    ]
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

### cURL 示例

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openai/gpt-4",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  }'
```
