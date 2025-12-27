"""
测试 Models Controller

测试模型列表端点的各种场景
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from gaiarouter.api.controllers.models import list_models
from gaiarouter.database.models import APIKey, Model


class TestListModels:
    """测试模型列表查询"""

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

    @pytest.mark.asyncio
    async def test_list_models_success(self, mock_api_key):
        """测试成功列出模型"""
        mock_models = [
            Model(
                id="openai/gpt-4",
                name="GPT-4",
                provider="openai",
                is_enabled=True,
                created_at=datetime.now(),
            ),
            Model(
                id="anthropic/claude-2",
                name="Claude 2",
                provider="anthropic",
                is_enabled=True,
                created_at=datetime.now(),
            ),
            Model(
                id="google/gemini-pro",
                name="Gemini Pro",
                provider="google",
                is_enabled=True,
                created_at=datetime.now(),
            ),
        ]

        with patch("gaiarouter.api.controllers.models.get_model_manager") as mock_mgr:
            model_mgr_instance = Mock()
            model_mgr_instance.list_models.return_value = (mock_models, 3)
            mock_mgr.return_value = model_mgr_instance

            response = await list_models(mock_api_key)

            # Verify
            assert len(response.data) == 3
            assert response.data[0].id == "openai/gpt-4"
            assert response.data[0].provider == "openai"
            assert response.data[0].owned_by == "openai"
            assert response.data[0].object == "model"
            assert response.data[1].id == "anthropic/claude-2"
            assert response.data[2].id == "google/gemini-pro"

            # Verify manager was called with correct params
            model_mgr_instance.list_models.assert_called_once_with(enabled_only=True, limit=1000)

    @pytest.mark.asyncio
    async def test_list_models_empty(self, mock_api_key):
        """测试空模型列表"""
        with patch("gaiarouter.api.controllers.models.get_model_manager") as mock_mgr:
            model_mgr_instance = Mock()
            model_mgr_instance.list_models.return_value = ([], 0)
            mock_mgr.return_value = model_mgr_instance

            response = await list_models(mock_api_key)

            # Verify
            assert len(response.data) == 0
            assert response.data == []

    @pytest.mark.asyncio
    async def test_list_models_only_enabled(self, mock_api_key):
        """测试只返回启用的模型"""
        # Manager should only return enabled models
        enabled_models = [
            Model(
                id="openai/gpt-4",
                name="GPT-4",
                provider="openai",
                is_enabled=True,
                created_at=datetime.now(),
            ),
        ]

        with patch("gaiarouter.api.controllers.models.get_model_manager") as mock_mgr:
            model_mgr_instance = Mock()
            model_mgr_instance.list_models.return_value = (enabled_models, 1)
            mock_mgr.return_value = model_mgr_instance

            response = await list_models(mock_api_key)

            # Verify only enabled models returned
            assert len(response.data) == 1
            assert response.data[0].id == "openai/gpt-4"

            # Verify enabled_only=True was passed
            model_mgr_instance.list_models.assert_called_once_with(enabled_only=True, limit=1000)

    @pytest.mark.asyncio
    async def test_list_models_response_format(self, mock_api_key):
        """测试响应格式"""
        mock_models = [
            Model(
                id="openai/gpt-3.5-turbo",
                name="GPT-3.5 Turbo",
                provider="openai",
                is_enabled=True,
                created_at=datetime.now(),
            ),
        ]

        with patch("gaiarouter.api.controllers.models.get_model_manager") as mock_mgr:
            model_mgr_instance = Mock()
            model_mgr_instance.list_models.return_value = (mock_models, 1)
            mock_mgr.return_value = model_mgr_instance

            response = await list_models(mock_api_key)

            # Verify response structure
            assert hasattr(response, "data")
            assert isinstance(response.data, list)
            assert len(response.data) == 1

            # Verify ModelInfo fields
            model_info = response.data[0]
            assert hasattr(model_info, "id")
            assert hasattr(model_info, "object")
            assert hasattr(model_info, "created")
            assert hasattr(model_info, "owned_by")
            assert hasattr(model_info, "provider")

            assert model_info.id == "openai/gpt-3.5-turbo"
            assert model_info.object == "model"
            assert isinstance(model_info.created, int)
            assert model_info.created > 0
            assert model_info.owned_by == "openai"
            assert model_info.provider == "openai"

    @pytest.mark.asyncio
    async def test_list_models_default_provider(self, mock_api_key):
        """测试默认 provider (openrouter)"""
        mock_models = [
            Model(
                id="some/model",
                name="Some Model",
                provider=None,  # No provider specified
                is_enabled=True,
                created_at=datetime.now(),
            ),
        ]

        with patch("gaiarouter.api.controllers.models.get_model_manager") as mock_mgr:
            model_mgr_instance = Mock()
            model_mgr_instance.list_models.return_value = (mock_models, 1)
            mock_mgr.return_value = model_mgr_instance

            response = await list_models(mock_api_key)

            # Should default to "openrouter"
            assert response.data[0].provider == "openrouter"
            assert response.data[0].owned_by == "openrouter"

    @pytest.mark.asyncio
    async def test_list_models_large_list(self, mock_api_key):
        """测试大量模型列表"""
        # Create 50 mock models
        mock_models = [
            Model(
                id=f"provider-{i}/model-{i}",
                name=f"Model {i}",
                provider=f"provider-{i}",
                is_enabled=True,
                created_at=datetime.now(),
            )
            for i in range(50)
        ]

        with patch("gaiarouter.api.controllers.models.get_model_manager") as mock_mgr:
            model_mgr_instance = Mock()
            model_mgr_instance.list_models.return_value = (mock_models, 50)
            mock_mgr.return_value = model_mgr_instance

            response = await list_models(mock_api_key)

            # Verify all models returned
            assert len(response.data) == 50
            assert response.data[0].id == "provider-0/model-0"
            assert response.data[49].id == "provider-49/model-49"

    @pytest.mark.asyncio
    async def test_list_models_timestamp_format(self, mock_api_key):
        """测试时间戳格式"""
        import time

        mock_models = [
            Model(
                id="openai/gpt-4",
                name="GPT-4",
                provider="openai",
                is_enabled=True,
                created_at=datetime.now(),
            ),
        ]

        with patch("gaiarouter.api.controllers.models.get_model_manager") as mock_mgr:
            model_mgr_instance = Mock()
            model_mgr_instance.list_models.return_value = (mock_models, 1)
            mock_mgr.return_value = model_mgr_instance

            before_time = int(time.time())
            response = await list_models(mock_api_key)
            after_time = int(time.time())

            # Timestamp should be within reasonable range
            created_time = response.data[0].created
            assert before_time <= created_time <= after_time + 1


class TestListModelsEdgeCases:
    """测试边缘情况"""

    @pytest.fixture
    def mock_api_key(self):
        return APIKey(
            id="ak_123",
            organization_id="org_123",
            name="Test Key",
            status="active",
            created_at=datetime.now(),
        )

    @pytest.mark.asyncio
    async def test_list_models_with_special_characters(self, mock_api_key):
        """测试包含特殊字符的模型 ID"""
        mock_models = [
            Model(
                id="openrouter/anthropic/claude-3-opus:beta",
                name="Claude 3 Opus Beta",
                provider="openrouter",
                is_enabled=True,
                created_at=datetime.now(),
            ),
        ]

        with patch("gaiarouter.api.controllers.models.get_model_manager") as mock_mgr:
            model_mgr_instance = Mock()
            model_mgr_instance.list_models.return_value = (mock_models, 1)
            mock_mgr.return_value = model_mgr_instance

            response = await list_models(mock_api_key)

            # Should handle special characters correctly
            assert response.data[0].id == "openrouter/anthropic/claude-3-opus:beta"

    @pytest.mark.asyncio
    async def test_list_models_multiple_providers(self, mock_api_key):
        """测试多个提供商的模型"""
        mock_models = [
            Model(id="openai/gpt-4", name="GPT-4", provider="openai", is_enabled=True),
            Model(id="anthropic/claude-2", name="Claude 2", provider="anthropic", is_enabled=True),
            Model(id="google/gemini-pro", name="Gemini Pro", provider="google", is_enabled=True),
            Model(
                id="openrouter/mistral-7b",
                name="Mistral 7B",
                provider="openrouter",
                is_enabled=True,
            ),
        ]

        # Add created_at to all models
        for model in mock_models:
            model.created_at = datetime.now()

        with patch("gaiarouter.api.controllers.models.get_model_manager") as mock_mgr:
            model_mgr_instance = Mock()
            model_mgr_instance.list_models.return_value = (mock_models, 4)
            mock_mgr.return_value = model_mgr_instance

            response = await list_models(mock_api_key)

            # Verify all providers present
            providers = [model.provider for model in response.data]
            assert "openai" in providers
            assert "anthropic" in providers
            assert "google" in providers
            assert "openrouter" in providers
            assert len(response.data) == 4
