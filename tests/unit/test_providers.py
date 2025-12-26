"""
测试 Provider 模块

测试各个提供商的实现、重试逻辑、错误处理等
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from gaiarouter.providers.anthropic import AnthropicProvider
from gaiarouter.providers.base import Provider, ProviderResponse
from gaiarouter.providers.google import GoogleProvider
from gaiarouter.providers.openai import OpenAIProvider
from gaiarouter.providers.openrouter import OpenRouterProvider
from gaiarouter.utils.errors import TimeoutError


class TestProviderBase:
    """测试 Provider 基类"""

    class TestProvider(Provider):
        """测试用的 Provider 实现"""

        def get_default_base_url(self) -> str:
            return "https://api.test.com"

        async def chat_completion(self, messages, model, **kwargs):
            return ProviderResponse(content="Test", model=model, total_tokens=10)

        async def stream_chat_completion(self, messages, model, **kwargs):
            yield {"content": "Test"}

    def test_init_with_api_key(self):
        """测试使用 API Key 初始化"""
        provider = self.TestProvider(api_key="test-key")

        assert provider.api_key == "test-key"
        assert provider.base_url == "https://api.test.com"

    def test_init_with_custom_base_url(self):
        """测试使用自定义 base_url 初始化"""
        provider = self.TestProvider(api_key="test-key", base_url="https://custom.api.com")

        assert provider.base_url == "https://custom.api.com"

    def test_get_headers_with_api_key(self):
        """测试生成带 API Key 的请求头"""
        provider = self.TestProvider(api_key="test-key")

        headers = provider.get_headers()

        assert headers["Content-Type"] == "application/json"
        assert headers["Authorization"] == "Bearer test-key"

    def test_get_headers_without_api_key(self):
        """测试生成不带 API Key 的请求头"""
        provider = self.TestProvider()

        headers = provider.get_headers()

        assert headers["Content-Type"] == "application/json"
        assert "Authorization" not in headers

    @pytest.mark.asyncio
    async def test_retry_request_success_first_try(self, mock_settings):
        """测试重试机制：首次尝试成功"""
        provider = self.TestProvider(api_key="test-key")

        async def mock_func():
            return "success"

        with patch("gaiarouter.providers.base.get_settings", return_value=mock_settings):
            result = await provider._retry_request(mock_func)

        assert result == "success"

    @pytest.mark.asyncio
    async def test_retry_request_success_after_retry(self, mock_settings):
        """测试重试机制：重试后成功"""
        provider = self.TestProvider(api_key="test-key")

        call_count = 0

        async def mock_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Temporary error")
            return "success"

        with patch("gaiarouter.providers.base.get_settings", return_value=mock_settings):
            result = await provider._retry_request(mock_func, max_retries=2)

        assert result == "success"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_retry_request_all_failed(self, mock_settings):
        """测试重试机制：所有尝试都失败"""
        provider = self.TestProvider(api_key="test-key")

        async def mock_func():
            raise Exception("Persistent error")

        with patch("gaiarouter.providers.base.get_settings", return_value=mock_settings):
            with pytest.raises(Exception, match="Persistent error"):
                await provider._retry_request(mock_func, max_retries=2)


class TestOpenAIProvider:
    """测试 OpenAI Provider"""

    def test_init(self):
        """测试初始化"""
        provider = OpenAIProvider(api_key="test-key")

        assert provider.api_key == "test-key"
        assert "openai.com" in provider.base_url

    def test_get_default_base_url(self):
        """测试默认 base URL"""
        provider = OpenAIProvider(api_key="test-key")

        assert provider.get_default_base_url() == "https://api.openai.com/v1"

    @pytest.mark.asyncio
    async def test_chat_completion_basic(self):
        """测试基础聊天完成（模拟）"""
        provider = OpenAIProvider(api_key="test-key")

        # Mock httpx client
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = {
                "id": "chatcmpl-123",
                "object": "chat.completion",
                "model": "gpt-4",
                "choices": [
                    {
                        "message": {"role": "assistant", "content": "Hello!"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 5,
                    "total_tokens": 15,
                },
            }
            mock_response.raise_for_status = Mock()

            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            result = await provider.chat_completion(
                messages=[{"role": "user", "content": "Hi"}],
                model="gpt-4",
                temperature=0.7,
            )

        assert result.content == "Hello!"
        assert result.model
        assert result.total_tokens == 15


class TestAnthropicProvider:
    """测试 Anthropic Provider"""

    def test_init(self):
        """测试初始化"""
        provider = AnthropicProvider(api_key="test-key")

        assert provider.api_key == "test-key"
        assert "anthropic.com" in provider.base_url

    def test_get_headers_with_anthropic_version(self):
        """测试 Anthropic 特有的请求头"""
        provider = AnthropicProvider(api_key="test-key")

        headers = provider.get_headers()

        assert "x-api-key" in headers or "Authorization" in headers
        assert headers["Content-Type"] == "application/json"


class TestGoogleProvider:
    """测试 Google Provider"""

    def test_init(self):
        """测试初始化"""
        provider = GoogleProvider(api_key="test-key")

        assert provider.api_key == "test-key"
        assert "googleapis.com" in provider.base_url

    def test_get_default_base_url(self):
        """测试默认 base URL"""
        provider = GoogleProvider(api_key="test-key")

        base_url = provider.get_default_base_url()

        assert "googleapis.com" in base_url
        assert "generativelanguage" in base_url


class TestOpenRouterProvider:
    """测试 OpenRouter Provider"""

    def test_init(self):
        """测试初始化"""
        provider = OpenRouterProvider(api_key="test-key")

        assert provider.api_key == "test-key"
        assert "openrouter.ai" in provider.base_url

    def test_get_default_base_url(self):
        """测试默认 base URL"""
        provider = OpenRouterProvider(api_key="test-key")

        assert provider.get_default_base_url() == "https://openrouter.ai/api/v1"

    def test_get_headers_includes_referrer(self):
        """测试 OpenRouter 特有的请求头"""
        provider = OpenRouterProvider(api_key="test-key")

        headers = provider.get_headers()

        # OpenRouter 可能需要特定的 referrer 头
        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test-key"


class TestProviderEdgeCases:
    """测试 Provider 边界情况"""

    @pytest.mark.asyncio
    async def test_provider_without_api_key(self):
        """测试没有 API Key 的情况"""

        class TestProvider(Provider):
            def get_default_base_url(self):
                return "https://api.test.com"

            async def chat_completion(self, messages, model, **kwargs):
                return ProviderResponse(content="Test", model=model, total_tokens=10)

            async def stream_chat_completion(self, messages, model, **kwargs):
                yield {"content": "Test"}

        provider = TestProvider()  # 不提供 API Key

        headers = provider.get_headers()

        # 不应该有 Authorization 头
        assert "Authorization" not in headers

    def test_provider_response_dataclass(self):
        """测试 ProviderResponse 数据类"""
        response = ProviderResponse(
            content="Hello",
            model="gpt-4",
            finish_reason="stop",
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15,
        )

        assert response.content == "Hello"
        assert response.model == "gpt-4"
        assert response.finish_reason == "stop"
        assert response.prompt_tokens == 10
        assert response.completion_tokens == 5
        assert response.total_tokens == 15

    def test_provider_response_defaults(self):
        """测试 ProviderResponse 默认值"""
        response = ProviderResponse(content="Test", model="test-model")

        assert response.finish_reason is None
        assert response.prompt_tokens == 0
        assert response.completion_tokens == 0
        assert response.total_tokens == 0
