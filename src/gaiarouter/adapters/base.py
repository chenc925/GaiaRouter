"""
基础适配器接口

定义请求和响应适配器的抽象接口
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from ..providers.base import ProviderResponse


class RequestAdapter(ABC):
    """请求适配器抽象基类"""

    @abstractmethod
    def adapt(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        将统一格式的请求转换为提供商格式

        Args:
          request: 统一格式的请求字典

        Returns:
          提供商格式的请求字典
        """
        pass


class ResponseAdapter(ABC):
    """响应适配器抽象基类"""

    @abstractmethod
    def adapt(self, response: ProviderResponse) -> Dict[str, Any]:
        """
        将提供商的响应转换为统一格式

        Args:
          response: ProviderResponse对象

        Returns:
          统一格式的响应字典
        """
        pass

    @abstractmethod
    def adapt_stream_chunk(self, chunk: Dict[str, Any]) -> Dict[str, Any]:
        """
        将流式响应的chunk转换为统一格式

        Args:
          chunk: 提供商返回的chunk字典

        Returns:
          统一格式的chunk字典
        """
        pass
