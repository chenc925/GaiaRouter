"""
适配器模块

处理请求和响应的格式转换
"""

from .anthropic import AnthropicRequestAdapter, AnthropicResponseAdapter
from .base import RequestAdapter, ResponseAdapter
from .google import GoogleRequestAdapter, GoogleResponseAdapter
from .openai import OpenAIRequestAdapter, OpenAIResponseAdapter
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
