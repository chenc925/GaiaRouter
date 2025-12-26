"""
Anthropic适配器

处理Anthropic的请求和响应格式转换
"""

from typing import Any, Dict

from ..providers.base import ProviderResponse
from .base import RequestAdapter, ResponseAdapter


class AnthropicRequestAdapter(RequestAdapter):
    """Anthropic请求适配器"""

    def adapt(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        将统一格式转换为Anthropic格式
        """
        # Anthropic需要max_tokens，如果没有则设置默认值
        max_tokens = request.get("max_tokens") or 4096

        return {
            "model": request["model"].split("/")[-1],  # 移除provider前缀
            "messages": request["messages"],
            "temperature": request.get("temperature"),
            "max_tokens": max_tokens,
            "stream": request.get("stream", False),
        }


class AnthropicResponseAdapter(ResponseAdapter):
    """Anthropic响应适配器"""

    def adapt(self, response: ProviderResponse) -> Dict[str, Any]:
        """
        将Anthropic响应转换为统一格式

        Args:
          response: ProviderResponse对象

        Returns:
          统一格式的响应字典
        """
        import time

        return {
            "id": f"msg-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": response.model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response.content,
                    },
                    "finish_reason": response.finish_reason,
                }
            ],
            "usage": {
                "prompt_tokens": response.prompt_tokens,
                "completion_tokens": response.completion_tokens,
                "total_tokens": response.total_tokens,
            },
        }

    def adapt_stream_chunk(self, chunk: Dict[str, Any]) -> Dict[str, Any]:
        """
        将Anthropic流式chunk转换为统一格式
        """
        # Anthropic的流式格式需要转换
        if chunk.get("type") == "content_block_delta":
            return {
                "id": chunk.get("id", ""),
                "object": "chat.completion.chunk",
                "created": 0,
                "model": chunk.get("model", ""),
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": chunk.get("delta", {}).get("text", "")},
                        "finish_reason": None,
                    }
                ],
            }
        elif chunk.get("type") == "message_stop":
            return {
                "id": chunk.get("id", ""),
                "object": "chat.completion.chunk",
                "created": 0,
                "model": chunk.get("model", ""),
                "choices": [
                    {
                        "index": 0,
                        "delta": {},
                        "finish_reason": "stop",
                    }
                ],
            }
        return chunk
