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

**权限要求**: Admin

**请求体**：

```json
{
  "organization_id": "org_1234567890abcdef"
}
```

**参数说明**：

- `organization_id` (string, required): 所属组织 ID

**响应**：

```json
{
  "id": "ak_1234567890abcdef",
  "organization_id": "org_1234567890abcdef",
  "organization_name": "My Organization",
  "name": "My Organization API Key",
  "description": "Auto-generated API Key for My Organization",
  "key": "sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "permissions": ["read", "write"],
  "status": "active",
  "created_at": "2024-01-01T00:00:00Z",
  "expires_at": null,
  "last_used_at": null,
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**业务规则**：

- **一个组织一个 API Key**：每个组织只能创建一个活跃的 API Key。如果组织已有活跃的 API Key，再次创建会返回错误。
- **自动生成字段**：
  - `name`: 自动生成为 `{组织名} API Key`
  - `description`: 自动生成为 `Auto-generated API Key for {组织名}`
  - `permissions`: 固定为 `["read", "write"]`
  - `expires_at`: 固定为 `null`（永不过期）

**安全说明**：

- **重要**：`key` 字段**仅在创建时返回一次**，请务必妥善保存。
- 后续查询（列表和详情接口）不会返回 `key` 字段（返回 `null`）。
- 如果丢失 API Key，唯一的解决方案是删除旧的并创建新的。

**状态码**：

- `201`: 创建成功
- `400`: 请求参数错误或组织已有 API Key
- `401`: 未认证
- `403`: 权限不足（非 Admin 用户）
- `404`: 组织不存在

**错误示例**：

```json
{
  "detail": "Organization already has an API Key. Each organization can only have one API Key."
}
```

#### 4.2 查询 API Key 列表

获取 API Key 列表。

**Endpoint**: `GET /v1/api-keys`

**查询参数**：

- `page` (integer, optional): 页码，默认 1
- `limit` (integer, optional): 每页数量，默认 20，最大 100
- `status` (string, optional): 状态筛选，可选值：`active`, `inactive`, `expired`
- `search` (string, optional): 名称或描述搜索
- `organization_id` (string, optional): 按组织 ID 筛选

**响应**：

```json
{
  "data": [
    {
      "id": "ak_1234567890abcdef",
      "organization_id": "org_1234567890abcdef",
      "organization_name": "My Organization",
      "name": "My Organization API Key",
      "description": "Auto-generated API Key for My Organization",
      "key": null,
      "permissions": ["read", "write"],
      "status": "active",
      "created_at": "2024-01-01T00:00:00Z",
      "expires_at": null,
      "last_used_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
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

**注意**：出于安全考虑，`key` 字段始终返回 `null`。完整的 API Key 仅在创建时返回一次。

**状态码**：

- `200`: 成功
- `401`: 未认证

#### 4.3 查询单个 API Key

获取单个 API Key 详情。

**Endpoint**: `GET /v1/api-keys/{key_id}`

**响应**：

```json
{
  "id": "ak_1234567890abcdef",
  "organization_id": "org_1234567890abcdef",
  "organization_name": "My Organization",
  "name": "My Organization API Key",
  "description": "Auto-generated API Key for My Organization",
  "key": null,
  "permissions": ["read", "write"],
  "status": "active",
  "created_at": "2024-01-01T00:00:00Z",
  "expires_at": null,
  "last_used_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**注意**：出于安全考虑，`key` 字段始终返回 `null`。完整的 API Key 仅在创建时返回一次。

**状态码**：

- `200`: 成功
- `401`: 未认证
- `404`: API Key 不存在

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

### 6. 组织管理接口

#### 6.1 创建组织

创建新的组织。

**Endpoint**: `POST /v1/organizations`

**权限要求**: Admin

**请求体**：

```json
{
  "name": "My Organization",
  "description": "Organization for production use",
  "monthly_requests_limit": 10000,
  "monthly_tokens_limit": 1000000,
  "monthly_cost_limit": 1000.0
}
```

**参数说明**：

- `name` (string, required): 组织名称
- `description` (string, optional): 组织描述
- `monthly_requests_limit` (integer, optional): 月度请求次数限制，不设置则无限制
- `monthly_tokens_limit` (integer, optional): 月度 Token 限制，不设置则无限制
- `monthly_cost_limit` (number, optional): 月度费用限制（美元），不设置则无限制

**响应**：

```json
{
  "id": "org_1234567890abcdef",
  "name": "My Organization",
  "description": "Organization for production use",
  "admin_user_id": null,
  "status": "active",
  "monthly_requests_limit": 10000,
  "monthly_tokens_limit": 1000000,
  "monthly_cost_limit": 1000.0,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**状态码**：

- `201`: 创建成功
- `400`: 请求参数错误
- `401`: 未认证
- `403`: 权限不足（非 Admin 用户）

#### 6.2 查询组织列表

获取组织列表。

**Endpoint**: `GET /v1/organizations`

**查询参数**：

- `page` (integer, optional): 页码，默认 1
- `limit` (integer, optional): 每页数量，默认 20，最大 100
- `status` (string, optional): 状态筛选，可选值：`active`, `inactive`
- `search` (string, optional): 名称或描述搜索

**响应**：

```json
{
  "data": [
    {
      "id": "org_1234567890abcdef",
      "name": "My Organization",
      "description": "Organization for production use",
      "admin_user_id": null,
      "status": "active",
      "monthly_requests_limit": 10000,
      "monthly_tokens_limit": 1000000,
      "monthly_cost_limit": 1000.0,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
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

**状态码**：

- `200`: 成功
- `401`: 未认证

#### 6.3 查询单个组织

获取单个组织详情。

**Endpoint**: `GET /v1/organizations/{org_id}`

**响应**：

```json
{
  "id": "org_1234567890abcdef",
  "name": "My Organization",
  "description": "Organization for production use",
  "admin_user_id": null,
  "status": "active",
  "monthly_requests_limit": 10000,
  "monthly_tokens_limit": 1000000,
  "monthly_cost_limit": 1000.0,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**状态码**：

- `200`: 成功
- `401`: 未认证
- `404`: 组织不存在

#### 6.4 更新组织

更新组织信息。

**Endpoint**: `PATCH /v1/organizations/{org_id}`

**权限要求**: Admin

**请求体**：

```json
{
  "name": "Updated Organization Name",
  "description": "Updated description",
  "status": "active",
  "monthly_requests_limit": 20000,
  "monthly_tokens_limit": 2000000,
  "monthly_cost_limit": 2000.0
}
```

**参数说明**：所有参数都是可选的，只更新提供的字段。

- `name` (string, optional): 组织名称
- `description` (string, optional): 描述
- `admin_user_id` (string, optional): 管理员用户 ID
- `status` (string, optional): 状态，可选值：`active`, `inactive`
- `monthly_requests_limit` (integer, optional): 月度请求次数限制
- `monthly_tokens_limit` (integer, optional): 月度 Token 限制
- `monthly_cost_limit` (number, optional): 月度费用限制

**响应**：

```json
{
  "id": "org_1234567890abcdef",
  "name": "Updated Organization Name",
  "description": "Updated description",
  "admin_user_id": null,
  "status": "active",
  "monthly_requests_limit": 20000,
  "monthly_tokens_limit": 2000000,
  "monthly_cost_limit": 2000.0,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-16T10:00:00Z"
}
```

**状态码**：

- `200`: 成功
- `400`: 请求参数错误
- `401`: 未认证
- `403`: 权限不足
- `404`: 组织不存在

#### 6.5 删除组织

删除组织（软删除，更新状态为 inactive）。

**Endpoint**: `DELETE /v1/organizations/{org_id}`

**权限要求**: Admin

**响应**：

```json
{
  "message": "Organization deleted successfully"
}
```

**状态码**：

- `200`: 删除成功
- `401`: 未认证
- `403`: 权限不足
- `404`: 组织不存在

**注意**：删除组织不会删除其关联的 API Key，但会将组织状态设置为 `inactive`。

#### 6.6 查询组织统计

获取组织的使用统计信息（聚合该组织所有 API Key 的统计）。

**Endpoint**: `GET /v1/organizations/{org_id}/stats`

**查询参数**：

- `start_date` (string, optional): 开始日期（ISO 8601 格式），默认 30 天前
- `end_date` (string, optional): 结束日期（ISO 8601 格式），默认今天
- `group_by` (string, optional): 分组方式，可选值：`day`, `week`, `month`, `model`, `provider`，默认 `day`

**响应**：

```json
{
  "organization_id": "org_1234567890abcdef",
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

**状态码**：

- `200`: 成功
- `400`: 参数错误（如日期格式错误）
- `401`: 未认证
- `404`: 组织不存在

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
