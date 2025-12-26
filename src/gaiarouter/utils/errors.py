"""
错误处理模块

定义统一的错误类型
"""


class OpenRouterError(Exception):
    """OpenRouter基础异常类"""

    def __init__(self, message: str, code: str = None, status_code: int = 500):
        """
        初始化错误

        Args:
          message: 错误消息
          code: 错误代码
          status_code: HTTP状态码
        """
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)


class ModelNotFoundError(OpenRouterError):
    """模型不存在错误"""

    def __init__(self, model: str):
        super().__init__(
            message=f"Model not found: {model}", code="model_not_found", status_code=404
        )


class AuthenticationError(OpenRouterError):
    """认证错误"""

    def __init__(self, message: str = "Invalid API Key"):
        super().__init__(message=message, code="authentication_error", status_code=401)


class TimeoutError(OpenRouterError):
    """超时错误"""

    def __init__(self, message: str = "Request timeout"):
        super().__init__(message=message, code="timeout_error", status_code=504)


class InvalidRequestError(OpenRouterError):
    """无效请求错误"""

    def __init__(self, message: str):
        super().__init__(message=message, code="invalid_request", status_code=400)


class RateLimitError(OpenRouterError):
    """频率限制错误"""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message=message, code="rate_limit_error", status_code=429)


class OrganizationLimitError(OpenRouterError):
    """组织使用限制错误"""

    def __init__(self, message: str = "Organization limit exceeded"):
        super().__init__(message=message, code="organization_limit_error", status_code=429)
