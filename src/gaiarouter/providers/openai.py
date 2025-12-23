"""
OpenAI提供商实现
"""

import httpx
from typing import List, Dict, Any, Optional, AsyncIterator
from ..utils.errors import TimeoutError, AuthenticationError
from ..config import get_settings
from .base import Provider, ProviderResponse


class OpenAIProvider(Provider):
    """OpenAI提供商"""

    def get_default_base_url(self) -> str:
        """获取OpenAI API基础URL"""
        return "https://api.openai.com/v1"

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs,
    ) -> ProviderResponse:
        """
        调用OpenAI聊天完成接口

        Args:
          messages: 消息列表
          model: 模型名称（如gpt-4）
          temperature: 温度参数
          max_tokens: 最大token数
          stream: 是否流式响应
          **kwargs: 其他参数

        Returns:
          ProviderResponse: 响应对象
        """
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": model,
            "messages": messages,
        }

        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if stream:
            payload["stream"] = True

        payload.update(kwargs)

        async def _make_request():
            async with httpx.AsyncClient(timeout=self.settings.request_timeout) as client:
                response = await client.post(url, json=payload, headers=self.get_headers())
                response.raise_for_status()
                return response.json()

        try:
            data = await self._retry_request(_make_request)
            choice = data["choices"][0]
            usage = data.get("usage", {})

            return ProviderResponse(
                content=choice["message"]["content"],
                model=data["model"],
                finish_reason=choice.get("finish_reason"),
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
                total_tokens=usage.get("total_tokens", 0),
                usage=usage,
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid OpenAI API Key")
            raise
        except httpx.TimeoutException:
            raise TimeoutError("OpenAI API request timeout")

    async def stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        流式调用OpenAI聊天完成接口

        Args:
          messages: 消息列表
          model: 模型名称
          temperature: 温度参数
          max_tokens: 最大token数
          **kwargs: 其他参数

        Yields:
          Dict: 流式响应块
        """
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
        }

        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        payload.update(kwargs)

        async with httpx.AsyncClient(timeout=self.settings.request_timeout) as client:
            try:
                async with client.stream(
                    "POST", url, json=payload, headers=self.get_headers()
                ) as response:
                    response.raise_for_status()

                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]  # 移除"data: "前缀
                            if data_str == "[DONE]":
                                break

                            import json

                            try:
                                data = json.loads(data_str)
                                yield data
                            except json.JSONDecodeError:
                                continue
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    raise AuthenticationError("Invalid OpenAI API Key")
                raise
            except httpx.TimeoutException:
                raise TimeoutError("OpenAI API request timeout")
