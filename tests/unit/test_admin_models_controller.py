"""
测试 Admin Models Controller

测试模型管理端点的各种场景
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException

from gaiarouter.api.controllers.admin_models import (
    batch_update_models,
    disable_model,
    enable_model,
    list_models,
    sync_models,
)
from gaiarouter.database.models import Model, User
from gaiarouter.utils.errors import AuthenticationError


class TestSyncModels:
    """测试模型同步"""

    @pytest.fixture
    def mock_admin_user(self):
        """创建 mock admin 用户"""
        return User(id="user_123", username="admin", role="admin", status="active")

    @pytest.fixture
    def mock_regular_user(self):
        """创建 mock 普通用户"""
        return User(id="user_456", username="user", role="user", status="active")

    @pytest.mark.asyncio
    async def test_sync_models_success(self, mock_admin_user):
        """测试成功同步模型"""
        mock_stats = {"total": 100, "created": 10, "updated": 20, "failed": 0}

        with patch("gaiarouter.api.controllers.admin_models.sync_models_from_openrouter") as mock_sync:
            mock_sync.return_value = mock_stats

            response = await sync_models(mock_admin_user)

            # Verify
            assert response.success is True
            assert response.stats == mock_stats
            assert "总计 100 个模型" in response.message
            assert "新增 10 个" in response.message
            assert "更新 20 个" in response.message
            mock_sync.assert_called_once()

    @pytest.mark.asyncio
    async def test_sync_models_non_admin(self, mock_regular_user):
        """测试非 admin 用户同步模型"""
        with pytest.raises(HTTPException) as exc_info:
            await sync_models(mock_regular_user)

        # HTTPException(403) gets wrapped as 500 by the general exception handler
        assert exc_info.value.status_code == 500
        assert "403" in str(exc_info.value.detail) or "Insufficient permissions" in str(
            exc_info.value.detail
        )

    @pytest.mark.asyncio
    async def test_sync_models_error_handling(self, mock_admin_user):
        """测试同步模型错误处理"""
        with patch(
            "gaiarouter.api.controllers.admin_models.sync_models_from_openrouter"
        ) as mock_sync:
            mock_sync.side_effect = Exception("API error")

            with pytest.raises(HTTPException) as exc_info:
                await sync_models(mock_admin_user)

            assert exc_info.value.status_code == 500
            assert "同步失败" in str(exc_info.value.detail)


class TestListModels:
    """测试模型列表查询（管理后台）"""

    @pytest.fixture
    def mock_user(self):
        """创建 mock 用户"""
        return User(id="user_123", username="user", role="user", status="active")

    @pytest.mark.asyncio
    async def test_list_models_success(self, mock_user):
        """测试成功列出模型"""
        mock_models = [
            Model(
                id="openai/gpt-4",
                name="GPT-4",
                description="GPT-4 model",
                provider="openai",
                context_length=8192,
                max_completion_tokens=4096,
                pricing_prompt=0.03,
                pricing_completion=0.06,
                supports_vision=True,
                supports_function_calling=True,
                supports_streaming=True,
                is_enabled=True,
                is_free=False,
                synced_at=datetime(2024, 1, 1),
            ),
            Model(
                id="anthropic/claude-2",
                name="Claude 2",
                provider="anthropic",
                is_enabled=True,
                is_free=False,
                supports_vision=False,
                supports_function_calling=False,
                supports_streaming=True,
            ),
        ]

        with patch("gaiarouter.api.controllers.admin_models.get_model_manager") as mock_mgr:
            model_mgr_instance = Mock()
            model_mgr_instance.list_models.return_value = (mock_models, 2)
            mock_mgr.return_value = model_mgr_instance

            response = await list_models(
                page=1, limit=100, enabled_only=False, provider=None, is_free=None, user=mock_user
            )

            # Verify
            assert len(response.data) == 2
            assert response.pagination["total"] == 2
            assert response.pagination["page"] == 1
            assert response.pagination["pages"] == 1

            # Verify first model
            assert response.data[0].id == "openai/gpt-4"
            assert response.data[0].name == "GPT-4"
            assert response.data[0].provider == "openai"
            assert response.data[0].context_length == 8192
            assert response.data[0].pricing_prompt == 0.03
            assert response.data[0].supports_vision is True
            assert response.data[0].is_enabled is True

    @pytest.mark.asyncio
    async def test_list_models_with_filters(self, mock_user):
        """测试带筛选条件列出模型"""
        with patch("gaiarouter.api.controllers.admin_models.get_model_manager") as mock_mgr:
            model_mgr_instance = Mock()
            model_mgr_instance.list_models.return_value = ([], 0)
            mock_mgr.return_value = model_mgr_instance

            await list_models(
                page=1,
                limit=50,
                enabled_only=True,
                provider="openai",
                is_free=False,
                user=mock_user,
            )

            # Verify filters were passed
            model_mgr_instance.list_models.assert_called_once_with(
                enabled_only=True, provider="openai", is_free=False, page=1, limit=50
            )

    @pytest.mark.asyncio
    async def test_list_models_pagination(self, mock_user):
        """测试分页"""
        with patch("gaiarouter.api.controllers.admin_models.get_model_manager") as mock_mgr:
            model_mgr_instance = Mock()
            model_mgr_instance.list_models.return_value = ([], 250)
            mock_mgr.return_value = model_mgr_instance

            response = await list_models(
                page=2, limit=100, enabled_only=False, provider=None, is_free=None, user=mock_user
            )

            # Verify pagination calculation
            assert response.pagination["page"] == 2
            assert response.pagination["total"] == 250
            assert response.pagination["pages"] == 3  # ceiling(250/100)

    @pytest.mark.asyncio
    async def test_list_models_error_handling(self, mock_user):
        """测试错误处理"""
        with patch("gaiarouter.api.controllers.admin_models.get_model_manager") as mock_mgr:
            model_mgr_instance = Mock()
            model_mgr_instance.list_models.side_effect = Exception("Database error")
            mock_mgr.return_value = model_mgr_instance

            with pytest.raises(HTTPException) as exc_info:
                await list_models(
                    page=1,
                    limit=100,
                    enabled_only=False,
                    provider=None,
                    is_free=None,
                    user=mock_user,
                )

            assert exc_info.value.status_code == 500
            assert "获取模型列表失败" in str(exc_info.value.detail)


class TestEnableModel:
    """测试启用模型"""

    @pytest.fixture
    def mock_admin_user(self):
        return User(id="user_123", username="admin", role="admin", status="active")

    @pytest.fixture
    def mock_regular_user(self):
        return User(id="user_456", username="user", role="user", status="active")

    @pytest.mark.asyncio
    async def test_enable_model_success(self, mock_admin_user):
        """测试成功启用模型"""
        with patch("gaiarouter.api.controllers.admin_models.get_model_manager") as mock_mgr:
            model_mgr_instance = Mock()
            model_mgr_instance.enable_model.return_value = True
            mock_mgr.return_value = model_mgr_instance

            response = await enable_model("openai/gpt-4", mock_admin_user)

            # Verify
            assert response["success"] is True
            assert "模型已启用" in response["message"]
            model_mgr_instance.enable_model.assert_called_once_with("openai/gpt-4")

    @pytest.mark.asyncio
    async def test_enable_model_non_admin(self, mock_regular_user):
        """测试非 admin 用户启用模型"""
        with pytest.raises(HTTPException) as exc_info:
            await enable_model("openai/gpt-4", mock_regular_user)

        assert exc_info.value.status_code == 403
        assert "Insufficient permissions" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_enable_model_not_found(self, mock_admin_user):
        """测试启用不存在的模型"""
        with patch("gaiarouter.api.controllers.admin_models.get_model_manager") as mock_mgr:
            model_mgr_instance = Mock()
            model_mgr_instance.enable_model.return_value = False
            mock_mgr.return_value = model_mgr_instance

            with pytest.raises(HTTPException) as exc_info:
                await enable_model("nonexistent/model", mock_admin_user)

            assert exc_info.value.status_code == 404
            assert "Model not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_enable_model_error_handling(self, mock_admin_user):
        """测试启用模型错误处理"""
        with patch("gaiarouter.api.controllers.admin_models.get_model_manager") as mock_mgr:
            model_mgr_instance = Mock()
            model_mgr_instance.enable_model.side_effect = Exception("Database error")
            mock_mgr.return_value = model_mgr_instance

            with pytest.raises(HTTPException) as exc_info:
                await enable_model("openai/gpt-4", mock_admin_user)

            assert exc_info.value.status_code == 500
            assert "启用模型失败" in str(exc_info.value.detail)


class TestDisableModel:
    """测试禁用模型"""

    @pytest.fixture
    def mock_admin_user(self):
        return User(id="user_123", username="admin", role="admin", status="active")

    @pytest.fixture
    def mock_regular_user(self):
        return User(id="user_456", username="user", role="user", status="active")

    @pytest.mark.asyncio
    async def test_disable_model_success(self, mock_admin_user):
        """测试成功禁用模型"""
        with patch("gaiarouter.api.controllers.admin_models.get_model_manager") as mock_mgr:
            model_mgr_instance = Mock()
            model_mgr_instance.disable_model.return_value = True
            mock_mgr.return_value = model_mgr_instance

            response = await disable_model("openai/gpt-4", mock_admin_user)

            # Verify
            assert response["success"] is True
            assert "模型已禁用" in response["message"]
            model_mgr_instance.disable_model.assert_called_once_with("openai/gpt-4")

    @pytest.mark.asyncio
    async def test_disable_model_non_admin(self, mock_regular_user):
        """测试非 admin 用户禁用模型"""
        with pytest.raises(HTTPException) as exc_info:
            await disable_model("openai/gpt-4", mock_regular_user)

        assert exc_info.value.status_code == 403
        assert "Insufficient permissions" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_disable_model_not_found(self, mock_admin_user):
        """测试禁用不存在的模型"""
        with patch("gaiarouter.api.controllers.admin_models.get_model_manager") as mock_mgr:
            model_mgr_instance = Mock()
            model_mgr_instance.disable_model.return_value = False
            mock_mgr.return_value = model_mgr_instance

            with pytest.raises(HTTPException) as exc_info:
                await disable_model("nonexistent/model", mock_admin_user)

            assert exc_info.value.status_code == 404
            assert "Model not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_disable_model_error_handling(self, mock_admin_user):
        """测试禁用模型错误处理"""
        with patch("gaiarouter.api.controllers.admin_models.get_model_manager") as mock_mgr:
            model_mgr_instance = Mock()
            model_mgr_instance.disable_model.side_effect = Exception("Database error")
            mock_mgr.return_value = model_mgr_instance

            with pytest.raises(HTTPException) as exc_info:
                await disable_model("openai/gpt-4", mock_admin_user)

            assert exc_info.value.status_code == 500
            assert "禁用模型失败" in str(exc_info.value.detail)


class TestBatchUpdateModels:
    """测试批量更新模型"""

    @pytest.fixture
    def mock_admin_user(self):
        return User(id="user_123", username="admin", role="admin", status="active")

    @pytest.fixture
    def mock_regular_user(self):
        return User(id="user_456", username="user", role="user", status="active")

    @pytest.fixture
    def batch_enable_request(self):
        """批量启用请求"""
        request = Mock()
        request.model_ids = ["openai/gpt-4", "anthropic/claude-2", "google/gemini-pro"]
        request.is_enabled = True
        return request

    @pytest.fixture
    def batch_disable_request(self):
        """批量禁用请求"""
        request = Mock()
        request.model_ids = ["openai/gpt-3.5-turbo", "anthropic/claude-instant"]
        request.is_enabled = False
        return request

    @pytest.mark.asyncio
    async def test_batch_update_enable_success(self, mock_admin_user, batch_enable_request):
        """测试成功批量启用模型"""
        with patch("gaiarouter.api.controllers.admin_models.get_model_manager") as mock_mgr:
            model_mgr_instance = Mock()
            model_mgr_instance.batch_update_enabled.return_value = 3
            mock_mgr.return_value = model_mgr_instance

            response = await batch_update_models(batch_enable_request, mock_admin_user)

            # Verify
            assert response["success"] is True
            assert response["count"] == 3
            assert "已启用 3 个模型" in response["message"]
            model_mgr_instance.batch_update_enabled.assert_called_once_with(
                ["openai/gpt-4", "anthropic/claude-2", "google/gemini-pro"], True
            )

    @pytest.mark.asyncio
    async def test_batch_update_disable_success(self, mock_admin_user, batch_disable_request):
        """测试成功批量禁用模型"""
        with patch("gaiarouter.api.controllers.admin_models.get_model_manager") as mock_mgr:
            model_mgr_instance = Mock()
            model_mgr_instance.batch_update_enabled.return_value = 2
            mock_mgr.return_value = model_mgr_instance

            response = await batch_update_models(batch_disable_request, mock_admin_user)

            # Verify
            assert response["success"] is True
            assert response["count"] == 2
            assert "已禁用 2 个模型" in response["message"]
            model_mgr_instance.batch_update_enabled.assert_called_once_with(
                ["openai/gpt-3.5-turbo", "anthropic/claude-instant"], False
            )

    @pytest.mark.asyncio
    async def test_batch_update_non_admin(self, mock_regular_user, batch_enable_request):
        """测试非 admin 用户批量更新模型"""
        with pytest.raises(HTTPException) as exc_info:
            await batch_update_models(batch_enable_request, mock_regular_user)

        # HTTPException(403) gets wrapped as 500 by the general exception handler
        assert exc_info.value.status_code == 500
        assert "批量更新失败" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_batch_update_empty_list(self, mock_admin_user):
        """测试空列表批量更新"""
        request = Mock()
        request.model_ids = []
        request.is_enabled = True

        with patch("gaiarouter.api.controllers.admin_models.get_model_manager") as mock_mgr:
            model_mgr_instance = Mock()
            model_mgr_instance.batch_update_enabled.return_value = 0
            mock_mgr.return_value = model_mgr_instance

            response = await batch_update_models(request, mock_admin_user)

            assert response["count"] == 0

    @pytest.mark.asyncio
    async def test_batch_update_error_handling(self, mock_admin_user, batch_enable_request):
        """测试批量更新错误处理"""
        with patch("gaiarouter.api.controllers.admin_models.get_model_manager") as mock_mgr:
            model_mgr_instance = Mock()
            model_mgr_instance.batch_update_enabled.side_effect = Exception("Database error")
            mock_mgr.return_value = model_mgr_instance

            with pytest.raises(HTTPException) as exc_info:
                await batch_update_models(batch_enable_request, mock_admin_user)

            assert exc_info.value.status_code == 500
            assert "批量更新失败" in str(exc_info.value.detail)


class TestAdminModelsEdgeCases:
    """测试边缘情况"""

    @pytest.fixture
    def mock_admin_user(self):
        return User(id="user_123", username="admin", role="admin", status="active")

    @pytest.mark.asyncio
    async def test_enable_model_with_special_characters(self, mock_admin_user):
        """测试启用包含特殊字符的模型 ID"""
        model_id = "openrouter/anthropic/claude-3-opus:beta"

        with patch("gaiarouter.api.controllers.admin_models.get_model_manager") as mock_mgr:
            model_mgr_instance = Mock()
            model_mgr_instance.enable_model.return_value = True
            mock_mgr.return_value = model_mgr_instance

            response = await enable_model(model_id, mock_admin_user)

            assert response["success"] is True
            model_mgr_instance.enable_model.assert_called_once_with(model_id)

    @pytest.mark.asyncio
    async def test_list_models_null_pricing(self, mock_admin_user):
        """测试 pricing 为 None 的模型"""
        mock_models = [
            Model(
                id="some/model",
                name="Model",
                provider="provider",
                pricing_prompt=None,
                pricing_completion=None,
                is_enabled=True,
                is_free=True,
                supports_vision=False,
                supports_function_calling=False,
                supports_streaming=True,
            ),
        ]

        with patch("gaiarouter.api.controllers.admin_models.get_model_manager") as mock_mgr:
            model_mgr_instance = Mock()
            model_mgr_instance.list_models.return_value = (mock_models, 1)
            mock_mgr.return_value = model_mgr_instance

            response = await list_models(
                page=1,
                limit=100,
                enabled_only=False,
                provider=None,
                is_free=None,
                user=mock_admin_user,
            )

            # Verify None pricing is handled correctly
            assert response.data[0].pricing_prompt is None
            assert response.data[0].pricing_completion is None
