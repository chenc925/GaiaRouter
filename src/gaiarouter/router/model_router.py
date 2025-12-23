"""
模型路由

根据模型标识符选择对应的提供商和适配器
"""

from typing import Dict, Any, Tuple, Optional
from ..router.registry import get_model_registry
from ..providers import (
    OpenAIProvider,
    AnthropicProvider,
    GoogleProvider,
    OpenRouterProvider,
    Provider,
)
from ..adapters import (
    OpenAIRequestAdapter,
    OpenAIResponseAdapter,
    AnthropicRequestAdapter,
    AnthropicResponseAdapter,
    GoogleRequestAdapter,
    GoogleResponseAdapter,
    OpenRouterRequestAdapter,
    OpenRouterResponseAdapter,
    RequestAdapter,
    ResponseAdapter,
)
from ..config import get_settings
from ..utils.errors import ModelNotFoundError
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ModelRouter:
    """模型路由器"""

    def __init__(self):
        """初始化路由器"""
        self.registry = get_model_registry()
        self.settings = get_settings()
        self._providers: Dict[str, Provider] = {}
        self._request_adapters: Dict[str, RequestAdapter] = {}
        self._response_adapters: Dict[str, ResponseAdapter] = {}
        self._init_providers()
        self._init_adapters()

    def _init_providers(self):
        """初始化提供商实例"""
        providers_config = self.settings.providers

        # OpenAI Provider
        if providers_config.openai_api_key:
            self._providers["openai"] = OpenAIProvider(api_key=providers_config.openai_api_key)

        # Anthropic Provider
        if providers_config.anthropic_api_key:
            self._providers["anthropic"] = AnthropicProvider(
                api_key=providers_config.anthropic_api_key
            )

        # Google Provider
        if providers_config.google_api_key:
            self._providers["google"] = GoogleProvider(api_key=providers_config.google_api_key)

        # OpenRouter Provider
        if providers_config.openrouter_api_key:
            self._providers["openrouter"] = OpenRouterProvider(
                api_key=providers_config.openrouter_api_key
            )

    def _init_adapters(self):
        """初始化适配器实例"""
        self._request_adapters = {
            "openai": OpenAIRequestAdapter(),
            "anthropic": AnthropicRequestAdapter(),
            "google": GoogleRequestAdapter(),
            "openrouter": OpenRouterRequestAdapter(),
        }

        self._response_adapters = {
            "openai": OpenAIResponseAdapter(),
            "anthropic": AnthropicResponseAdapter(),
            "google": GoogleResponseAdapter(),
            "openrouter": OpenRouterResponseAdapter(),
        }

    def route(self, model_id: str) -> Tuple[Provider, RequestAdapter, ResponseAdapter, str]:
        """
        路由模型到对应的提供商和适配器

        Args:
          model_id: 模型ID，格式为 {provider}/{model-name} 或 openrouter/{original-id}

        Returns:
          Tuple[Provider, RequestAdapter, ResponseAdapter, str]:
            提供商实例、请求适配器、响应适配器、实际模型名称

        Raises:
          ModelNotFoundError: 模型不存在
        """
        # 处理 openrouter/ 前缀
        actual_model_id = model_id
        provider_name = None

        if model_id.startswith("openrouter/"):
            # 去除 openrouter/ 前缀，获取原始模型 ID
            original_id = model_id[len("openrouter/") :]
            provider_name = "openrouter"
            actual_model_id = original_id
        else:
            # 从注册表获取模型配置
            model_config = self.registry.get(model_id)
            if model_config:
                provider_name = model_config.provider
                actual_model_id = model_config.name

        if not provider_name:
            raise ModelNotFoundError(model_id)

        # 获取提供商
        provider = self._providers.get(provider_name)
        if not provider:
            raise ModelNotFoundError(f"Provider {provider_name} not configured")

        # 获取适配器
        request_adapter = self._request_adapters.get(provider_name)
        response_adapter = self._response_adapters.get(provider_name)

        if not request_adapter or not response_adapter:
            raise ModelNotFoundError(f"Adapters for {provider_name} not found")

        logger.info(
            f"Routed model {model_id} to provider {provider_name} with actual model {actual_model_id}"
        )

        return provider, request_adapter, response_adapter, actual_model_id

    def get_provider(self, model_id: str) -> Optional[Provider]:
        """
        获取模型对应的提供商

        Args:
          model_id: 模型ID

        Returns:
          提供商实例，如果不存在返回None
        """
        try:
            provider, _, _, _ = self.route(model_id)
            return provider
        except ModelNotFoundError:
            return None


# 全局路由器实例
_router: Optional[ModelRouter] = None


def get_model_router() -> ModelRouter:
    """获取模型路由器实例（单例模式）"""
    global _router
    if _router is None:
        _router = ModelRouter()
    return _router
