"""
数据库模型定义

使用SQLAlchemy定义数据表结构
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """用户表"""

    __tablename__ = "users"

    id = Column(String(64), primary_key=True, comment="用户ID")
    username = Column(String(255), nullable=False, unique=True, comment="用户名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希值")
    email = Column(String(255), comment="邮箱")
    full_name = Column(String(255), comment="全名")
    role = Column(String(20), default="admin", comment="角色：admin/user")
    status = Column(String(20), default="active", comment="状态：active/inactive")

    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间"
    )
    last_login_at = Column(DateTime, comment="最后登录时间")


class Organization(Base):
    """组织表"""

    __tablename__ = "organizations"

    id = Column(String(64), primary_key=True, comment="组织ID")
    name = Column(String(255), nullable=False, comment="组织名称")
    description = Column(Text, comment="组织描述")
    admin_user_id = Column(String(64), comment="管理员用户ID")
    status = Column(String(20), default="active", comment="状态：active/inactive")

    # 使用限制
    monthly_requests_limit = Column(Integer, comment="月度请求次数限制")
    monthly_tokens_limit = Column(Integer, comment="月度Token限制")
    monthly_cost_limit = Column(Numeric(10, 2), comment="月度费用限制")

    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间"
    )

    # 关系
    api_keys = relationship("APIKey", back_populates="organization", cascade="all, delete-orphan")
    stats = relationship("RequestStat", back_populates="organization")


class APIKey(Base):
    """API Key表"""

    __tablename__ = "api_keys"

    id = Column(String(64), primary_key=True, comment="API Key ID")
    organization_id = Column(
        String(64), ForeignKey("organizations.id"), nullable=False, comment="组织ID"
    )
    name = Column(String(255), nullable=False, comment="API Key名称")
    description = Column(Text, comment="描述")
    key = Column(String(255), nullable=False, unique=True, comment="API Key原始值（明文存储）")
    permissions = Column(JSON, default=["read", "write"], comment="权限列表")
    status = Column(String(20), default="active", comment="状态：active/inactive/expired")
    expires_at = Column(DateTime, comment="过期时间")

    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间"
    )
    last_used_at = Column(DateTime, comment="最后使用时间")

    # 关系
    organization = relationship("Organization", back_populates="api_keys")
    stats = relationship("RequestStat", back_populates="api_key")


class RequestStat(Base):
    """请求统计表"""

    __tablename__ = "request_stats"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="统计ID")
    api_key_id = Column(String(64), ForeignKey("api_keys.id"), nullable=False, comment="API Key ID")
    organization_id = Column(String(64), ForeignKey("organizations.id"), comment="组织ID")

    model = Column(String(255), nullable=False, comment="模型标识")
    provider = Column(String(50), nullable=False, comment="提供商")

    prompt_tokens = Column(Integer, default=0, comment="输入Token数")
    completion_tokens = Column(Integer, default=0, comment="输出Token数")
    total_tokens = Column(Integer, default=0, comment="总Token数")
    cost = Column(Numeric(10, 4), comment="费用")

    timestamp = Column(DateTime, default=datetime.utcnow, index=True, comment="请求时间")

    # 关系
    api_key = relationship("APIKey", back_populates="stats")
    organization = relationship("Organization", back_populates="stats")


class Model(Base):
    """模型表"""

    __tablename__ = "models"

    id = Column(String(255), primary_key=True, comment="模型ID（完整路径，如openai/gpt-4）")
    name = Column(String(255), nullable=False, comment="模型名称")
    description = Column(Text, comment="模型描述")

    # 提供商信息
    provider = Column(String(50), comment="提供商（openrouter, openai, anthropic等）")

    # 能力标签
    context_length = Column(Integer, comment="上下文长度")
    max_completion_tokens = Column(Integer, comment="最大输出Token数")

    # 定价信息
    pricing_prompt = Column(Numeric(10, 6), comment="输入价格（每1K tokens，美元）")
    pricing_completion = Column(Numeric(10, 6), comment="输出价格（每1K tokens，美元）")

    # 功能支持
    supports_vision = Column(Boolean, default=False, comment="是否支持视觉")
    supports_function_calling = Column(Boolean, default=False, comment="是否支持函数调用")
    supports_streaming = Column(Boolean, default=True, comment="是否支持流式输出")

    # 管理字段
    is_enabled = Column(Boolean, default=False, comment="是否启用")
    is_free = Column(Boolean, default=False, comment="是否免费")

    # OpenRouter 特定字段
    openrouter_id = Column(String(255), comment="OpenRouter 模型ID")

    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间"
    )
    synced_at = Column(DateTime, comment="最后同步时间")
