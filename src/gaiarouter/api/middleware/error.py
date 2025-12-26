"""
错误处理中间件
"""

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from ...utils.errors import OpenRouterError
from ...utils.logger import get_logger
from ..schemas.response import ErrorDetail, ErrorResponse

logger = get_logger(__name__)


async def error_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    全局错误处理中间件

    Args:
      request: FastAPI请求对象
      exc: 异常对象

    Returns:
      JSONResponse: 错误响应（包含CORS头）
    """
    # 获取请求的Origin头，用于CORS
    origin = request.headers.get("origin")
    cors_headers = {}
    if origin and origin in [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]:
        cors_headers = {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }

    if isinstance(exc, OpenRouterError):
        # 将异常类名转换为错误类型（如ModelNotFoundError -> invalid_request_error）
        error_type_map = {
            "ModelNotFoundError": "invalid_request_error",
            "AuthenticationError": "authentication_error",
            "TimeoutError": "timeout_error",
            "InvalidRequestError": "invalid_request_error",
            "RateLimitError": "rate_limit_error",
            "OrganizationLimitError": "rate_limit_error",
        }
        error_type = error_type_map.get(exc.__class__.__name__, "server_error")

        error_response = ErrorResponse(
            error=ErrorDetail(message=exc.message, type=error_type, code=exc.code)
        )
        return JSONResponse(
            status_code=exc.status_code, content=error_response.dict(), headers=cors_headers
        )

    elif isinstance(exc, RequestValidationError):
        # 提取验证错误详情
        errors = exc.errors()
        error_messages = []
        for error in errors:
            field = ".".join(str(loc) for loc in error["loc"])
            error_messages.append(f"{field}: {error['msg']}")

        error_response = ErrorResponse(
            error=ErrorDetail(
                message="Request validation error: " + "; ".join(error_messages),
                type="invalid_request_error",
                code="validation_error",
            )
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response.dict(),
            headers=cors_headers,
        )

    elif isinstance(exc, HTTPException):
        error_response = ErrorResponse(
            error=ErrorDetail(message=exc.detail, type="http_error", code=str(exc.status_code))
        )
        return JSONResponse(
            status_code=exc.status_code, content=error_response.dict(), headers=cors_headers
        )

    else:
        # 未知错误
        logger.exception("Unhandled exception", exc_info=exc)
        error_response = ErrorResponse(
            error=ErrorDetail(
                message="Internal server error", type="server_error", code="internal_error"
            )
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.dict(),
            headers=cors_headers,
        )
