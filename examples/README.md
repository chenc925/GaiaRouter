# GaiaRouter Examples

This directory contains example code demonstrating how to use the GaiaRouter API.

## Prerequisites

Before running these examples, make sure you have:

1. GaiaRouter backend running (see [Getting Started](../docs/getting-started/README.md))
2. A valid API key (create one in the admin dashboard)
3. Python 3.11+ installed
4. Required packages: `pip install httpx`

## Setting Up

Export your API key as an environment variable:

```bash
export GAIAROUTER_API_KEY="your-api-key-here"
```

Or edit the examples to hardcode your API key (not recommended for production).

## Available Examples

### 1. Basic Usage (`basic_usage.py`)

Demonstrates a simple chat completion request:

```bash
python examples/basic_usage.py
```

**What it shows:**
- Making a basic API request
- Handling the response
- Error handling

### 2. Streaming Response (`streaming_example.py`)

Demonstrates streaming responses using Server-Sent Events:

```bash
python examples/streaming_example.py
```

**What it shows:**
- Enabling streaming mode
- Processing SSE events
- Real-time response handling

### 3. Multiple Models (`multi_model_example.py`)

Compare responses from different models:

```bash
python examples/multi_model_example.py
```

**What it shows:**
- Using different AI models
- Comparing outputs
- Model selection strategies

### 4. API Key Management (`manage_api_keys.py`)

Administrative operations for API keys:

```bash
python examples/manage_api_keys.py
```

**What it shows:**
- Creating new API keys
- Setting usage limits
- Checking statistics

## Configuration

All examples use the following default configuration:

```python
API_BASE_URL = "http://localhost:8000"
API_KEY = os.getenv("GAIAROUTER_API_KEY", "your-api-key-here")
```

Modify these values if your setup is different.

## Available Models

GaiaRouter supports models from multiple providers. Model IDs follow the format:

```
{provider}/{model-name}
```

Examples:
- `openrouter/anthropic/claude-3.5-sonnet`
- `openrouter/openai/gpt-4`
- `openrouter/google/gemini-pro`

See the [Models API](../docs/api/api-documentation.md#models) for a complete list.

## Error Handling

All examples include basic error handling. In production, you should:

- Implement retry logic for transient errors
- Handle rate limiting (429 status codes)
- Log errors appropriately
- Validate responses

## Best Practices

1. **API Keys**: Always use environment variables for API keys
2. **Timeouts**: Set appropriate timeouts for long-running requests
3. **Streaming**: Use streaming for better user experience
4. **Error Handling**: Always check response status codes
5. **Rate Limits**: Respect rate limits and implement backoff

## Need Help?

- Read the [API Documentation](../docs/api/api-documentation.md)
- Check the [User Guide](../docs/guides/user-guide/user-guide.md)
- Open an issue on GitHub

## Contributing

Have a useful example? Please contribute! See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.
