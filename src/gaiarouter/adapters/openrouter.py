"""
OpenRouter适配器

处理OpenRouter的请求和响应格式转换
"""

from typing import Dict, Any
from .base import RequestAdapter, ResponseAdapter
from ..providers.base import ProviderResponse


class OpenRouterRequestAdapter(RequestAdapter):
  """OpenRouter请求适配器"""
  
  def adapt(self, request: Dict[str, Any]) -> Dict[str, Any]:
    """
    将统一格式转换为OpenRouter格式
    
    OpenRouter格式与OpenAI格式兼容
    """
    return {
      "model": request["model"],  # OpenRouter使用完整模型标识
      "messages": request["messages"],
      "temperature": request.get("temperature"),
      "max_tokens": request.get("max_tokens"),
      "top_p": request.get("top_p"),
      "frequency_penalty": request.get("frequency_penalty"),
      "presence_penalty": request.get("presence_penalty"),
      "stream": request.get("stream", False),
    }


class OpenRouterResponseAdapter(ResponseAdapter):
  """OpenRouter响应适配器"""
  
  def adapt(self, response: ProviderResponse) -> Dict[str, Any]:
    """
    将OpenRouter响应转换为统一格式
    
    OpenRouter格式与OpenAI格式兼容
    
    Args:
      response: ProviderResponse对象
      
    Returns:
      统一格式的响应字典
    """
    import time
    return {
      "id": f"chatcmpl-{int(time.time())}",
      "object": "chat.completion",
      "created": int(response.usage.get("created", time.time())) if response.usage else int(time.time()),
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
    将OpenRouter流式chunk转换为统一格式
    
    OpenRouter格式与OpenAI格式兼容
    """
    return chunk
