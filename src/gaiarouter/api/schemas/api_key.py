"""
API Key数据模型

定义API Key相关的请求和响应模型
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class CreateAPIKeyRequest(BaseModel):
    """创建API Key请求"""

    organization_id: str = Field(..., description="组织ID")

    class Config:
        json_schema_extra = {"example": {"organization_id": "org_1234567890abcdef"}}


class UpdateAPIKeyRequest(BaseModel):
    """更新API Key请求"""

    name: Optional[str] = Field(None, description="API Key名称")
    description: Optional[str] = Field(None, description="描述")
    permissions: Optional[List[str]] = Field(None, description="权限列表")
    status: Optional[str] = Field(None, description="状态：active/inactive")
    expires_at: Optional[str] = Field(None, description="过期时间（ISO 8601格式）")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Updated API Key Name",
                "description": "Updated description",
                "permissions": ["read"],
                "status": "inactive",
            }
        }


class APIKeyResponse(BaseModel):
    """API Key响应"""

    id: str = Field(..., description="API Key ID")
    organization_id: str = Field(..., description="组织ID")
    organization_name: Optional[str] = Field(None, description="组织名称")
    name: str = Field(..., description="API Key名称")
    description: Optional[str] = Field(None, description="描述")
    key: Optional[str] = Field(None, description="API Key值")
    permissions: List[str] = Field(..., description="权限列表")
    status: str = Field(..., description="状态")
    created_at: str = Field(..., description="创建时间")
    expires_at: Optional[str] = Field(None, description="过期时间")
    last_used_at: Optional[str] = Field(None, description="最后使用时间")
    updated_at: Optional[str] = Field(None, description="更新时间")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "ak_1234567890abcdef",
                "name": "My API Key",
                "description": "API Key for production use",
                "permissions": ["read", "write"],
                "status": "active",
                "created_at": "2024-01-01T00:00:00Z",
                "expires_at": "2024-12-31T23:59:59Z",
                "last_used_at": "2024-01-15T10:30:00Z",
            }
        }
        # 确保序列化时包含None值
        from_attributes = True


class APIKeyListResponse(BaseModel):
    """API Key列表响应"""

    data: List[APIKeyResponse] = Field(..., description="API Key列表")
    pagination: dict = Field(..., description="分页信息")

    class Config:
        json_schema_extra = {
            "example": {
                "data": [
                    {
                        "id": "ak_1234567890abcdef",
                        "name": "My API Key",
                        "permissions": ["read", "write"],
                        "status": "active",
                    }
                ],
                "pagination": {"page": 1, "limit": 20, "total": 1, "pages": 1},
            }
        }
