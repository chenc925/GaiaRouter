"""
模型注册表

管理模型配置和提供商映射
"""

from typing import Dict, Optional, List
from dataclasses import dataclass
from ..config import get_settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ModelConfig:
    """模型配置"""

    id: str  # 完整模型ID，如 openai/gpt-4
    provider: str  # 提供商名称
    name: str  # 模型名称，如 gpt-4
    api_key_env: Optional[str] = None  # API Key环境变量名


class ModelRegistry:
    """模型注册表"""

    def __init__(self):
        """初始化模型注册表"""
        self.models: Dict[str, ModelConfig] = {}
        self._load_default_models()

    def _load_default_models(self):
        """加载默认模型配置"""
        settings = get_settings()

        # OpenAI模型
        self.register(
            ModelConfig(
                id="openai/gpt-4", provider="openai", name="gpt-4", api_key_env="OPENAI_API_KEY"
            )
        )
        self.register(
            ModelConfig(
                id="openai/gpt-3.5-turbo",
                provider="openai",
                name="gpt-3.5-turbo",
                api_key_env="OPENAI_API_KEY",
            )
        )

        # Anthropic模型
        self.register(
            ModelConfig(
                id="anthropic/claude-3-opus",
                provider="anthropic",
                name="claude-3-opus-20240229",
                api_key_env="ANTHROPIC_API_KEY",
            )
        )
        self.register(
            ModelConfig(
                id="anthropic/claude-3-sonnet",
                provider="anthropic",
                name="claude-3-sonnet-20240229",
                api_key_env="ANTHROPIC_API_KEY",
            )
        )

        # Google模型
        self.register(
            ModelConfig(
                id="google/gemini-pro",
                provider="google",
                name="gemini-pro",
                api_key_env="GOOGLE_API_KEY",
            )
        )

        # OpenRouter模型（使用OpenRouter作为提供商）
        # 免费模型
        self.register(
            ModelConfig(
                id="openrouter/meta-llama/llama-3.2-3b-instruct:free",
                provider="openrouter",
                name="meta-llama/llama-3.2-3b-instruct:free",
                api_key_env="OPENROUTER_API_KEY",
            )
        )
        self.register(
            ModelConfig(
                id="openrouter/meta-llama/llama-3.1-8b-instruct:free",
                provider="openrouter",
                name="meta-llama/llama-3.1-8b-instruct:free",
                api_key_env="OPENROUTER_API_KEY",
            )
        )
        self.register(
            ModelConfig(
                id="openrouter/google/gemma-2-9b-it:free",
                provider="openrouter",
                name="google/gemma-2-9b-it:free",
                api_key_env="OPENROUTER_API_KEY",
            )
        )
        self.register(
            ModelConfig(
                id="openrouter/microsoft/phi-3-mini-128k-instruct:free",
                provider="openrouter",
                name="microsoft/phi-3-mini-128k-instruct:free",
                api_key_env="OPENROUTER_API_KEY",
            )
        )
        self.register(
            ModelConfig(
                id="openrouter/qwen/qwen-2-7b-instruct:free",
                provider="openrouter",
                name="qwen/qwen-2-7b-instruct:free",
                api_key_env="OPENROUTER_API_KEY",
            )
        )
        self.register(
            ModelConfig(
                id="openrouter/mistralai/mistral-7b-instruct:free",
                provider="openrouter",
                name="mistralai/mistral-7b-instruct:free",
                api_key_env="OPENROUTER_API_KEY",
            )
        )

        # 付费模型
        self.register(
            ModelConfig(
                id="openrouter/gpt-4",
                provider="openrouter",
                name="openai/gpt-4",
                api_key_env="OPENROUTER_API_KEY",
            )
        )
        self.register(
            ModelConfig(
                id="openrouter/claude-3-opus",
                provider="openrouter",
                name="anthropic/claude-3-opus",
                api_key_env="OPENROUTER_API_KEY",
            )
        )
        self.register(
            ModelConfig(
                id="openrouter/gpt-3.5-turbo",
                provider="openrouter",
                name="openai/gpt-3.5-turbo",
                api_key_env="OPENROUTER_API_KEY",
            )
        )

    def register(self, model: ModelConfig):
        """
        注册模型

        Args:
          model: 模型配置
        """
        self.models[model.id] = model
        logger.info(f"Registered model: {model.id} ({model.provider})")

    def get(self, model_id: str) -> Optional[ModelConfig]:
        """
        获取模型配置

        Args:
          model_id: 模型ID

        Returns:
          模型配置，如果不存在返回None
        """
        return self.models.get(model_id)

    def list_models(self) -> List[ModelConfig]:
        """
        获取所有模型列表

        Returns:
          模型配置列表
        """
        return list(self.models.values())

    def get_provider(self, model_id: str) -> Optional[str]:
        """
        获取模型所属的提供商

        Args:
          model_id: 模型ID

        Returns:
          提供商名称，如果不存在返回None
        """
        model = self.get(model_id)
        return model.provider if model else None


# 全局模型注册表实例
_registry: Optional[ModelRegistry] = None


def get_model_registry() -> ModelRegistry:
    """获取模型注册表实例（单例模式）"""
    global _registry
    if _registry is None:
        _registry = ModelRegistry()
    return _registry
