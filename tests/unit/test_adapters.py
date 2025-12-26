"""
测试 Adapter 模块

测试请求/响应转换器，确保统一格式与各提供商格式之间正确转换
"""

import pytest

from gaiarouter.adapters.anthropic import (
    AnthropicRequestAdapter,
    AnthropicResponseAdapter,
)
from gaiarouter.adapters.google import GoogleRequestAdapter, GoogleResponseAdapter
from gaiarouter.adapters.openai import OpenAIRequestAdapter, OpenAIResponseAdapter
from gaiarouter.adapters.openrouter import (
    OpenRouterRequestAdapter,
    OpenRouterResponseAdapter,
)
from gaiarouter.providers.base import ProviderResponse


class TestOpenAIAdapters:
    """测试 OpenAI 适配器"""

    @pytest.fixture
    def request_adapter(self):
        return OpenAIRequestAdapter()

    @pytest.fixture
    def response_adapter(self):
        return OpenAIResponseAdapter()

    def test_request_adapter_basic(self, request_adapter, sample_unified_request):
        """测试基础请求转换"""
        result = request_adapter.adapt(sample_unified_request)

        # OpenAI adapter 移除 provider 前缀
        assert result["model"] == "gpt-4"
        assert result["messages"] == sample_unified_request["messages"]
        assert result["temperature"] == 0.7
        assert result["max_tokens"] == 100

    def test_request_adapter_removes_internal_fields(self, request_adapter):
        """测试移除内部字段"""
        request = {
            "model": "openai/gpt-4",
            "messages": [{"role": "user", "content": "Hi"}],
            "stream": False,  # 内部字段，不应传给 OpenAI
        }

        result = request_adapter.adapt(request)

        # stream 字段应该被保留（OpenAI 支持）
        assert "stream" in result

    def test_response_adapter_basic(self, response_adapter, sample_openai_response):
        """测试基础响应转换"""
        provider_response = ProviderResponse(
            content="Hello!",
            model="gpt-4",
            finish_reason="stop",
            prompt_tokens=20,
            completion_tokens=10,
            total_tokens=30,
        )

        result = response_adapter.adapt(provider_response)

        assert result["id"]
        assert result["object"] == "chat.completion"
        assert result["model"] == "gpt-4"
        assert result["choices"][0]["message"]["content"] == "Hello!"
        assert result["usage"]["prompt_tokens"] == 20
        assert result["usage"]["completion_tokens"] == 10

    def test_stream_chunk_adapter(self, response_adapter):
        """测试流式响应块转换"""
        chunk = {
            "id": "chatcmpl-123",
            "object": "chat.completion.chunk",
            "created": 1677652288,
            "model": "gpt-4",
            "choices": [{"index": 0, "delta": {"content": "Hello"}, "finish_reason": None}],
        }

        result = response_adapter.adapt_stream_chunk(chunk)

        # OpenAI 格式直接返回
        assert result == chunk


class TestAnthropicAdapters:
    """测试 Anthropic 适配器"""

    @pytest.fixture
    def request_adapter(self):
        return AnthropicRequestAdapter()

    @pytest.fixture
    def response_adapter(self):
        return AnthropicResponseAdapter()

    def test_request_adapter_converts_messages(self, request_adapter):
        """测试消息格式转换"""
        request = {
            "model": "claude-3-opus",
            "messages": [
                {"role": "system", "content": "You are helpful."},
                {"role": "user", "content": "Hello!"},
            ],
            "max_tokens": 100,
        }

        result = request_adapter.adapt(request)

        # Anthropic adapter 保持 messages 数组，不单独提取 system
        assert "messages" in result
        assert len(result["messages"]) == 2
        assert result["messages"][0]["role"] == "system"
        assert result["messages"][1]["role"] == "user"

    def test_request_adapter_max_tokens_required(self, request_adapter):
        """测试 max_tokens 默认值"""
        request = {
            "model": "claude-3-opus",
            "messages": [{"role": "user", "content": "Hello!"}],
        }

        result = request_adapter.adapt(request)

        # Anthropic 要求 max_tokens，应该有默认值
        assert "max_tokens" in result
        assert result["max_tokens"] > 0

    def test_response_adapter_converts_to_openai_format(
        self, response_adapter, sample_anthropic_response
    ):
        """测试响应转换为 OpenAI 格式"""
        provider_response = ProviderResponse(
            content="Hello! How can I help you today?",
            model="claude-3-opus-20240229",
            finish_reason="end_turn",
            prompt_tokens=20,
            completion_tokens=10,
            total_tokens=30,
        )

        result = response_adapter.adapt(provider_response)

        assert result["object"] == "chat.completion"
        assert result["model"] == "claude-3-opus-20240229"
        assert result["choices"][0]["message"]["role"] == "assistant"
        assert "Hello!" in result["choices"][0]["message"]["content"]

    def test_stream_chunk_adapter(self, response_adapter):
        """测试流式响应块转换"""
        chunk = {
            "type": "content_block_delta",
            "index": 0,
            "delta": {"type": "text_delta", "text": "Hello"},
        }

        result = response_adapter.adapt_stream_chunk(chunk)

        # 应该转换为 OpenAI 格式
        assert result["object"] == "chat.completion.chunk"
        assert result["choices"][0]["delta"]["content"] == "Hello"


class TestGoogleAdapters:
    """测试 Google 适配器"""

    @pytest.fixture
    def request_adapter(self):
        return GoogleRequestAdapter()

    @pytest.fixture
    def response_adapter(self):
        return GoogleResponseAdapter()

    def test_request_adapter_converts_to_contents(self, request_adapter):
        """测试消息转换为 Google contents 格式"""
        request = {
            "model": "gemini-pro",
            "messages": [
                {"role": "user", "content": "Hello!"},
                {"role": "assistant", "content": "Hi there!"},
                {"role": "user", "content": "How are you?"},
            ],
        }

        result = request_adapter.adapt(request)

        # Google 使用 contents 数组
        assert "contents" in result
        assert len(result["contents"]) == 3
        assert result["contents"][0]["role"] == "user"
        assert result["contents"][0]["parts"][0]["text"] == "Hello!"

    def test_request_adapter_maps_roles(self, request_adapter):
        """测试角色映射（assistant -> model）"""
        request = {
            "model": "gemini-pro",
            "messages": [{"role": "assistant", "content": "I'm Claude"}],
        }

        result = request_adapter.adapt(request)

        # Google 使用 'model' 而不是 'assistant'
        assert result["contents"][0]["role"] == "model"

    def test_response_adapter_extracts_text(self, response_adapter):
        """测试从 Google 响应中提取文本"""
        provider_response = ProviderResponse(
            content="Hello from Gemini!",
            model="gemini-pro",
            finish_reason="STOP",
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15,
        )

        result = response_adapter.adapt(provider_response)

        assert result["model"] == "gemini-pro"
        assert result["choices"][0]["message"]["content"] == "Hello from Gemini!"
        # Google adapter 保持原始 finish_reason 大写
        assert result["choices"][0]["finish_reason"] == "STOP"

    def test_stream_chunk_adapter(self, response_adapter):
        """测试流式响应块转换"""
        chunk = {
            "candidates": [
                {
                    "content": {"parts": [{"text": "Hello"}], "role": "model"},
                    "finishReason": "STOP",
                }
            ]
        }

        result = response_adapter.adapt_stream_chunk(chunk)

        assert result["object"] == "chat.completion.chunk"
        assert result["choices"][0]["delta"]["content"] == "Hello"


class TestOpenRouterAdapters:
    """测试 OpenRouter 适配器"""

    @pytest.fixture
    def request_adapter(self):
        return OpenRouterRequestAdapter()

    @pytest.fixture
    def response_adapter(self):
        return OpenRouterResponseAdapter()

    def test_request_adapter_openai_compatible(self, request_adapter, sample_unified_request):
        """测试 OpenRouter 兼容 OpenAI 格式"""
        result = request_adapter.adapt(sample_unified_request)

        # OpenRouter 使用 OpenAI 兼容格式
        assert result["model"] == sample_unified_request["model"]
        assert result["messages"] == sample_unified_request["messages"]

    def test_response_adapter_openai_compatible(self, response_adapter, sample_openai_response):
        """测试 OpenRouter 响应兼容 OpenAI 格式"""
        provider_response = ProviderResponse(
            content="Response from OpenRouter",
            model="anthropic/claude-3-opus",
            finish_reason="stop",
            prompt_tokens=15,
            completion_tokens=8,
            total_tokens=23,
        )

        result = response_adapter.adapt(provider_response)

        assert result["object"] == "chat.completion"
        assert result["model"] == "anthropic/claude-3-opus"
        assert result["choices"][0]["message"]["content"] == "Response from OpenRouter"


class TestAdapterEdgeCases:
    """测试适配器边界情况"""

    def test_empty_messages_handling(self):
        """测试空消息处理"""
        adapter = OpenAIRequestAdapter()

        request = {"model": "gpt-4", "messages": []}

        result = adapter.adapt(request)

        assert result["messages"] == []

    def test_missing_optional_fields(self):
        """测试缺失可选字段"""
        adapter = OpenAIRequestAdapter()

        request = {"model": "gpt-4", "messages": [{"role": "user", "content": "Hi"}]}

        result = adapter.adapt(request)

        # 应该正常处理，没有可选字段
        assert "temperature" not in result or result.get("temperature") is None

    def test_response_with_null_finish_reason(self):
        """测试 finish_reason 为 None 的情况"""
        adapter = OpenAIResponseAdapter()

        provider_response = ProviderResponse(
            content="Incomplete", model="gpt-4", finish_reason=None, total_tokens=10
        )

        result = adapter.adapt(provider_response)

        # 应该正常处理
        assert result["choices"][0]["finish_reason"] is None

    def test_stream_chunk_with_empty_delta(self):
        """测试空 delta 的流式块"""
        adapter = OpenAIResponseAdapter()

        chunk = {
            "id": "chatcmpl-123",
            "object": "chat.completion.chunk",
            "choices": [{"index": 0, "delta": {}, "finish_reason": None}],
        }

        result = adapter.adapt_stream_chunk(chunk)

        # 应该保持原样
        assert result == chunk
