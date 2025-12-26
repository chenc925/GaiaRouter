"""
pytest 配置和共享 fixtures
"""

import sys
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, Mock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# 添加 src 目录到 Python 路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from gaiarouter.database.models import APIKey, Base, Model, Organization, RequestStat


@pytest.fixture(scope="session")
def test_db_engine():
    """创建测试数据库引擎（内存数据库）"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="function")
def db_session(test_db_engine) -> Generator[Session, None, None]:
    """创建测试数据库会话（每个测试函数独立）"""
    TestingSessionLocal = sessionmaker(bind=test_db_engine)
    session = TestingSessionLocal()

    yield session

    # 清理
    session.rollback()
    session.close()


@pytest.fixture
def mock_settings():
    """模拟配置对象"""
    settings = Mock()
    settings.max_retries = 3
    settings.request_timeout = 30
    settings.providers = Mock()
    settings.providers.openai_api_key = "test-openai-key"
    settings.providers.anthropic_api_key = "test-anthropic-key"
    settings.providers.google_api_key = "test-google-key"
    settings.providers.openrouter_api_key = "test-openrouter-key"
    return settings


@pytest.fixture
def sample_organization(db_session):
    """创建测试组织"""
    org = Organization(
        id="test-org-001",
        name="Test Organization",
        monthly_requests_limit=10000,
        monthly_tokens_limit=1000000,
        monthly_cost_limit=100.0,
    )
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org


@pytest.fixture
def sample_api_key(db_session, sample_organization):
    """创建测试 API Key"""
    api_key = APIKey(
        id="ak_test123",
        organization_id=sample_organization.id,
        name="Test API Key",
        key="sk-or-v1-test-key-123",
        permissions=["read", "write"],
        status="active",
    )
    db_session.add(api_key)
    db_session.commit()
    db_session.refresh(api_key)
    return api_key


@pytest.fixture
def sample_model(db_session):
    """创建测试模型"""
    model = Model(
        id="openai/gpt-4",
        name="GPT-4",
        provider="openai",
        pricing_prompt=0.03,
        pricing_completion=0.06,
    )
    db_session.add(model)
    db_session.commit()
    db_session.refresh(model)
    return model


@pytest.fixture
def sample_request_stat(db_session, sample_api_key):
    """创建测试请求统计"""
    stat = RequestStat(
        api_key_id=sample_api_key.id,
        organization_id=sample_api_key.organization_id,
        model="openai/gpt-4",
        provider="openai",
        prompt_tokens=100,
        completion_tokens=200,
        total_tokens=300,
        cost=0.015,
    )
    db_session.add(stat)
    db_session.commit()
    db_session.refresh(stat)
    return stat


@pytest.fixture
def sample_unified_request():
    """标准的统一格式请求"""
    return {
        "model": "openai/gpt-4",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
        ],
        "temperature": 0.7,
        "max_tokens": 100,
        "stream": False,
    }


@pytest.fixture
def sample_openai_response():
    """OpenAI 格式的响应"""
    return {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": "Hello! How can I help you today?"},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 20, "completion_tokens": 10, "total_tokens": 30},
    }


@pytest.fixture
def sample_anthropic_response():
    """Anthropic 格式的响应"""
    return {
        "id": "msg_123",
        "type": "message",
        "role": "assistant",
        "content": [{"type": "text", "text": "Hello! How can I help you today?"}],
        "model": "claude-3-opus-20240229",
        "stop_reason": "end_turn",
        "usage": {"input_tokens": 20, "output_tokens": 10},
    }


@pytest.fixture
def mock_httpx_client():
    """模拟 httpx 客户端"""
    client = MagicMock()
    return client
