"""
组织数据模型

定义组织相关的请求和响应模型
"""

from typing import Optional
from pydantic import BaseModel, Field


class CreateOrganizationRequest(BaseModel):
  """创建组织请求"""
  name: str = Field(..., description="组织名称")
  description: Optional[str] = Field(None, description="描述")
  monthly_requests_limit: Optional[int] = Field(None, description="月度请求次数限制")
  monthly_tokens_limit: Optional[int] = Field(None, description="月度Token限制")
  monthly_cost_limit: Optional[float] = Field(None, description="月度费用限制")
  
  class Config:
    json_schema_extra = {
      "example": {
        "name": "My Organization",
        "description": "Organization for production use",
        "monthly_requests_limit": 10000,
        "monthly_tokens_limit": 1000000,
        "monthly_cost_limit": 1000.0
      }
    }


class UpdateOrganizationRequest(BaseModel):
  """更新组织请求"""
  name: Optional[str] = Field(None, description="组织名称")
  description: Optional[str] = Field(None, description="描述")
  admin_user_id: Optional[str] = Field(None, description="管理员用户ID")
  status: Optional[str] = Field(None, description="状态：active/inactive")
  monthly_requests_limit: Optional[int] = Field(None, description="月度请求次数限制")
  monthly_tokens_limit: Optional[int] = Field(None, description="月度Token限制")
  monthly_cost_limit: Optional[float] = Field(None, description="月度费用限制")
  
  class Config:
    json_schema_extra = {
      "example": {
        "name": "Updated Organization Name",
        "description": "Updated description",
        "status": "inactive"
      }
    }


class OrganizationResponse(BaseModel):
  """组织响应"""
  id: str = Field(..., description="组织ID")
  name: str = Field(..., description="组织名称")
  description: Optional[str] = Field(None, description="描述")
  admin_user_id: Optional[str] = Field(None, description="管理员用户ID")
  status: str = Field(..., description="状态")
  monthly_requests_limit: Optional[int] = Field(None, description="月度请求次数限制")
  monthly_tokens_limit: Optional[int] = Field(None, description="月度Token限制")
  monthly_cost_limit: Optional[float] = Field(None, description="月度费用限制")
  created_at: str = Field(..., description="创建时间")
  updated_at: str = Field(..., description="更新时间")
  
  class Config:
    json_schema_extra = {
      "example": {
        "id": "org_1234567890abcdef",
        "name": "My Organization",
        "description": "Organization for production use",
        "status": "active",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
      }
    }


class OrganizationListResponse(BaseModel):
  """组织列表响应"""
  data: list[OrganizationResponse] = Field(..., description="组织列表")
  pagination: dict = Field(..., description="分页信息")
  
  class Config:
    json_schema_extra = {
      "example": {
        "data": [
          {
            "id": "org_1234567890abcdef",
            "name": "My Organization",
            "status": "active"
          }
        ],
        "pagination": {
          "page": 1,
          "limit": 20,
          "total": 1,
          "pages": 1
        }
      }
    }

