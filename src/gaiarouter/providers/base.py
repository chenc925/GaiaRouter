"""
基础提供商接口

定义Provider的抽象接口
"""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, AsyncIterator, Dict, List, Optional

from ..config import get_settings
from ..utils.errors import TimeoutError
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ProviderResponse:
    """提供商响应数据类"""

    content: str
    model: str
    finish_reason: Optional[str] = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    usage: Optional[Dict[str, Any]] = None


class Provider(ABC):
    """提供商抽象基类"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化提供商

        Args:
          api_key: API密钥
          base_url: API基础URL
        """
        self.api_key = api_key
        self.base_url = base_url or self.get_default_base_url()
        self.settings = get_settings()

    @abstractmethod
    def get_default_base_url(self) -> str:
        """获取默认的API基础URL"""
        pass

    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs,
    ) -> ProviderResponse:
        """
        聊天完成接口

        Args:
          messages: 消息列表
          model: 模型名称
          temperature: 温度参数
          max_tokens: 最大token数
          stream: 是否流式响应
          **kwargs: 其他参数

        Returns:
          ProviderResponse: 响应对象
        """
        pass

    @abstractmethod
    async def stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        流式聊天完成接口

        Args:
          messages: 消息列表
          model: 模型名称
          temperature: 温度参数
          max_tokens: 最大token数
          **kwargs: 其他参数

        Yields:
          Dict: 流式响应块
        """
        pass

    def get_headers(self) -> Dict[str, str]:
        """
        获取请求头

        Returns:
          请求头字典
        """
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def _retry_request(
        self, func, max_retries: Optional[int] = None, retry_delay: float = 1.0, *args, **kwargs
    ):
        """
        重试请求的通用方法

        Args:
          func: 要执行的异步函数
          max_retries: 最大重试次数，默认从配置读取
          retry_delay: 重试延迟（秒）
          *args: 函数位置参数
          **kwargs: 函数关键字参数

        Returns:
          函数执行结果

        Raises:
          最后一次尝试的异常
        """
        if max_retries is None:
            max_retries = self.settings.max_retries

        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except (TimeoutError, Exception) as e:
                last_exception = e
                if attempt < max_retries:
                    wait_time = retry_delay * (2**attempt)  # 指数退避
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}/{max_retries + 1}), "
                        f"retrying in {wait_time}s: {str(e)}"
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Request failed after {max_retries + 1} attempts: {str(e)}")

        raise last_exception
