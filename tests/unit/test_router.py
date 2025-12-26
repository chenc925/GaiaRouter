"""
测试 Router 模块

测试模型路由逻辑、提供商选择、OpenRouter 前缀处理等
"""

from unittest.mock import Mock, patch

import pytest

from gaiarouter.router.model_router import ModelRouter
from gaiarouter.router.registry import ModelConfig, ModelRegistry
from gaiarouter.utils.errors import ModelNotFoundError


class TestModelRegistry:
    """测试模型注册表"""

    def test_register_model(self):
        """测试注册模型"""
        registry = ModelRegistry()
        initial_count = len(registry.models)

        # 注册新模型
        config = ModelConfig(
            id="test/model-1", provider="test", name="test-model", api_key_env="TEST_API_KEY"
        )
        registry.register(config)

        assert len(registry.models) == initial_count + 1
        assert registry.get("test/model-1") == config

    def test_get_existing_model(self):
        """测试获取已注册的模型"""
        registry = ModelRegistry()

        # OpenAI GPT-4 应该在默认注册表中
        config = registry.get("openai/gpt-4")

        assert config is not None
        assert config.provider == "openai"
        assert config.name == "gpt-4"

    def test_get_nonexistent_model(self):
        """测试获取不存在的模型"""
        registry = ModelRegistry()

        config = registry.get("nonexistent/model")

        assert config is None

    def test_list_models(self):
        """测试列出所有模型"""
        registry = ModelRegistry()

        models = registry.list_models()

        assert len(models) > 0
        assert all(isinstance(m, ModelConfig) for m in models)

    def test_get_provider(self):
        """测试获取模型提供商"""
        registry = ModelRegistry()

        # 测试已注册的模型
        provider = registry.get_provider("openai/gpt-4")
        assert provider == "openai"

        # 测试不存在的模型
        provider = registry.get_provider("nonexistent/model")
        assert provider is None


class TestModelRouter:
    """测试模型路由器"""

    @pytest.fixture
    def mock_router(self, mock_settings):
        """创建模拟的路由器"""
        with patch("gaiarouter.router.model_router.get_settings", return_value=mock_settings):
            with patch("gaiarouter.router.model_router.get_model_registry") as mock_registry:
                # 设置模拟注册表
                registry = Mock()
                registry.get.return_value = ModelConfig(
                    id="openai/gpt-4",
                    provider="openai",
                    name="gpt-4",
                    api_key_env="OPENAI_API_KEY",
                )
                mock_registry.return_value = registry

                router = ModelRouter()
                return router

    def test_init_providers(self, mock_router):
        """测试提供商初始化"""
        assert "openai" in mock_router._providers
        assert "anthropic" in mock_router._providers
        assert "google" in mock_router._providers
        assert "openrouter" in mock_router._providers

    def test_init_adapters(self, mock_router):
        """测试适配器初始化"""
        # 请求适配器
        assert "openai" in mock_router._request_adapters
        assert "anthropic" in mock_router._request_adapters
        assert "google" in mock_router._request_adapters
        assert "openrouter" in mock_router._request_adapters

        # 响应适配器
        assert "openai" in mock_router._response_adapters
        assert "anthropic" in mock_router._response_adapters
        assert "google" in mock_router._response_adapters
        assert "openrouter" in mock_router._response_adapters

    def test_route_standard_model(self, mock_router):
        """测试路由标准模型（provider/model 格式）"""
        provider, req_adapter, resp_adapter, actual_model = mock_router.route("openai/gpt-4")

        assert provider is not None
        assert req_adapter is not None
        assert resp_adapter is not None
        assert actual_model == "gpt-4"

    def test_route_openrouter_prefix(self, mock_router):
        """测试 OpenRouter 前缀处理"""
        # OpenRouter 模型应该去除 openrouter/ 前缀
        provider, req_adapter, resp_adapter, actual_model = mock_router.route(
            "openrouter/anthropic/claude-3-opus"
        )

        assert provider is not None
        assert actual_model == "anthropic/claude-3-opus"

    def test_route_nonexistent_model(self, mock_router):
        """测试路由不存在的模型"""
        # 修改注册表返回 None
        mock_router.registry.get.return_value = None

        with pytest.raises(ModelNotFoundError):
            mock_router.route("nonexistent/model")

    def test_route_unconfigured_provider(self, mock_settings):
        """测试路由未配置的提供商"""
        # 创建一个没有任何提供商配置的路由器
        mock_settings.providers.openai_api_key = None
        mock_settings.providers.anthropic_api_key = None
        mock_settings.providers.google_api_key = None
        mock_settings.providers.openrouter_api_key = None

        with patch("gaiarouter.router.model_router.get_settings", return_value=mock_settings):
            with patch("gaiarouter.router.model_router.get_model_registry") as mock_registry:
                registry = Mock()
                registry.get.return_value = ModelConfig(
                    id="openai/gpt-4", provider="openai", name="gpt-4"
                )
                mock_registry.return_value = registry

                router = ModelRouter()

                with pytest.raises(ModelNotFoundError, match="Provider openai not configured"):
                    router.route("openai/gpt-4")

    def test_get_provider_success(self, mock_router):
        """测试获取提供商（成功）"""
        provider = mock_router.get_provider("openai/gpt-4")

        assert provider is not None

    def test_get_provider_failure(self, mock_router):
        """测试获取提供商（失败）"""
        mock_router.registry.get.return_value = None

        provider = mock_router.get_provider("nonexistent/model")

        assert provider is None

    def test_route_returns_correct_adapter_types(self, mock_router):
        """测试路由返回正确的适配器类型"""
        provider, req_adapter, resp_adapter, actual_model = mock_router.route("openai/gpt-4")

        # 验证适配器有必要的方法
        assert hasattr(req_adapter, "adapt")
        assert hasattr(resp_adapter, "adapt")
        assert hasattr(resp_adapter, "adapt_stream_chunk")


class TestModelRouterIntegration:
    """测试路由器集成场景"""

    @pytest.fixture
    def real_router(self, mock_settings):
        """创建真实配置的路由器（用于集成测试）"""
        with patch("gaiarouter.router.model_router.get_settings", return_value=mock_settings):
            router = ModelRouter()
            return router

    def test_route_multiple_providers(self, real_router):
        """测试路由到不同提供商"""
        # OpenAI
        provider1, _, _, model1 = real_router.route("openai/gpt-4")
        assert model1 == "gpt-4"

        # Anthropic
        provider2, _, _, model2 = real_router.route("anthropic/claude-3-opus")
        assert "claude" in model2

        # Google
        provider3, _, _, model3 = real_router.route("google/gemini-pro")
        assert model3 == "gemini-pro"

    def test_openrouter_free_models(self, real_router):
        """测试 OpenRouter 免费模型"""
        provider, _, _, actual_model = real_router.route(
            "openrouter/meta-llama/llama-3.2-3b-instruct:free"
        )

        assert actual_model == "meta-llama/llama-3.2-3b-instruct:free"

    def test_consistent_adapter_per_provider(self, real_router):
        """测试同一提供商的模型使用相同的适配器"""
        _, req1, resp1, _ = real_router.route("openai/gpt-4")
        _, req2, resp2, _ = real_router.route("openai/gpt-3.5-turbo")

        # 同一提供商应该使用相同的适配器实例
        assert req1 is req2
        assert resp1 is resp2
