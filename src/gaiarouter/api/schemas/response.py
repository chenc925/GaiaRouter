"""
响应数据模型
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """聊天消息"""

    role: str = Field(..., description="角色")
    content: str = Field(..., description="消息内容")


class ChatChoice(BaseModel):
    """聊天选择"""

    index: int = Field(..., description="选择索引")
    message: ChatMessage = Field(..., description="消息")
    finish_reason: Optional[str] = Field(None, description="完成原因")


class Usage(BaseModel):
    """Token使用量"""

    prompt_tokens: int = Field(0, description="输入token数")
    completion_tokens: int = Field(0, description="输出token数")
    total_tokens: int = Field(0, description="总token数")


class ChatResponse(BaseModel):
    """聊天完成响应模型"""

    id: str = Field(..., description="响应ID")
    object: str = Field("chat.completion", description="对象类型")
    created: int = Field(..., description="创建时间戳")
    model: str = Field(..., description="模型名称")
    choices: List[ChatChoice] = Field(..., description="选择列表")
    usage: Usage = Field(..., description="Token使用量")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "chatcmpl-123",
                "object": "chat.completion",
                "created": 1677652288,
                "model": "openai/gpt-4",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "Hello! How can I help you?"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            }
        }


class ErrorDetail(BaseModel):
    """错误详情"""

    message: str = Field(..., description="错误消息")
    type: str = Field(..., description="错误类型")
    code: Optional[str] = Field(None, description="错误代码")


class ErrorResponse(BaseModel):
    """错误响应模型"""

    error: ErrorDetail = Field(..., description="错误详情")

    class Config:
        json_schema_extra = {
            "example": {
                "error": {
                    "message": "Model not found",
                    "type": "invalid_request_error",
                    "code": "model_not_found",
                }
            }
        }


class ModelInfo(BaseModel):
    """模型信息"""

    id: str = Field(..., description="模型ID")
    object: str = Field("model", description="对象类型")
    created: int = Field(..., description="创建时间戳")
    owned_by: str = Field(..., description="拥有者")
    provider: str = Field(..., description="提供商")


class ModelsResponse(BaseModel):
    """模型列表响应模型"""

    data: List[ModelInfo] = Field(..., description="模型列表")

    class Config:
        json_schema_extra = {
            "example": {
                "data": [
                    {
                        "id": "openai/gpt-4",
                        "object": "model",
                        "created": 1677610602,
                        "owned_by": "openai",
                        "provider": "openai",
                    }
                ]
            }
        }
