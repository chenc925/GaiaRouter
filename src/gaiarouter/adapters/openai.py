"""
OpenAI适配器

处理OpenAI的请求和响应格式转换
"""

from typing import Dict, Any
from .base import RequestAdapter, ResponseAdapter
from ..providers.base import ProviderResponse


class OpenAIRequestAdapter(RequestAdapter):
  """OpenAI请求适配器"""
  
  def adapt(self, request: Dict[str, Any]) -> Dict[str, Any]:
    """
    将统一格式转换为OpenAI格式
    
    OpenAI格式与统一格式基本一致，只需简单映射
    """
    return {
      "model": request["model"].split("/")[-1],  # 移除provider前缀
      "messages": request["messages"],
      "temperature": request.get("temperature"),
      "max_tokens": request.get("max_tokens"),
      "top_p": request.get("top_p"),
      "frequency_penalty": request.get("frequency_penalty"),
      "presence_penalty": request.get("presence_penalty"),
      "stream": request.get("stream", False),
    }


class OpenAIResponseAdapter(ResponseAdapter):
  """OpenAI响应适配器"""
  
  def adapt(self, response: ProviderResponse) -> Dict[str, Any]:
    """
    将OpenAI响应转换为统一格式
    
    Args:
      response: ProviderResponse对象
      
    Returns:
      统一格式的响应字典
    """
    import time
    return {
      "id": f"chatcmpl-{int(time.time())}",
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
    将OpenAI流式chunk转换为统一格式
    """
    # OpenAI的流式响应已经是统一格式
    return chunk
