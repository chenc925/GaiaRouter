"""
测试 Chat Controller

测试聊天完成端点的各种场景
"""

import json
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import HTTPException

from gaiarouter.api.controllers.chat import create_completion
from gaiarouter.database.models import APIKey, Model, Organization
from gaiarouter.providers.base import ProviderResponse
from gaiarouter.utils.errors import ModelNotFoundError


class TestChatCompletionNonStreaming:
    """测试非流式聊天完成"""

    @pytest.fixture
    def mock_api_key(self):
        """创建 mock API key"""
        return APIKey(
            id="ak_123",
            organization_id="org_123",
            name="Test Key",
            status="active",
            created_at=datetime.now(),
        )

    @pytest.fixture
    def chat_request(self):
        """创建聊天请求"""
        request = Mock()
        request.model = "openai/gpt-4"
        request.messages = [{"role": "user", "content": "Hello"}]
        request.temperature = 0.7
        request.max_tokens = 100
        request.top_p = None
        request.frequency_penalty = None
        request.presence_penalty = None
        request.stream = False
        request.dict = Mock(
            return_value={
                "model": "openai/gpt-4",
                "messages": [{"role": "user", "content": "Hello"}],
                "temperature": 0.7,
                "max_tokens": 100,
                "stream": False,
            }
        )
        return request

    @pytest.mark.asyncio
    async def test_chat_completion_success(self, mock_api_key, chat_request):
        """测试成功的聊天完成"""
        # Mock model
        mock_model = Model(
            id="openai/gpt-4",
            name="GPT-4",
            provider="openai",
            is_enabled=True,
        )

        # Mock provider response
        provider_response = ProviderResponse(
            content="Hello! How can I help you?",
            model="gpt-4",
            finish_reason="stop",
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30,
        )

        with (
            patch("gaiarouter.api.controllers.chat.get_model_manager") as mock_model_mgr,
            patch("gaiarouter.api.controllers.chat.get_model_router") as mock_router,
            patch("gaiarouter.api.controllers.chat.get_stats_collector") as mock_stats,
        ):
            # Setup model manager
            model_mgr_instance = Mock()
            model_mgr_instance.get_model.return_value = mock_model
            mock_model_mgr.return_value = model_mgr_instance

            # Setup router
            mock_provider = AsyncMock()
            mock_provider.chat_completion.return_value = provider_response

            mock_request_adapter = Mock()
            mock_request_adapter.adapt.return_value = {
                "messages": [{"role": "user", "content": "Hello"}],
                "temperature": 0.7,
                "max_tokens": 100,
            }

            mock_response_adapter = Mock()
            mock_response_adapter.adapt.return_value = {
                "id": "chatcmpl-123",
                "object": "chat.completion",
                "created": 1234567890,
                "model": "openai/gpt-4",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "Hello! How can I help you?"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            }

            router_instance = Mock()
            router_instance.route.return_value = (
                mock_provider,
                mock_request_adapter,
                mock_response_adapter,
                "gpt-4",
            )
            mock_router.return_value = router_instance

            # Setup stats collector
            stats_instance = Mock()
            stats_instance.record_request_sync.return_value = True
            mock_stats.return_value = stats_instance

            # Call endpoint
            response = await create_completion(chat_request, mock_api_key)

            # Verify
            assert response.id == "chatcmpl-123"
            assert response.model == "openai/gpt-4"
            assert response.choices[0].message.content == "Hello! How can I help you?"
            assert response.usage.total_tokens == 30

            mock_provider.chat_completion.assert_called_once()
            stats_instance.record_request_sync.assert_called_once()

    @pytest.mark.asyncio
    async def test_chat_completion_model_not_found(self, mock_api_key, chat_request):
        """测试模型不存在"""
        with patch("gaiarouter.api.controllers.chat.get_model_manager") as mock_model_mgr:
            model_mgr_instance = Mock()
            model_mgr_instance.get_model.return_value = None
            mock_model_mgr.return_value = model_mgr_instance

            with pytest.raises(ModelNotFoundError, match="Model not found"):
                await create_completion(chat_request, mock_api_key)

    @pytest.mark.asyncio
    async def test_chat_completion_model_disabled(self, mock_api_key, chat_request):
        """测试模型被禁用"""
        mock_model = Model(
            id="openai/gpt-4",
            name="GPT-4",
            provider="openai",
            is_enabled=False,  # Disabled
        )

        with patch("gaiarouter.api.controllers.chat.get_model_manager") as mock_model_mgr:
            model_mgr_instance = Mock()
            model_mgr_instance.get_model.return_value = mock_model
            mock_model_mgr.return_value = model_mgr_instance

            with pytest.raises(ModelNotFoundError, match="Model is not enabled"):
                await create_completion(chat_request, mock_api_key)

    @pytest.mark.asyncio
    async def test_chat_completion_with_organization_limits(self, chat_request):
        """测试带组织限制检查"""
        mock_api_key = APIKey(
            id="ak_123",
            organization_id="org_123",
            name="Test Key",
            status="active",
            created_at=datetime.now(),
        )

        mock_model = Model(
            id="openai/gpt-4",
            name="GPT-4",
            provider="openai",
            is_enabled=True,
        )

        mock_org = Organization(
            id="org_123",
            name="Test Org",
            status="active",
            monthly_requests_limit=1000,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        provider_response = ProviderResponse(
            content="Response",
            model="gpt-4",
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30,
        )

        with (
            patch("gaiarouter.api.controllers.chat.get_model_manager") as mock_model_mgr,
            patch("gaiarouter.api.controllers.chat.get_db") as mock_get_db,
            patch("gaiarouter.api.controllers.chat.get_limit_checker") as mock_limit,
            patch("gaiarouter.api.controllers.chat.get_model_router") as mock_router,
            patch("gaiarouter.api.controllers.chat.get_stats_collector") as mock_stats,
        ):
            # Setup model manager
            model_mgr_instance = Mock()
            model_mgr_instance.get_model.return_value = mock_model
            mock_model_mgr.return_value = model_mgr_instance

            # Setup database
            mock_db_session = Mock()
            mock_query = Mock()
            mock_query.filter.return_value.first.return_value = mock_org
            mock_db_session.query.return_value = mock_query
            mock_db_session.close = Mock()
            mock_get_db.return_value = iter([mock_db_session])

            # Setup limit checker
            limit_checker = Mock()
            limit_checker.check_limits.return_value = None  # No exception = OK
            mock_limit.return_value = limit_checker

            # Setup router
            mock_provider = AsyncMock()
            mock_provider.chat_completion.return_value = provider_response

            mock_request_adapter = Mock()
            mock_request_adapter.adapt.return_value = {
                "messages": [{"role": "user", "content": "Hello"}],
            }

            mock_response_adapter = Mock()
            mock_response_adapter.adapt.return_value = {
                "id": "chatcmpl-123",
                "created": 1234567890,
                "model": "openai/gpt-4",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "Response"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            }

            router_instance = Mock()
            router_instance.route.return_value = (
                mock_provider,
                mock_request_adapter,
                mock_response_adapter,
                "gpt-4",
            )
            mock_router.return_value = router_instance

            # Setup stats
            stats_instance = Mock()
            stats_instance.record_request_sync.return_value = True
            mock_stats.return_value = stats_instance

            # Call endpoint
            response = await create_completion(chat_request, mock_api_key)

            # Verify limit was checked
            limit_checker.check_limits.assert_called_once_with(
                mock_org, additional_requests=1, additional_tokens=100
            )

            assert response.id == "chatcmpl-123"

    @pytest.mark.asyncio
    async def test_chat_completion_stats_recording(self, mock_api_key, chat_request):
        """测试统计记录"""
        mock_model = Model(
            id="openai/gpt-4",
            name="GPT-4",
            provider="openai",
            is_enabled=True,
        )

        provider_response = ProviderResponse(
            content="Response",
            model="gpt-4",
            prompt_tokens=15,
            completion_tokens=25,
            total_tokens=40,
        )

        with (
            patch("gaiarouter.api.controllers.chat.get_model_manager") as mock_model_mgr,
            patch("gaiarouter.api.controllers.chat.get_model_router") as mock_router,
            patch("gaiarouter.api.controllers.chat.get_stats_collector") as mock_stats,
        ):
            # Setup
            model_mgr_instance = Mock()
            model_mgr_instance.get_model.return_value = mock_model
            mock_model_mgr.return_value = model_mgr_instance

            mock_provider = AsyncMock()
            mock_provider.chat_completion.return_value = provider_response

            mock_request_adapter = Mock()
            mock_request_adapter.adapt.return_value = {"messages": []}

            mock_response_adapter = Mock()
            mock_response_adapter.adapt.return_value = {
                "id": "chatcmpl-123",
                "created": 1234567890,
                "model": "openai/gpt-4",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "Response"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 15, "completion_tokens": 25, "total_tokens": 40},
            }

            router_instance = Mock()
            router_instance.route.return_value = (
                mock_provider,
                mock_request_adapter,
                mock_response_adapter,
                "gpt-4",
            )
            mock_router.return_value = router_instance

            stats_instance = Mock()
            mock_stats.return_value = stats_instance

            # Call endpoint
            await create_completion(chat_request, mock_api_key)

            # Verify stats were recorded
            stats_instance.record_request_sync.assert_called_once()
            call_args = stats_instance.record_request_sync.call_args[1]
            assert call_args["api_key_id"] == "ak_123"
            assert call_args["organization_id"] == "org_123"
            assert call_args["model"] == "openai/gpt-4"
            assert call_args["provider"] == "openai"
            assert call_args["prompt_tokens"] == 15
            assert call_args["completion_tokens"] == 25
            assert call_args["total_tokens"] == 40

    @pytest.mark.asyncio
    async def test_chat_completion_stats_error_handling(self, mock_api_key, chat_request):
        """测试统计记录失败不影响响应"""
        mock_model = Model(
            id="openai/gpt-4",
            name="GPT-4",
            provider="openai",
            is_enabled=True,
        )

        provider_response = ProviderResponse(
            content="Response",
            model="gpt-4",
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30,
        )

        with (
            patch("gaiarouter.api.controllers.chat.get_model_manager") as mock_model_mgr,
            patch("gaiarouter.api.controllers.chat.get_model_router") as mock_router,
            patch("gaiarouter.api.controllers.chat.get_stats_collector") as mock_stats,
        ):
            # Setup
            model_mgr_instance = Mock()
            model_mgr_instance.get_model.return_value = mock_model
            mock_model_mgr.return_value = model_mgr_instance

            mock_provider = AsyncMock()
            mock_provider.chat_completion.return_value = provider_response

            mock_request_adapter = Mock()
            mock_request_adapter.adapt.return_value = {"messages": []}

            mock_response_adapter = Mock()
            mock_response_adapter.adapt.return_value = {
                "id": "chatcmpl-123",
                "created": 1234567890,
                "model": "openai/gpt-4",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "Response"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            }

            router_instance = Mock()
            router_instance.route.return_value = (
                mock_provider,
                mock_request_adapter,
                mock_response_adapter,
                "gpt-4",
            )
            mock_router.return_value = router_instance

            # Stats collector raises exception
            stats_instance = Mock()
            stats_instance.record_request_sync.side_effect = Exception("Stats DB error")
            mock_stats.return_value = stats_instance

            # Should not raise exception - stats error is caught
            response = await create_completion(chat_request, mock_api_key)

            # Response should still be successful
            assert response.id == "chatcmpl-123"


class TestChatCompletionStreaming:
    """测试流式聊天完成"""

    @pytest.fixture
    def mock_api_key(self):
        """创建 mock API key"""
        return APIKey(
            id="ak_123",
            organization_id="org_123",
            name="Test Key",
            status="active",
            created_at=datetime.now(),
        )

    @pytest.fixture
    def chat_request_streaming(self):
        """创建流式聊天请求"""
        request = Mock()
        request.model = "openai/gpt-4"
        request.messages = [{"role": "user", "content": "Hello"}]
        request.temperature = 0.7
        request.max_tokens = 100
        request.top_p = None
        request.frequency_penalty = None
        request.presence_penalty = None
        request.stream = True  # Streaming mode
        request.dict = Mock(
            return_value={
                "model": "openai/gpt-4",
                "messages": [{"role": "user", "content": "Hello"}],
                "temperature": 0.7,
                "max_tokens": 100,
                "stream": True,
            }
        )
        return request

    @pytest.mark.asyncio
    async def test_chat_completion_streaming_success(self, mock_api_key, chat_request_streaming):
        """测试成功的流式响应"""
        mock_model = Model(
            id="openai/gpt-4",
            name="GPT-4",
            provider="openai",
            is_enabled=True,
        )

        with (
            patch("gaiarouter.api.controllers.chat.get_model_manager") as mock_model_mgr,
            patch("gaiarouter.api.controllers.chat.get_model_router") as mock_router,
        ):
            # Setup model manager
            model_mgr_instance = Mock()
            model_mgr_instance.get_model.return_value = mock_model
            mock_model_mgr.return_value = model_mgr_instance

            # Setup router with streaming provider
            async def mock_stream():
                """Mock async generator"""
                chunks = [
                    {"delta": {"content": "Hello"}},
                    {"delta": {"content": " there"}},
                    {"delta": {"content": "!"}},
                ]
                for chunk in chunks:
                    yield chunk

            mock_provider = AsyncMock()
            mock_provider.stream_chat_completion.return_value = mock_stream()

            mock_request_adapter = Mock()
            mock_request_adapter.adapt.return_value = {
                "messages": [{"role": "user", "content": "Hello"}],
                "temperature": 0.7,
                "max_tokens": 100,
            }

            mock_response_adapter = Mock()
            mock_response_adapter.adapt_stream_chunk.side_effect = [
                {"id": "chatcmpl-123", "choices": [{"delta": {"content": "Hello"}}]},
                {"id": "chatcmpl-123", "choices": [{"delta": {"content": " there"}}]},
                {"id": "chatcmpl-123", "choices": [{"delta": {"content": "!"}}]},
            ]

            router_instance = Mock()
            router_instance.route.return_value = (
                mock_provider,
                mock_request_adapter,
                mock_response_adapter,
                "gpt-4",
            )
            mock_router.return_value = router_instance

            # Call endpoint
            response = await create_completion(chat_request_streaming, mock_api_key)

            # Verify it returns a StreamingResponse
            from fastapi.responses import StreamingResponse

            assert isinstance(response, StreamingResponse)
            assert response.media_type == "text/event-stream"
            assert response.headers["Cache-Control"] == "no-cache"
            assert response.headers["Connection"] == "keep-alive"


class TestChatCompletionResponseFormatting:
    """测试响应格式化"""

    @pytest.fixture
    def mock_api_key(self):
        return APIKey(
            id="ak_123",
            organization_id="org_123",
            name="Test Key",
            status="active",
            created_at=datetime.now(),
        )

    @pytest.fixture
    def chat_request(self):
        request = Mock()
        request.model = "openai/gpt-4"
        request.messages = [{"role": "user", "content": "Hello"}]
        request.stream = False
        request.dict = Mock(return_value={"model": "openai/gpt-4", "messages": []})
        return request

    @pytest.mark.asyncio
    async def test_response_adds_missing_id(self, mock_api_key, chat_request):
        """测试自动添加缺失的响应 ID"""
        mock_model = Model(
            id="openai/gpt-4",
            name="GPT-4",
            provider="openai",
            is_enabled=True,
        )

        provider_response = ProviderResponse(
            content="Response",
            model="gpt-4",
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30,
        )

        with (
            patch("gaiarouter.api.controllers.chat.get_model_manager") as mock_model_mgr,
            patch("gaiarouter.api.controllers.chat.get_model_router") as mock_router,
            patch("gaiarouter.api.controllers.chat.get_stats_collector") as mock_stats,
        ):
            model_mgr_instance = Mock()
            model_mgr_instance.get_model.return_value = mock_model
            mock_model_mgr.return_value = model_mgr_instance

            mock_provider = AsyncMock()
            mock_provider.chat_completion.return_value = provider_response

            mock_request_adapter = Mock()
            mock_request_adapter.adapt.return_value = {"messages": []}

            # Response adapter returns response WITHOUT id
            mock_response_adapter = Mock()
            mock_response_adapter.adapt.return_value = {
                "created": 1234567890,
                "model": "openai/gpt-4",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "Response"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            }

            router_instance = Mock()
            router_instance.route.return_value = (
                mock_provider,
                mock_request_adapter,
                mock_response_adapter,
                "gpt-4",
            )
            mock_router.return_value = router_instance

            stats_instance = Mock()
            mock_stats.return_value = stats_instance

            response = await create_completion(chat_request, mock_api_key)

            # Should have auto-generated ID
            assert response.id is not None
            assert response.id.startswith("chatcmpl-")
