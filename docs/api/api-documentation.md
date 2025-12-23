# GaiaRouter API 文档

## 概述

GaiaRouter API 提供统一的接口访问多个 AI 模型，支持 OpenAI、Anthropic、Google 和 OpenRouter 等提供商。

**Base URL**: `http://localhost:8000/v1`

**认证方式**: Bearer Token（API Key）

## 认证

所有 API 请求都需要在请求头中包含 API Key：

```
Authorization: Bearer sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## 通用响应格式

### 成功响应

大多数 API 返回 JSON 格式的数据。

### 错误响应

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

**HTTP 状态码**：

- `200` - 成功
- `201` - 创建成功
- `400` - 请求错误
- `401` - 认证错误
- `403` - 权限不足
- `404` - 资源不存在
- `422` - 验证错误
- `429` - 频率限制
- `500` - 服务器错误
- `504` - 超时错误

## API 端点

### 1. 聊天完成

#### POST /v1/chat/completions

创建聊天完成请求，支持普通模式和流式模式。

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
  "stream": false
}
```

**参数说明**：

- `model` (string, required): 模型标识符，格式：`{provider}/{model-name}`
- `messages` (array, required): 消息列表，至少 1 条
  - `role` (string, required): 角色，可选值：`system`, `user`, `assistant`
  - `content` (string, required): 消息内容
- `temperature` (float, optional): 温度参数，范围 0-2，默认 0.7
- `max_tokens` (integer, optional): 最大 token 数
- `top_p` (float, optional): Top-p 采样参数，范围 0-1
- `frequency_penalty` (float, optional): 频率惩罚，范围-2 到 2
- `presence_penalty` (float, optional): 存在惩罚，范围-2 到 2
- `stream` (boolean, optional): 是否使用流式响应，默认 false

**普通模式响应**：

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

**流式模式响应**（Server-Sent Events）：

```
data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1677652288,"model":"openai/gpt-4","choices":[{"index":0,"delta":{"content":"Hello"},"finish_reason":null}]}

data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1677652288,"model":"openai/gpt-4","choices":[{"index":0,"delta":{"content":"!"},"finish_reason":null}]}

data: [DONE]
```

**示例**：

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

### 2. 模型列表

#### GET /v1/models

获取所有可用的模型列表。

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
      "id": "anthropic/claude-3-opus",
      "object": "model",
      "created": 1677610602,
      "owned_by": "anthropic",
      "provider": "anthropic"
    }
  ]
}
```

**示例**：

```bash
curl -X GET http://localhost:8000/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### 3. API Key 管理

#### POST /v1/api-keys

创建新的 API Key。

**请求体**：

```json
{
  "name": "My API Key",
  "description": "API Key for production use",
  "permissions": ["read", "write"],
  "expires_at": "2024-12-31T23:59:59Z"
}
```

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

**注意**：`key`字段只在创建时返回一次，请妥善保存。

#### GET /v1/api-keys

查询 API Key 列表。

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

#### GET /v1/api-keys/{key_id}

查询单个 API Key 详情。

#### PATCH /v1/api-keys/{key_id}

更新 API Key 信息。

**请求体**（所有字段可选）：

```json
{
  "name": "Updated API Key Name",
  "description": "Updated description",
  "permissions": ["read"],
  "status": "inactive",
  "expires_at": "2025-12-31T23:59:59Z"
}
```

#### DELETE /v1/api-keys/{key_id}

删除 API Key（软删除）。

**响应**：

```json
{
  "message": "API Key deleted successfully"
}
```

### 4. 统计接口

#### GET /v1/api-keys/{key_id}/stats

获取 API Key 的使用统计信息。

**查询参数**：

- `start_date` (string, optional): 开始日期（ISO 8601 格式），默认 30 天前
- `end_date` (string, optional): 结束日期（ISO 8601 格式），默认今天
- `group_by` (string, optional): 分组方式，可选值：`day`, `week`, `month`, `model`, `provider`，默认`day`

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

#### GET /v1/stats

获取全局统计信息。

**查询参数**：

- `start_date` (string, optional): 开始日期（ISO 8601 格式）
- `end_date` (string, optional): 结束日期（ISO 8601 格式）
- `group_by` (string, optional): 分组方式，可选值：`day`, `week`, `month`, `provider`

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

## 支持的模型

### OpenAI

- `openai/gpt-4`
- `openai/gpt-3.5-turbo`

### Anthropic

- `anthropic/claude-3-opus`
- `anthropic/claude-3-sonnet`

### Google

- `google/gemini-pro`

### OpenRouter

- `openrouter/meta-llama/llama-3-70b-instruct`
- 更多模型请参考 OpenRouter 文档

## 错误代码

- `model_not_found`: 模型不存在
- `invalid_api_key`: API Key 无效
- `authentication_error`: 认证错误
- `rate_limit_error`: 频率限制
- `organization_limit_error`: 组织使用限制
- `validation_error`: 验证错误
- `timeout_error`: 超时错误
- `server_error`: 服务器错误

## 速率限制

- 默认限制：每分钟 100 个请求
- 超出限制时返回 429 状态码

## 示例代码

### Python

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

### JavaScript

```javascript
const response = await fetch("http://localhost:8000/v1/chat/completions", {
  method: "POST",
  headers: {
    Authorization: "Bearer YOUR_API_KEY",
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    model: "openai/gpt-4",
    messages: [{ role: "user", content: "Hello!" }],
  }),
});

const data = await response.json();
console.log(data);
```

### cURL

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

## 更多信息

- 项目文档：`docs/`
- 用户指南：`docs/user-guide/user-guide.md`
- 部署指南：`docs/deployment/deployment-guide.md`
