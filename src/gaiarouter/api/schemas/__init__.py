"""
API数据模型

定义请求和响应的Pydantic模型
"""

from .request import ChatRequest, Message
from .response import (
  ChatResponse,
  ChatChoice,
  ChatMessage,
  Usage,
  ErrorResponse,
  ErrorDetail,
  ModelInfo,
  ModelsResponse,
)
from .api_key import (
  CreateAPIKeyRequest,
  UpdateAPIKeyRequest,
  APIKeyResponse,
  APIKeyListResponse,
)
from .organization import (
  CreateOrganizationRequest,
  UpdateOrganizationRequest,
  OrganizationResponse,
  OrganizationListResponse,
)

__all__ = [
  "ChatRequest",
  "Message",
  "ChatResponse",
  "ChatChoice",
  "ChatMessage",
  "Usage",
  "ErrorResponse",
  "ErrorDetail",
  "ModelInfo",
  "ModelsResponse",
  "CreateAPIKeyRequest",
  "UpdateAPIKeyRequest",
  "APIKeyResponse",
  "APIKeyListResponse",
  "CreateOrganizationRequest",
  "UpdateOrganizationRequest",
  "OrganizationResponse",
  "OrganizationListResponse",
]
