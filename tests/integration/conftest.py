"""
集成测试配置和 fixtures

提供测试数据库、测试客户端和认证模拟
"""

from typing import Generator
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from gaiarouter.database.connection import get_db
from gaiarouter.database.models import APIKey, Base, Model, Organization, User
from gaiarouter.main import app


@pytest.fixture(scope="function")
def test_db_engine():
    """创建测试数据库引擎（内存数据库）"""
    # 使用 SQLite 内存数据库进行测试
    engine = create_engine(
        "sqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},  # SQLite 需要这个参数
    )
    # 创建所有表
    Base.metadata.create_all(engine)
    yield engine
    # 清理
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_db_session(test_db_engine) -> Generator[Session, None, None]:
    """创建测试数据库会话（每个测试函数独立）"""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_db_engine
    )
    session = TestingSessionLocal()

    yield session

    # 清理
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def test_client_with_db(test_db_session):
    """创建带有测试数据库的测试客户端"""

    def override_get_db():
        """覆盖数据库依赖"""
        try:
            yield test_db_session
        finally:
            pass

    # 覆盖数据库依赖
    app.dependency_overrides[get_db] = override_get_db

    # 创建测试客户端
    client = TestClient(app)

    yield client

    # 清理依赖覆盖
    app.dependency_overrides = {}


@pytest.fixture
def test_organization(test_db_session):
    """创建测试组织"""
    org = Organization(
        id="test_org_001",
        name="Test Organization",
        status="active",
        monthly_requests_limit=10000,
        monthly_tokens_limit=1000000,
        monthly_cost_limit=100.0,
    )
    test_db_session.add(org)
    test_db_session.commit()
    test_db_session.refresh(org)
    return org


@pytest.fixture
def test_model(test_db_session):
    """创建测试模型"""
    model = Model(
        id="openai/gpt-4",
        name="GPT-4",
        provider="openai",
        is_enabled=True,
        pricing_prompt=0.03,
        pricing_completion=0.06,
    )
    test_db_session.add(model)
    test_db_session.commit()
    test_db_session.refresh(model)
    return model


@pytest.fixture
def test_api_key(test_db_session, test_organization):
    """创建测试 API Key"""
    api_key = APIKey(
        id="test_key_001",
        organization_id=test_organization.id,
        name="Test API Key",
        key="sk-test-key-12345",
        permissions=["read", "write"],
        status="active",
    )
    test_db_session.add(api_key)
    test_db_session.commit()
    test_db_session.refresh(api_key)
    return api_key


@pytest.fixture
def test_admin_user(test_db_session):
    """创建测试管理员用户"""
    user = User(
        id="admin_001",
        username="admin",
        password_hash="hashed_password",
        role="admin",
        status="active",
    )
    test_db_session.add(user)
    test_db_session.commit()
    test_db_session.refresh(user)
    return user


@pytest.fixture
def mock_api_key_manager_for_no_auth():
    """模拟 API Key 管理器（用于缺少认证的测试）"""
    from gaiarouter.auth.api_key_manager import get_api_key_manager

    mock_manager = Mock()
    # 这个 fixture 不会被调用，因为请求会在验证authorization header时就失败

    def override_get_api_key_manager():
        return mock_manager

    # 使用 patch 来覆盖
    import gaiarouter.api.middleware.auth as auth_module

    original = auth_module.get_api_key_manager
    auth_module.get_api_key_manager = override_get_api_key_manager

    yield mock_manager

    # 恢复原始函数
    auth_module.get_api_key_manager = original


@pytest.fixture
def mock_verify_api_key_for_no_auth():
    """模拟 verify_api_key 依赖以正确返回 401 错误"""
    from fastapi import HTTPException, status
    from gaiarouter.api.middleware.auth import verify_api_key

    async def override_verify_api_key(authorization: str = None):
        """模拟认证验证 - 总是返回 401"""
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid API Key",
        )

    app.dependency_overrides[verify_api_key] = override_verify_api_key

    yield

    # 清理
    if verify_api_key in app.dependency_overrides:
        del app.dependency_overrides[verify_api_key]


@pytest.fixture
def test_client_for_no_auth(test_client_with_db, mock_verify_api_key_for_no_auth):
    """创建用于测试缺少认证的客户端"""
    return test_client_with_db


@pytest.fixture
def mock_verify_api_key(test_api_key):
    """模拟 API Key 验证依赖"""
    from gaiarouter.api.middleware.auth import verify_api_key

    async def override_verify_api_key():
        """返回测试 API Key"""
        return test_api_key

    app.dependency_overrides[verify_api_key] = override_verify_api_key

    yield test_api_key

    # 清理
    if verify_api_key in app.dependency_overrides:
        del app.dependency_overrides[verify_api_key]


@pytest.fixture
def mock_model_manager(test_model):
    """模拟模型管理器"""
    from gaiarouter.models.manager import get_model_manager

    mock_manager = Mock()
    mock_manager.get_model.return_value = test_model

    def override_get_model_manager():
        return mock_manager

    # 使用 patch 来覆盖
    import gaiarouter.api.controllers.chat as chat_module

    original = chat_module.get_model_manager
    chat_module.get_model_manager = override_get_model_manager

    yield mock_manager

    # 恢复原始函数
    chat_module.get_model_manager = original


@pytest.fixture
def mock_model_router():
    """模拟模型路由器"""
    from gaiarouter.router import get_model_router

    # 创建 mock provider 和 adapters
    mock_provider = Mock()
    mock_provider.chat_completion = AsyncMock()

    # 模拟响应
    mock_response = Mock()
    mock_response.prompt_tokens = 10
    mock_response.completion_tokens = 20
    mock_response.total_tokens = 30
    mock_provider.chat_completion.return_value = mock_response

    mock_request_adapter = Mock()
    mock_request_adapter.adapt.return_value = {
        "messages": [{"role": "user", "content": "Hello"}]
    }

    mock_response_adapter = Mock()
    mock_response_adapter.adapt.return_value = {
        "id": "test-id",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "openai/gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": "Hello!"},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
    }

    mock_router = Mock()
    mock_router.route.return_value = (
        mock_provider,
        mock_request_adapter,
        mock_response_adapter,
        "gpt-4",
    )

    def override_get_model_router():
        return mock_router

    # 使用 patch 来覆盖
    import gaiarouter.api.controllers.chat as chat_module

    original = chat_module.get_model_router
    chat_module.get_model_router = override_get_model_router

    yield mock_router

    # 恢复原始函数
    chat_module.get_model_router = original


@pytest.fixture
def mock_limit_checker():
    """模拟使用限制检查器"""
    from gaiarouter.organizations.limits import get_limit_checker

    mock_checker = Mock()
    mock_checker.check_limits.return_value = None  # No exception means limits are OK

    def override_get_limit_checker():
        return mock_checker

    # 使用 patch 来覆盖
    import gaiarouter.api.controllers.chat as chat_module

    original = chat_module.get_limit_checker
    chat_module.get_limit_checker = override_get_limit_checker

    yield mock_checker

    # 恢复原始函数
    chat_module.get_limit_checker = original


@pytest.fixture
def mock_stats_collector():
    """模拟统计收集器"""
    from gaiarouter.stats.collector import get_stats_collector

    mock_collector = Mock()
    mock_collector.record_request_sync.return_value = None

    def override_get_stats_collector():
        return mock_collector

    # 使用 patch 来覆盖
    import gaiarouter.api.controllers.chat as chat_module

    original = chat_module.get_stats_collector
    chat_module.get_stats_collector = override_get_stats_collector

    yield mock_collector

    # 恢复原始函数
    chat_module.get_stats_collector = original


@pytest.fixture
def test_client_with_auth(
    test_client_with_db,
    mock_verify_api_key,
    test_model,
    mock_model_manager,
    mock_model_router,
    mock_limit_checker,
    mock_stats_collector,
):
    """创建带有认证和所有必要 mocks 的测试客户端"""
    return test_client_with_db
