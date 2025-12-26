"""
认证控制器

处理用户登录和认证
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ...auth.jwt_token import get_token_manager
from ...auth.user_manager import get_user_manager
from ...utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/v1/admin", tags=["auth"])


class LoginRequest(BaseModel):
    """登录请求"""

    username: str
    password: str


class LoginResponse(BaseModel):
    """登录响应"""

    token: str
    user_id: str
    username: str
    role: str


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    用户登录

    Args:
      request: 登录请求（用户名和密码）

    Returns:
      LoginResponse: 登录响应（包含JWT token）
    """
    try:
        user_manager = get_user_manager()
        user = user_manager.verify_user(request.username, request.password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password"
            )

        # 生成JWT token
        token_manager = get_token_manager()
        token = token_manager.generate_token(
            user_id=user.id, username=user.username, role=user.role
        )

        logger.info(f"User logged in: {user.username}")

        return LoginResponse(token=token, user_id=user.id, username=user.username, role=user.role)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Login failed", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed"
        )
