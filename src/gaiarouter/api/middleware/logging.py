"""
日志中间件

记录请求和响应日志
"""

import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from ...utils.logger import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """日志中间件"""

    async def dispatch(self, request: Request, call_next):
        """
        处理请求并记录日志

        Args:
          request: FastAPI请求对象
          call_next: 下一个中间件或路由处理函数

        Returns:
          Response: HTTP响应
        """
        start_time = time.time()

        # 记录请求信息
        logger.info(
            "Request received",
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None,
        )

        # 处理请求
        response = await call_next(request)

        # 计算处理时间
        process_time = time.time() - start_time

        # 记录响应信息
        logger.info(
            "Request completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            process_time=f"{process_time:.3f}s",
        )

        return response


def log_request(request: Request, response: Response, duration: float):
    """
    记录请求日志（辅助函数）

    Args:
      request: FastAPI请求对象
      response: HTTP响应对象
      duration: 处理时长（秒）
    """
    logger.info(
        "Request processed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration=duration,
    )
