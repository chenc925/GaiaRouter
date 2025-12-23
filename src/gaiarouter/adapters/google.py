"""
Google适配器

处理Google的请求和响应格式转换
"""

from typing import Dict, Any, List
from .base import RequestAdapter, ResponseAdapter
from ..providers.base import ProviderResponse


class GoogleRequestAdapter(RequestAdapter):
  """Google请求适配器"""
  
  def adapt(self, request: Dict[str, Any]) -> Dict[str, Any]:
    """
    将统一格式转换为Google格式
    """
    # Google使用不同的消息格式
    contents = []
    for msg in request["messages"]:
      role = "user" if msg["role"] == "user" else "model"
      contents.append({
        "role": role,
        "parts": [{"text": msg["content"]}]
      })
    
    generation_config = {}
    if request.get("temperature") is not None:
      generation_config["temperature"] = request["temperature"]
    if request.get("max_tokens") is not None:
      generation_config["maxOutputTokens"] = request["max_tokens"]
    
    return {
      "contents": contents,
      "generationConfig": generation_config if generation_config else None,
    }


class GoogleResponseAdapter(ResponseAdapter):
  """Google响应适配器"""
  
  def adapt(self, response: ProviderResponse) -> Dict[str, Any]:
    """
    将Google响应转换为统一格式
    
    Args:
      response: ProviderResponse对象
      
    Returns:
      统一格式的响应字典
    """
    import time
    return {
      "id": f"gemini-{int(time.time())}",
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
    将Google流式chunk转换为统一格式
    """
    # Google的流式格式需要转换
    candidates = chunk.get("candidates", [])
    if candidates:
      candidate = candidates[0]
      content = candidate.get("content", {}).get("parts", [{}])[0].get("text", "")
      
      return {
        "id": chunk.get("id", ""),
        "object": "chat.completion.chunk",
        "created": 0,
        "model": chunk.get("model", ""),
        "choices": [
          {
            "index": 0,
            "delta": {
              "content": content
            },
            "finish_reason": candidate.get("finishReason"),
          }
        ],
      }
    return chunk
