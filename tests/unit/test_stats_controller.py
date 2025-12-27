"""
测试 Stats Controller

测试统计查询端点的各种场景
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from gaiarouter.api.controllers.stats import get_global_stats, get_key_stats
from gaiarouter.database.models import User
from gaiarouter.utils.errors import InvalidRequestError


class TestGetKeyStats:
    """测试获取 API Key 统计"""

    @pytest.fixture
    def mock_user(self):
        return User(id="user_123", username="admin", role="admin", status="active")

    @pytest.mark.asyncio
    async def test_get_key_stats_success(self, mock_user):
        """测试成功获取 API Key 统计"""
        mock_result = {
            "key_id": "ak_123",
            "period": {
                "start": "2024-01-01T00:00:00Z",
                "end": "2024-01-31T23:59:59Z",
            },
            "summary": {
                "total_requests": 100,
                "total_tokens": 10000,
                "total_cost": 5.0,
            },
            "by_date": [],
        }

        with patch("gaiarouter.api.controllers.stats.get_stats_query") as mock_stats_query:
            stats_query_instance = Mock()
            stats_query_instance.query_key_stats.return_value = mock_result
            mock_stats_query.return_value = stats_query_instance

            response = await get_key_stats(
                key_id="ak_123",
                start_date="2024-01-01T00:00:00Z",
                end_date="2024-01-31T23:59:59Z",
                group_by="day",
                user=mock_user,
            )

            assert response["key_id"] == "ak_123"
            assert response["summary"]["total_requests"] == 100
            stats_query_instance.query_key_stats.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_key_stats_invalid_start_date(self, mock_user):
        """测试无效的开始日期"""
        with pytest.raises(InvalidRequestError, match="Invalid start_date format"):
            await get_key_stats(
                key_id="ak_123",
                start_date="invalid-date",
                end_date=None,
                group_by="day",
                user=mock_user,
            )

    @pytest.mark.asyncio
    async def test_get_key_stats_invalid_end_date(self, mock_user):
        """测试无效的结束日期"""
        with pytest.raises(InvalidRequestError, match="Invalid end_date format"):
            await get_key_stats(
                key_id="ak_123",
                start_date=None,
                end_date="invalid-date",
                group_by="day",
                user=mock_user,
            )

    @pytest.mark.asyncio
    async def test_get_key_stats_invalid_group_by(self, mock_user):
        """测试无效的分组方式"""
        with pytest.raises(InvalidRequestError, match="Invalid group_by"):
            await get_key_stats(
                key_id="ak_123",
                start_date=None,
                end_date=None,
                group_by="invalid_group",
                user=mock_user,
            )

    @pytest.mark.asyncio
    async def test_get_key_stats_group_by_week(self, mock_user):
        """测试按周分组"""
        mock_result = {
            "key_id": "ak_123",
            "period": {"start": "2024-01-01T00:00:00Z", "end": "2024-01-31T23:59:59Z"},
            "summary": {},
            "by_week": [],
        }

        with patch("gaiarouter.api.controllers.stats.get_stats_query") as mock_stats_query:
            stats_query_instance = Mock()
            stats_query_instance.query_key_stats.return_value = mock_result
            mock_stats_query.return_value = stats_query_instance

            response = await get_key_stats(
                key_id="ak_123",
                start_date="2024-01-01T00:00:00Z",
                end_date="2024-01-31T23:59:59Z",
                group_by="week",
                user=mock_user,
            )

            assert response["key_id"] == "ak_123"

    @pytest.mark.asyncio
    async def test_get_key_stats_group_by_model(self, mock_user):
        """测试按模型分组"""
        mock_result = {
            "key_id": "ak_123",
            "period": {"start": "2024-01-01T00:00:00Z", "end": "2024-01-31T23:59:59Z"},
            "summary": {},
            "by_model": [
                {"model": "gpt-4", "requests": 50, "tokens": 5000, "cost": 2.5},
                {"model": "gpt-3.5-turbo", "requests": 50, "tokens": 5000, "cost": 2.5},
            ],
        }

        with patch("gaiarouter.api.controllers.stats.get_stats_query") as mock_stats_query:
            stats_query_instance = Mock()
            stats_query_instance.query_key_stats.return_value = mock_result
            mock_stats_query.return_value = stats_query_instance

            response = await get_key_stats(
                key_id="ak_123",
                start_date=None,
                end_date=None,
                group_by="model",
                user=mock_user,
            )

            assert "by_model" in response
            assert len(response["by_model"]) == 2

    @pytest.mark.asyncio
    async def test_get_key_stats_group_by_provider(self, mock_user):
        """测试按提供商分组"""
        mock_result = {
            "key_id": "ak_123",
            "summary": {},
            "by_provider": [
                {"provider": "openai", "requests": 80, "tokens": 8000, "cost": 4.0},
                {"provider": "anthropic", "requests": 20, "tokens": 2000, "cost": 1.0},
            ],
        }

        with patch("gaiarouter.api.controllers.stats.get_stats_query") as mock_stats_query:
            stats_query_instance = Mock()
            stats_query_instance.query_key_stats.return_value = mock_result
            mock_stats_query.return_value = stats_query_instance

            response = await get_key_stats(
                key_id="ak_123", start_date=None, end_date=None, group_by="provider", user=mock_user
            )

            assert "by_provider" in response
            assert len(response["by_provider"]) == 2

    @pytest.mark.asyncio
    async def test_get_key_stats_no_dates(self, mock_user):
        """测试不提供日期参数"""
        mock_result = {
            "key_id": "ak_123",
            "summary": {"total_requests": 100},
        }

        with patch("gaiarouter.api.controllers.stats.get_stats_query") as mock_stats_query:
            stats_query_instance = Mock()
            stats_query_instance.query_key_stats.return_value = mock_result
            mock_stats_query.return_value = stats_query_instance

            response = await get_key_stats(
                key_id="ak_123", start_date=None, end_date=None, group_by="day", user=mock_user
            )

            assert response["key_id"] == "ak_123"
            stats_query_instance.query_key_stats.assert_called_once()


class TestGetGlobalStats:
    """测试获取全局统计"""

    @pytest.fixture
    def mock_user(self):
        return User(id="user_123", username="admin", role="admin", status="active")

    @pytest.mark.asyncio
    async def test_get_global_stats_success(self, mock_user):
        """测试成功获取全局统计"""
        mock_result = {
            "period": {
                "start": "2024-01-01T00:00:00Z",
                "end": "2024-01-31T23:59:59Z",
            },
            "summary": {
                "total_requests": 1000,
                "total_tokens": 100000,
                "total_cost": 50.0,
                "unique_api_keys": 10,
            },
            "by_date": [],
        }

        with patch("gaiarouter.api.controllers.stats.get_stats_query") as mock_stats_query:
            stats_query_instance = Mock()
            stats_query_instance.query_global_stats.return_value = mock_result
            mock_stats_query.return_value = stats_query_instance

            response = await get_global_stats(
                start_date="2024-01-01T00:00:00Z",
                end_date="2024-01-31T23:59:59Z",
                group_by="day",
                user=mock_user,
            )

            assert response["summary"]["total_requests"] == 1000
            assert response["summary"]["unique_api_keys"] == 10
            stats_query_instance.query_global_stats.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_global_stats_invalid_start_date(self, mock_user):
        """测试无效的开始日期"""
        with pytest.raises(InvalidRequestError, match="Invalid start_date format"):
            await get_global_stats(
                start_date="not-a-date",
                end_date=None,
                group_by="day",
                user=mock_user,
            )

    @pytest.mark.asyncio
    async def test_get_global_stats_invalid_end_date(self, mock_user):
        """测试无效的结束日期"""
        with pytest.raises(InvalidRequestError, match="Invalid end_date format"):
            await get_global_stats(
                start_date=None,
                end_date="not-a-date",
                group_by="day",
                user=mock_user,
            )

    @pytest.mark.asyncio
    async def test_get_global_stats_invalid_group_by(self, mock_user):
        """测试无效的分组方式"""
        with pytest.raises(InvalidRequestError, match="Invalid group_by"):
            await get_global_stats(
                start_date=None,
                end_date=None,
                group_by="invalid",
                user=mock_user,
            )

    @pytest.mark.asyncio
    async def test_get_global_stats_group_by_week(self, mock_user):
        """测试按周分组"""
        mock_result = {
            "period": {"start": "2024-01-01T00:00:00Z", "end": "2024-01-31T23:59:59Z"},
            "summary": {},
            "by_week": [],
        }

        with patch("gaiarouter.api.controllers.stats.get_stats_query") as mock_stats_query:
            stats_query_instance = Mock()
            stats_query_instance.query_global_stats.return_value = mock_result
            mock_stats_query.return_value = stats_query_instance

            response = await get_global_stats(
                start_date="2024-01-01T00:00:00Z",
                end_date="2024-01-31T23:59:59Z",
                group_by="week",
                user=mock_user,
            )

            assert "summary" in response

    @pytest.mark.asyncio
    async def test_get_global_stats_group_by_month(self, mock_user):
        """测试按月分组"""
        mock_result = {
            "summary": {},
            "by_month": [
                {"month": "2024-01", "requests": 500, "tokens": 50000, "cost": 25.0},
                {"month": "2024-02", "requests": 500, "tokens": 50000, "cost": 25.0},
            ],
        }

        with patch("gaiarouter.api.controllers.stats.get_stats_query") as mock_stats_query:
            stats_query_instance = Mock()
            stats_query_instance.query_global_stats.return_value = mock_result
            mock_stats_query.return_value = stats_query_instance

            response = await get_global_stats(
                start_date=None,
                end_date=None,
                group_by="month",
                user=mock_user,
            )

            assert "by_month" in response
            assert len(response["by_month"]) == 2

    @pytest.mark.asyncio
    async def test_get_global_stats_group_by_provider(self, mock_user):
        """测试按提供商分组"""
        mock_result = {
            "summary": {},
            "by_provider": [
                {"provider": "openai", "requests": 600, "tokens": 60000, "cost": 30.0},
                {"provider": "anthropic", "requests": 300, "tokens": 30000, "cost": 15.0},
                {"provider": "google", "requests": 100, "tokens": 10000, "cost": 5.0},
            ],
        }

        with patch("gaiarouter.api.controllers.stats.get_stats_query") as mock_stats_query:
            stats_query_instance = Mock()
            stats_query_instance.query_global_stats.return_value = mock_result
            mock_stats_query.return_value = stats_query_instance

            response = await get_global_stats(
                start_date=None,
                end_date=None,
                group_by="provider",
                user=mock_user,
            )

            assert "by_provider" in response
            assert len(response["by_provider"]) == 3

    @pytest.mark.asyncio
    async def test_get_global_stats_no_dates(self, mock_user):
        """测试不提供日期参数"""
        mock_result = {
            "summary": {
                "total_requests": 1000,
                "total_tokens": 100000,
                "total_cost": 50.0,
            },
        }

        with patch("gaiarouter.api.controllers.stats.get_stats_query") as mock_stats_query:
            stats_query_instance = Mock()
            stats_query_instance.query_global_stats.return_value = mock_result
            mock_stats_query.return_value = stats_query_instance

            response = await get_global_stats(
                start_date=None,
                end_date=None,
                group_by="day",
                user=mock_user,
            )

            assert response["summary"]["total_requests"] == 1000
            stats_query_instance.query_global_stats.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_global_stats_date_parsing(self, mock_user):
        """测试日期解析"""
        mock_result = {"summary": {}}

        with patch("gaiarouter.api.controllers.stats.get_stats_query") as mock_stats_query:
            stats_query_instance = Mock()
            stats_query_instance.query_global_stats.return_value = mock_result
            mock_stats_query.return_value = stats_query_instance

            # Test with Z suffix
            response = await get_global_stats(
                start_date="2024-01-01T00:00:00Z",
                end_date="2024-01-31T23:59:59Z",
                group_by="day",
                user=mock_user,
            )

            # Verify the call was made
            assert response == mock_result
            stats_query_instance.query_global_stats.assert_called_once()
