# OpenRouter 简单版本 - 功能规范

## 功能概述

OpenRouter 简单版本是一个 AI 模型路由服务，提供统一的 API 接口，允许用户通过单一端点访问多个 AI 模型（如 OpenAI、Anthropic、Google 等）。该服务简化了多模型切换的复杂性，提供统一的请求格式和响应格式。

## 功能价值

- **统一接口**：提供统一的 API 接口，无需为每个模型维护不同的客户端
- **模型切换**：轻松切换不同的 AI 模型，无需修改应用代码
- **成本优化**：可以根据需求选择不同成本的模型
- **简化集成**：减少与多个模型提供商集成的复杂性

## 需求描述

### 核心功能

1. **模型路由**

   - 根据请求中的模型标识符，将请求路由到对应的模型提供商
   - 支持多个模型提供商（OpenAI、Anthropic、Google、OpenRouter 等）
   - 支持模型列表查询

2. **请求转发**

   - 接收标准化的请求格式
   - 将请求转换为目标模型的格式
   - 转发请求到目标模型 API
   - 处理响应并转换为统一格式

3. **API 接口**

   - 提供 RESTful API 接口（基于 Python FastAPI 框架）
   - 支持聊天完成（Chat Completion）功能
   - 支持流式（Stream）响应
   - 支持模型列表查询接口

4. **配置管理**

   - 支持模型配置管理
   - 支持模型提供商配置

5. **API Key 管理**

   - 支持 API Key 的创建、查询、更新、删除
   - 支持 API Key 的启用/禁用
   - 支持 API Key 的权限管理
   - 提供 API Key 的后台管理界面或 API 接口

6. **统计功能**

   - 支持 API Key 使用统计（请求次数、Token 使用量、费用等）
   - 支持按时间范围查询统计
   - 支持按模型提供商统计
   - 提供统计数据的 API 接口

7. **组织管理**
   - 支持组织的创建、查询、更新、删除
   - 支持为组织分配 API Key
   - 支持为组织设置 API 使用次数限制
   - 支持组织级别的统计和监控
   - 提供组织管理的后台界面（基于 Arco Design Vue 框架）

## 输入输出

### 聊天完成接口

**普通模式请求格式**：

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

**普通模式响应格式**：

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

**流式模式请求格式**：

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
  "stream": true
}
```

**流式模式响应格式**（Server-Sent Events）：

```
data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1677652288,"model":"openai/gpt-4","choices":[{"index":0,"delta":{"role":"assistant","content":"Hello"},"finish_reason":null}]}

data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1677652288,"model":"openai/gpt-4","choices":[{"index":0,"delta":{"content":"!"},"finish_reason":null}]}

data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1677652288,"model":"openai/gpt-4","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}

data: [DONE]
```

### 模型列表接口

**请求**：`GET /v1/models`

**响应格式**：

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

## 业务规则

1. **模型标识格式**：`{provider}/{model-name}`，例如 `openai/gpt-4`
2. **请求验证**：必须验证请求格式和必需字段
3. **错误处理**：统一的错误响应格式
4. **API Key 管理**：每个模型提供商需要配置对应的 API Key
5. **请求超时**：设置合理的请求超时时间（默认 60 秒）
6. **重试机制**：支持失败重试（最多 3 次）

## 异常处理

### 错误响应格式

```json
{
  "error": {
    "message": "Error message",
    "type": "invalid_request_error",
    "code": "model_not_found"
  }
}
```

### 常见错误类型

- `model_not_found`：模型不存在
- `invalid_request`：请求格式错误
- `authentication_error`：API Key 无效
- `rate_limit_error`：请求频率超限
- `server_error`：服务器内部错误
- `timeout_error`：请求超时

## 验收标准

1. ✅ 能够成功路由请求到指定的模型提供商
2. ✅ 支持至少 4 个模型提供商（OpenAI、Anthropic、Google、OpenRouter）
3. ✅ 提供统一的请求和响应格式
4. ✅ 正确处理各种错误情况
5. ✅ API 响应时间 < 2 秒（不含模型处理时间）
6. ✅ 支持模型列表查询
7. ✅ 提供完整的 API 文档
8. ✅ 支持 API Key 的完整生命周期管理
9. ✅ 支持 API Key 使用统计和查询
10. ✅ 提供 API Key 管理接口
11. ✅ 支持流式（Stream）响应
12. ✅ 支持组织管理和组织级别的 API Key 分配
13. ✅ 支持组织级别的使用次数限制和统计
14. ✅ 提供基于 Arco Design Vue 的后台管理界面

## 技术约束

- **后端框架**：Python FastAPI
- **数据库**：阿里云 RDS（MySQL/PostgreSQL）
- **前端框架**：Arco Design Vue
- **API 协议**：RESTful API，支持流式响应（Server-Sent Events）
- **配置管理**：支持环境变量配置
- **日志**：提供日志记录功能
- **部署**：支持 Docker 部署

## 相关文档

- 设计文档：`../../designs/openrouter/`
- 任务分解：`../../tasks/openrouter/`
- API 文档：`api.md`
