# GaiaRouter 数据流设计

## 请求数据流

### 1. 客户端请求

```
Client → POST /v1/chat/completions
{
  "model": "openai/gpt-4",
  "messages": [{"role": "user", "content": "Hello"}],
  "temperature": 0.7
}
```

### 2. API 层处理

**步骤 2.1: 请求接收**

```
HTTP Request → FastAPI/Express
→ Middleware (Auth, Logging)
→ ChatController.create_completion()
```

**步骤 2.2: 请求验证**

```python
ChatRequest(
    model="openai/gpt-4",
    messages=[Message(role="user", content="Hello")],
    temperature=0.7
)
→ 验证格式
→ 验证必需字段
```

### 3. 路由层处理

**步骤 3.1: 模型解析**

```python
ModelRouter.parse_model_id("openai/gpt-4")
→ ("openai", "gpt-4")
```

**步骤 3.2: 提供商选择**

```python
ModelRegistry.get_provider("openai/gpt-4")
→ OpenAIProvider(api_key="...", base_url="...")
```

### 4. 适配器层处理

**步骤 4.1: 请求转换**

```python
OpenAIRequestAdapter.adapt_request(ChatRequest)
→ {
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Hello"}],
    "temperature": 0.7
  }
```

### 5. 提供商层处理

**步骤 5.1: API 调用**

```python
OpenAIProvider.chat_completion(request_dict)
→ HTTP POST https://api.openai.com/v1/chat/completions
→ Headers: {"Authorization": "Bearer ..."}
→ Body: {...}
```

**步骤 5.2: 响应接收**

```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "gpt-4",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you?"
      }
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

### 6. 响应转换

**步骤 6.1: 响应适配**

```python
OpenAIResponseAdapter.adapt_response(openai_response)
→ ChatResponse(
    id="chatcmpl-123",
    model="openai/gpt-4",
    choices=[...],
    usage=Usage(...)
  )
```

### 7. 返回响应

```
ChatResponse → JSON
→ HTTP 200 OK
→ Client
```

## 错误处理数据流

### 错误场景 1: 模型不存在

```
1. Client Request: model="invalid/model"
2. Router.parse_model_id() → ("invalid", "model")
3. Registry.get_provider() → None
4. Raise ModelNotFoundError
5. Error Middleware → ErrorResponse
6. HTTP 404 {
     "error": {
       "message": "Model not found",
       "code": "model_not_found"
     }
   }
```

### 错误场景 2: API Key 无效

```
1. Provider.chat_completion()
2. External API → 401 Unauthorized
3. Raise AuthenticationError
4. Error Middleware → ErrorResponse
5. HTTP 401 {
     "error": {
       "message": "Invalid API key",
       "code": "authentication_error"
     }
   }
```

### 错误场景 3: 请求超时

```
1. Provider.chat_completion()
2. HTTP Request → Timeout (60s)
3. Raise TimeoutError
4. Error Middleware → ErrorResponse
5. HTTP 504 {
     "error": {
       "message": "Request timeout",
       "code": "timeout_error"
     }
   }
```

## 并发处理数据流

### 多请求并发

```
Request 1: openai/gpt-4 → Provider 1 → Async HTTP
Request 2: anthropic/claude → Provider 2 → Async HTTP
Request 3: google/gemini → Provider 3 → Async HTTP

→ 异步处理，不阻塞
→ 各自返回响应
```

## 日志数据流

### 请求日志

```
Request → Logging Middleware
→ {
    "timestamp": "2024-01-01T00:00:00Z",
    "method": "POST",
    "path": "/v1/chat/completions",
    "model": "openai/gpt-4",
    "status": "200",
    "duration_ms": 1500
  }
→ Logger → File/Console
```

### 错误日志

```
Exception → Error Middleware
→ {
    "timestamp": "2024-01-01T00:00:00Z",
    "error": "ModelNotFoundError",
    "message": "Model not found: invalid/model",
    "traceback": "..."
  }
→ Logger → File/Console
```

## 配置数据流

### 启动时配置加载

```
1. Application Start
2. Settings.from_env() / Settings.from_file()
3. Load API Keys from Environment
4. Load Models Config from YAML
5. Initialize ModelRegistry
6. Register all models
7. Ready to serve requests
```

## 缓存数据流（可选）

### 模型列表缓存

```
1. GET /v1/models
2. Check Cache
3. If cached → Return cached data
4. If not cached → Load from Registry → Cache → Return
```
