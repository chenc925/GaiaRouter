"""
适配器模块

处理请求和响应的格式转换
"""

from .base import RequestAdapter, ResponseAdapter
from .openai import OpenAIRequestAdapter, OpenAIResponseAdapter
from .anthropic import AnthropicRequestAdapter, AnthropicResponseAdapter
from .google import GoogleRequestAdapter, GoogleResponseAdapter
from .openrouter import OpenRouterRequestAdapter, OpenRouterResponseAdapter

__all__ = [
  "RequestAdapter",
  "ResponseAdapter",
  "OpenAIRequestAdapter",
  "OpenAIResponseAdapter",
  "AnthropicRequestAdapter",
  "AnthropicResponseAdapter",
  "GoogleRequestAdapter",
  "GoogleResponseAdapter",
  "OpenRouterRequestAdapter",
  "OpenRouterResponseAdapter",
]
