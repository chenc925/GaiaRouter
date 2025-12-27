"""
测试 Stats 模块

测试统计收集器的费用计算和请求记录功能
"""

from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest

from gaiarouter.database.models import Model, RequestStat
from gaiarouter.stats.collector import StatsCollector


class TestStatsCollector:
    """测试统计收集器"""

    @pytest.fixture
    def collector(self):
        """创建统计收集器实例"""
        return StatsCollector()

    def test_calculate_cost_success(self, collector):
        """测试成功计算费用"""
        mock_model = Model(
            id="openai/gpt-4",
            name="GPT-4",
            provider="openai",
            pricing_prompt=0.03,
            pricing_completion=0.06,
        )

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_model
        mock_db.close = Mock()

        with patch("gaiarouter.stats.collector.get_db", return_value=iter([mock_db])):
            cost = collector.calculate_cost("openai/gpt-4", prompt_tokens=1000, completion_tokens=500)

        # 1000 tokens * $0.03/1K + 500 tokens * $0.06/1K = $0.03 + $0.03 = $0.06
        assert cost == 0.06

    def test_calculate_cost_complex(self, collector):
        """测试复杂费用计算"""
        mock_model = Model(
            id="openai/gpt-4",
            name="GPT-4",
            provider="openai",
            pricing_prompt=0.03,
            pricing_completion=0.06,
        )

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_model
        mock_db.close = Mock()

        with patch("gaiarouter.stats.collector.get_db", return_value=iter([mock_db])):
            cost = collector.calculate_cost("openai/gpt-4", prompt_tokens=2500, completion_tokens=1200)

        # 2500 tokens * $0.03/1K + 1200 tokens * $0.06/1K = $0.075 + $0.072 = $0.147
        assert cost == 0.147

    def test_calculate_cost_model_not_found(self, collector):
        """测试模型不存在时的费用计算"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.close = Mock()

        with patch("gaiarouter.stats.collector.get_db", return_value=iter([mock_db])):
            cost = collector.calculate_cost("nonexistent/model", prompt_tokens=1000, completion_tokens=500)

        assert cost is None

    def test_calculate_cost_no_pricing(self, collector):
        """测试模型无定价信息时的费用计算"""
        mock_model = Model(
            id="openai/gpt-4",
            name="GPT-4",
            provider="openai",
            pricing_prompt=None,  # No pricing
            pricing_completion=None,
        )

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_model
        mock_db.close = Mock()

        with patch("gaiarouter.stats.collector.get_db", return_value=iter([mock_db])):
            cost = collector.calculate_cost("openai/gpt-4", prompt_tokens=1000, completion_tokens=500)

        assert cost is None

    def test_calculate_cost_zero_tokens(self, collector):
        """测试零 token 的费用计算"""
        mock_model = Model(
            id="openai/gpt-4",
            name="GPT-4",
            provider="openai",
            pricing_prompt=0.03,
            pricing_completion=0.06,
        )

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_model
        mock_db.close = Mock()

        with patch("gaiarouter.stats.collector.get_db", return_value=iter([mock_db])):
            cost = collector.calculate_cost("openai/gpt-4", prompt_tokens=0, completion_tokens=0)

        assert cost == 0.0

    def test_calculate_cost_error_handling(self, collector):
        """测试费用计算错误处理"""
        mock_db = MagicMock()
        mock_db.query.side_effect = Exception("Database error")
        mock_db.close = Mock()

        with patch("gaiarouter.stats.collector.get_db", return_value=iter([mock_db])):
            cost = collector.calculate_cost("openai/gpt-4", prompt_tokens=1000, completion_tokens=500)

        assert cost is None

    def test_record_request_sync_success(self, collector):
        """测试同步记录请求成功"""
        mock_db = MagicMock()
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        mock_db.close = Mock()

        with (
            patch("gaiarouter.stats.collector.get_db", return_value=iter([mock_db])),
            patch.object(collector, "calculate_cost", return_value=0.05),
        ):
            result = collector.record_request_sync(
                api_key_id="ak_test123",
                organization_id="org_test",
                model="openai/gpt-4",
                provider="openai",
                prompt_tokens=1000,
                completion_tokens=500,
                total_tokens=1500,
            )

        assert result is True
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_record_request_sync_with_provided_cost(self, collector):
        """测试提供费用时的同步记录"""
        mock_db = MagicMock()
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        mock_db.close = Mock()

        with patch("gaiarouter.stats.collector.get_db", return_value=iter([mock_db])):
            result = collector.record_request_sync(
                api_key_id="ak_test123",
                organization_id="org_test",
                model="openai/gpt-4",
                provider="openai",
                prompt_tokens=1000,
                completion_tokens=500,
                total_tokens=1500,
                cost=0.08,  # Provided cost
            )

        assert result is True
        mock_db.add.assert_called_once()

        # Verify the stat was created with the provided cost
        call_args = mock_db.add.call_args[0][0]
        assert isinstance(call_args, RequestStat)
        assert call_args.cost == 0.08

    def test_record_request_sync_no_organization(self, collector):
        """测试无组织ID时的记录"""
        mock_db = MagicMock()
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        mock_db.close = Mock()

        with (
            patch("gaiarouter.stats.collector.get_db", return_value=iter([mock_db])),
            patch.object(collector, "calculate_cost", return_value=0.05),
        ):
            result = collector.record_request_sync(
                api_key_id="ak_test123",
                organization_id=None,  # No organization
                model="openai/gpt-4",
                provider="openai",
                prompt_tokens=1000,
                completion_tokens=500,
                total_tokens=1500,
            )

        assert result is True

    def test_record_request_sync_database_error(self, collector):
        """测试数据库错误时的记录"""
        mock_db = MagicMock()
        mock_db.add.side_effect = Exception("Database error")
        mock_db.rollback = Mock()
        mock_db.close = Mock()

        with (
            patch("gaiarouter.stats.collector.get_db", return_value=iter([mock_db])),
            patch.object(collector, "calculate_cost", return_value=0.05),
        ):
            result = collector.record_request_sync(
                api_key_id="ak_test123",
                organization_id="org_test",
                model="openai/gpt-4",
                provider="openai",
                prompt_tokens=1000,
                completion_tokens=500,
                total_tokens=1500,
            )

        assert result is False
        mock_db.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_record_request_async_success(self, collector):
        """测试异步记录请求成功"""
        mock_db = MagicMock()
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        mock_db.close = Mock()

        with (
            patch("gaiarouter.stats.collector.get_db", return_value=iter([mock_db])),
            patch.object(collector, "calculate_cost", return_value=0.05),
        ):
            result = await collector.record_request(
                api_key_id="ak_test123",
                organization_id="org_test",
                model="openai/gpt-4",
                provider="openai",
                prompt_tokens=1000,
                completion_tokens=500,
                total_tokens=1500,
            )

        assert result is True
        mock_db.add.assert_called_once()


class TestCostCalculationAccuracy:
    """测试费用计算准确性"""

    @pytest.fixture
    def collector(self):
        return StatsCollector()

    def test_various_pricing_models(self, collector):
        """测试不同定价模型的计算"""
        test_cases = [
            # (prompt_price, completion_price, prompt_tokens, completion_tokens, expected_cost)
            (0.03, 0.06, 1000, 1000, 0.09),  # GPT-4
            (0.0015, 0.002, 1000, 1000, 0.0035),  # GPT-3.5
            (0.01, 0.03, 2000, 500, 0.035),  # Claude
            (0.0001, 0.0002, 10000, 5000, 0.002),  # Cheap model
        ]

        for prompt_price, completion_price, prompt_tokens, completion_tokens, expected_cost in test_cases:
            mock_model = Model(
                id="test/model",
                name="Test Model",
                provider="test",
                pricing_prompt=prompt_price,
                pricing_completion=completion_price,
            )

            mock_db = MagicMock()
            mock_db.query.return_value.filter.return_value.first.return_value = mock_model
            mock_db.close = Mock()

            with patch("gaiarouter.stats.collector.get_db", return_value=iter([mock_db])):
                cost = collector.calculate_cost("test/model", prompt_tokens, completion_tokens)

            assert cost == expected_cost, f"Expected {expected_cost}, got {cost}"

    def test_large_token_counts(self, collector):
        """测试大量 token 的费用计算"""
        mock_model = Model(
            id="openai/gpt-4",
            name="GPT-4",
            provider="openai",
            pricing_prompt=0.03,
            pricing_completion=0.06,
        )

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_model
        mock_db.close = Mock()

        with patch("gaiarouter.stats.collector.get_db", return_value=iter([mock_db])):
            # 100K prompt tokens + 50K completion tokens
            cost = collector.calculate_cost("openai/gpt-4", prompt_tokens=100000, completion_tokens=50000)

        # 100K * $0.03/1K + 50K * $0.06/1K = $3.0 + $3.0 = $6.0
        assert cost == 6.0

    def test_fractional_tokens(self, collector):
        """测试小数 token 的费用计算"""
        mock_model = Model(
            id="openai/gpt-4",
            name="GPT-4",
            provider="openai",
            pricing_prompt=0.03,
            pricing_completion=0.06,
        )

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_model
        mock_db.close = Mock()

        with patch("gaiarouter.stats.collector.get_db", return_value=iter([mock_db])):
            # Small token counts
            cost = collector.calculate_cost("openai/gpt-4", prompt_tokens=50, completion_tokens=25)

        # 50 * $0.03/1K + 25 * $0.06/1K = $0.0015 + $0.0015 = $0.003
        assert cost == 0.003


class TestStatsRecordingIntegrity:
    """测试统计记录完整性"""

    @pytest.fixture
    def collector(self):
        return StatsCollector()

    def test_stat_record_fields(self, collector):
        """测试统计记录字段完整性"""
        mock_db = MagicMock()
        captured_stat = None

        def capture_stat(stat):
            nonlocal captured_stat
            captured_stat = stat

        mock_db.add = Mock(side_effect=capture_stat)
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        mock_db.close = Mock()

        with (
            patch("gaiarouter.stats.collector.get_db", return_value=iter([mock_db])),
            patch.object(collector, "calculate_cost", return_value=0.05),
        ):
            collector.record_request_sync(
                api_key_id="ak_test123",
                organization_id="org_test",
                model="openai/gpt-4",
                provider="openai",
                prompt_tokens=1000,
                completion_tokens=500,
                total_tokens=1500,
            )

        assert captured_stat is not None
        assert captured_stat.api_key_id == "ak_test123"
        assert captured_stat.organization_id == "org_test"
        assert captured_stat.model == "openai/gpt-4"
        assert captured_stat.provider == "openai"
        assert captured_stat.prompt_tokens == 1000
        assert captured_stat.completion_tokens == 500
        assert captured_stat.total_tokens == 1500
        assert captured_stat.cost == 0.05
        assert isinstance(captured_stat.timestamp, datetime)
