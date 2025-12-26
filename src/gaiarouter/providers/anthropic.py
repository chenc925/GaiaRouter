"""
Anthropic提供商实现
"""

from typing import Any, AsyncIterator, Dict, List, Optional

import httpx

from ..config import get_settings
from ..utils.errors import AuthenticationError, TimeoutError
from .base import Provider, ProviderResponse


class AnthropicProvider(Provider):
    """Anthropic提供商"""

    def get_default_base_url(self) -> str:
        """获取Anthropic API基础URL"""
        return "https://api.anthropic.com/v1"

    def get_headers(self) -> Dict[str, str]:
        """获取请求头（Anthropic需要特殊的header格式）"""
        headers = {
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        }
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return headers

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
        调用Anthropic聊天完成接口

        Args:
          messages: 消息列表
          model: 模型名称（如claude-3-opus-20240229）
          temperature: 温度参数
          max_tokens: 最大token数（必需）
          stream: 是否流式响应
          **kwargs: 其他参数

        Returns:
          ProviderResponse: 响应对象
        """
        if max_tokens is None:
            max_tokens = 4096  # Anthropic默认值

        url = f"{self.base_url}/messages"
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
        }

        if temperature is not None:
            payload["temperature"] = temperature
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
            content = data["content"][0]["text"]
            usage = data.get("usage", {})

            return ProviderResponse(
                content=content,
                model=data["model"],
                finish_reason=data.get("stop_reason"),
                prompt_tokens=usage.get("input_tokens", 0),
                completion_tokens=usage.get("output_tokens", 0),
                total_tokens=usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
                usage=usage,
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid Anthropic API Key")
            raise
        except httpx.TimeoutException:
            raise TimeoutError("Anthropic API request timeout")

    async def stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        流式调用Anthropic聊天完成接口

        Args:
          messages: 消息列表
          model: 模型名称
          temperature: 温度参数
          max_tokens: 最大token数
          **kwargs: 其他参数

        Yields:
          Dict: 流式响应块
        """
        if max_tokens is None:
            max_tokens = 4096

        url = f"{self.base_url}/messages"
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "stream": True,
        }

        if temperature is not None:
            payload["temperature"] = temperature

        payload.update(kwargs)

        async with httpx.AsyncClient(timeout=self.settings.request_timeout) as client:
            try:
                async with client.stream(
                    "POST", url, json=payload, headers=self.get_headers()
                ) as response:
                    response.raise_for_status()

                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]
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
                    raise AuthenticationError("Invalid Anthropic API Key")
                raise
            except httpx.TimeoutException:
                raise TimeoutError("Anthropic API request timeout")
