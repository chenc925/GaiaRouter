"""
请求数据模型
"""

from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field, validator


class ContentPart(BaseModel):
    """内容块模型（支持多模态）"""

    type: str = Field(..., description="内容类型：text, image_url")
    text: Optional[str] = Field(None, description="文本内容")
    image_url: Optional[Dict[str, str]] = Field(
        None, description="图片URL，格式：{url: string, detail?: string}"
    )

    @validator("type")
    def validate_type(cls, v):
        """验证内容类型"""
        if v not in ["text", "image_url"]:
            raise ValueError("type must be one of: text, image_url")
        return v


class Message(BaseModel):
    """消息模型（支持多模态内容）"""

    role: str = Field(..., description="角色：system, user, assistant")
    content: Union[str, List[ContentPart]] = Field(
        ..., description="消息内容，可以是字符串或内容块列表"
    )

    @validator("role")
    def validate_role(cls, v):
        """验证角色"""
        if v not in ["system", "user", "assistant"]:
            raise ValueError("role must be one of: system, user, assistant")
        return v


class ChatRequest(BaseModel):
    """聊天完成请求模型"""

    model: str = Field(..., description="模型标识符，格式：{provider}/{model-name}")
    messages: List[Message] = Field(..., min_items=1, description="消息列表")
    temperature: Optional[float] = Field(None, ge=0, le=2, description="温度参数，范围0-2")
    max_tokens: Optional[int] = Field(None, gt=0, description="最大token数")
    top_p: Optional[float] = Field(None, ge=0, le=1, description="Top-p采样参数")
    frequency_penalty: Optional[float] = Field(None, ge=-2, le=2, description="频率惩罚")
    presence_penalty: Optional[float] = Field(None, ge=-2, le=2, description="存在惩罚")
    stream: bool = Field(False, description="是否使用流式响应")

    class Config:
        json_schema_extra = {
            "example": {
                "model": "openai/gpt-4",
                "messages": [{"role": "user", "content": "Hello, world!"}],
                "temperature": 0.7,
                "max_tokens": 1000,
                "stream": False,
            }
        }
