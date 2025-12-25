# GaiaRouter Architecture

## System Overview

GaiaRouter is designed as a multi-layered AI model routing service that provides a unified interface to multiple AI providers. The architecture follows a clean separation of concerns with four main layers.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Applications                   │
│                    (Web, Mobile, APIs)                       │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                         API Layer                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  FastAPI Endpoints                                    │  │
│  │  • /v1/chat/completions                              │  │
│  │  • /v1/models                                        │  │
│  │  • /v1/api-keys                                      │  │
│  │  • /v1/organizations                                 │  │
│  │  • Authentication & Authorization                    │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                       Router Layer                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  • Model Selection                                    │  │
│  │  • Load Balancing                                    │  │
│  │  • Request Routing                                   │  │
│  │  • Error Handling & Fallback                         │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                      Adapter Layer                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Format Conversion                                    │  │
│  │  • OpenAI Format ←→ Provider Format                  │  │
│  │  • Request Transformation                            │  │
│  │  • Response Transformation                           │  │
│  │  • Streaming Adaptation                              │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                     Provider Layer                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ OpenAI   │  │Anthropic │  │  Google  │  │OpenRouter│   │
│  │ Provider │  │ Provider │  │ Provider │  │ Provider │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │   External AI APIs   │
                  │  (OpenAI, Claude,   │
                  │   Gemini, etc.)     │
                  └─────────────────────┘
```

## Core Components

### 1. API Layer (`src/gaiarouter/api/`)

The API layer handles all HTTP requests and provides RESTful endpoints:

- **Endpoints**:
  - Chat completion endpoints with streaming support
  - Model management
  - API key management
  - Organization management
  - Statistics and usage tracking

- **Responsibilities**:
  - Request validation
  - Authentication & authorization
  - Rate limiting
  - Request/response logging
  - Error handling

### 2. Router Layer (`src/gaiarouter/router/`)

The router layer manages model selection and request routing:

- **Functions**:
  - Model registration and lookup
  - Provider selection based on model ID
  - Load balancing (future enhancement)
  - Fallback handling when primary provider fails

- **Key Files**:
  - `model_router.py` - Model routing logic
  - Model registry management

### 3. Adapter Layer (`src/gaiarouter/adapters/`)

The adapter layer converts between different API formats:

- **Base Adapter** (`base.py`):
  - Abstract interface for all providers
  - Common transformation logic
  - Streaming support

- **Provider-Specific Adapters**:
  - `openai_adapter.py` - OpenAI format (passthrough)
  - `anthropic_adapter.py` - Claude format conversion
  - `google_adapter.py` - Gemini format conversion
  - `openrouter_adapter.py` - OpenRouter format handling

### 4. Provider Layer (`src/gaiarouter/providers/`)

The provider layer handles direct communication with AI APIs:

- **Base Provider** (`base.py`):
  - HTTP client setup
  - Error handling
  - Retry logic
  - Timeout management

- **Provider Implementations**:
  - `openai.py` - OpenAI API client
  - `anthropic.py` - Anthropic API client
  - `google.py` - Google AI API client
  - `openrouter.py` - OpenRouter API client

## Database Schema

### Core Tables

- **organizations** - Tenant organizations
- **users** - Admin users
- **api_keys** - API keys for authentication
- **models** - Available AI models
- **usage_stats** - Request statistics and usage tracking

See [Database Schema](database-schema.md) for detailed table definitions.

## Authentication & Authorization

### API Key Authentication

All API requests must include an API key in the Authorization header:

```
Authorization: Bearer sk-xxx...
```

### Permission Levels

- **read** - Read-only access to resources
- **write** - Create and modify resources
- **admin** - Full access including user management

## Request Flow

### Chat Completion Request

1. **Client Request** → API endpoint `/v1/chat/completions`
2. **Authentication** → Validate API key
3. **Authorization** → Check permissions and limits
4. **Model Routing** → Determine provider from model ID
5. **Adapter** → Convert request to provider format
6. **Provider** → Send request to external API
7. **Streaming** → Stream response chunks back to client
8. **Statistics** → Record usage metrics

### Streaming Support

GaiaRouter supports Server-Sent Events (SSE) for streaming responses:

```python
async def stream_chat_completion():
    async for chunk in provider.stream_chat():
        yield f"data: {json.dumps(chunk)}\n\n"
```

## Configuration

### Environment Variables

Configuration is managed through environment variables (`.env` file):

- **Database**: Connection settings
- **Provider API Keys**: Authentication for external APIs
- **Server Settings**: Port, host, CORS
- **Logging**: Log level and format

See [Configuration Guide](../getting-started/configuration.md) for details.

## Extension Points

### Adding New Providers

1. Create adapter in `src/gaiarouter/adapters/`
2. Create provider in `src/gaiarouter/providers/`
3. Register in model router
4. Add configuration in settings

See [Developer Guide](../development/adding-providers.md) for step-by-step instructions.

## Security Considerations

- **API Keys**: Stored hashed in database
- **Rate Limiting**: Per-key limits enforced
- **Input Validation**: All requests validated
- **CORS**: Configured for frontend domain
- **HTTPS**: Required in production

## Performance Considerations

- **Async I/O**: FastAPI with asyncio for concurrent requests
- **Connection Pooling**: Reused HTTP connections
- **Streaming**: Reduced latency with SSE
- **Database Indexing**: Optimized queries

## Monitoring & Logging

- **Structured Logging**: Using structlog
- **Usage Statistics**: Tracked per request
- **Error Tracking**: Comprehensive error logging
- **Health Checks**: `/health` endpoint

## Related Documentation

- [API Documentation](../api/api-documentation.md)
- [Development Guide](../development/README.md)
- [Deployment Guide](../deployment/deployment-guide.md)
