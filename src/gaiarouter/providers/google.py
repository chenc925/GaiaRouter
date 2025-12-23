"""
Google提供商实现
"""

import httpx
from typing import List, Dict, Any, Optional, AsyncIterator
from ..utils.errors import TimeoutError, AuthenticationError
from ..config import get_settings
from .base import Provider, ProviderResponse


class GoogleProvider(Provider):
  """Google提供商"""
  
  def get_default_base_url(self) -> str:
    """获取Google API基础URL"""
    return "https://generativelanguage.googleapis.com/v1"
  
  def get_headers(self) -> Dict[str, str]:
    """获取请求头"""
    headers = {
      "Content-Type": "application/json",
    }
    return headers
  
  async def chat_completion(
    self,
    messages: List[Dict[str, str]],
    model: str,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    stream: bool = False,
    **kwargs
  ) -> ProviderResponse:
    """
    调用Google聊天完成接口
    
    Args:
      messages: 消息列表
      model: 模型名称（如gemini-pro）
      temperature: 温度参数
      max_tokens: 最大token数
      stream: 是否流式响应
      **kwargs: 其他参数
      
    Returns:
      ProviderResponse: 响应对象
    """
    url = f"{self.base_url}/models/{model}:generateContent"
    if stream:
      url = f"{self.base_url}/models/{model}:streamGenerateContent"
    
    # 转换消息格式
    contents = []
    for msg in messages:
      role = "user" if msg["role"] == "user" else "model"
      contents.append({
        "role": role,
        "parts": [{"text": msg["content"]}]
      })
    
    payload = {
      "contents": contents,
    }
    
    generation_config = {}
    if temperature is not None:
      generation_config["temperature"] = temperature
    if max_tokens is not None:
      generation_config["maxOutputTokens"] = max_tokens
    if generation_config:
      payload["generationConfig"] = generation_config
    
    payload.update(kwargs)
    
    params = {}
    if self.api_key:
      params["key"] = self.api_key
    
    async def _make_request():
      async with httpx.AsyncClient(timeout=self.settings.request_timeout) as client:
        response = await client.post(
          url,
          json=payload,
          headers=self.get_headers(),
          params=params
        )
        response.raise_for_status()
        return response.json()
    
    try:
      data = await self._retry_request(_make_request)
      
      # 解析响应
      if stream:
        # 流式响应的处理
        content = ""
        for candidate in data.get("candidates", []):
          content += candidate.get("content", {}).get("parts", [{}])[0].get("text", "")
        candidate = data.get("candidates", [{}])[0] if data.get("candidates") else {}
      else:
        candidate = data.get("candidates", [{}])[0]
        content = candidate.get("content", {}).get("parts", [{}])[0].get("text", "")
      
      usage = data.get("usageMetadata", {})
      
      return ProviderResponse(
        content=content,
        model=model,
        finish_reason=candidate.get("finishReason"),
        prompt_tokens=usage.get("promptTokenCount", 0),
        completion_tokens=usage.get("candidatesTokenCount", 0),
        total_tokens=usage.get("totalTokenCount", 0),
        usage=usage,
      )
    except httpx.HTTPStatusError as e:
      if e.response.status_code == 401:
        raise AuthenticationError("Invalid Google API Key")
      raise
    except httpx.TimeoutException:
      raise TimeoutError("Google API request timeout")
  
  async def stream_chat_completion(
    self,
    messages: List[Dict[str, str]],
    model: str,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    **kwargs
  ) -> AsyncIterator[Dict[str, Any]]:
    """
    流式调用Google聊天完成接口
    
    Args:
      messages: 消息列表
      model: 模型名称
      temperature: 温度参数
      max_tokens: 最大token数
      **kwargs: 其他参数
      
    Yields:
      Dict: 流式响应块
    """
    url = f"{self.base_url}/models/{model}:streamGenerateContent"
    
    # 转换消息格式
    contents = []
    for msg in messages:
      role = "user" if msg["role"] == "user" else "model"
      contents.append({
        "role": role,
        "parts": [{"text": msg["content"]}]
      })
    
    payload = {
      "contents": contents,
    }
    
    generation_config = {}
    if temperature is not None:
      generation_config["temperature"] = temperature
    if max_tokens is not None:
      generation_config["maxOutputTokens"] = max_tokens
    if generation_config:
      payload["generationConfig"] = generation_config
    
    payload.update(kwargs)
    
    params = {}
    if self.api_key:
      params["key"] = self.api_key
    
    async with httpx.AsyncClient(timeout=self.settings.request_timeout) as client:
      try:
        async with client.stream(
          "POST",
          url,
          json=payload,
          headers=self.get_headers(),
          params=params
        ) as response:
          response.raise_for_status()
          
          async for line in response.aiter_lines():
            if line.strip():
              import json
              try:
                data = json.loads(line)
                yield data
              except json.JSONDecodeError:
                continue
      except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
          raise AuthenticationError("Invalid Google API Key")
        raise
      except httpx.TimeoutException:
        raise TimeoutError("Google API request timeout")

