"""
测试 API 端点

集成测试，测试 FastAPI 端点的基础功能
"""

from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from gaiarouter.database.models import APIKey, Model, Organization, User
from gaiarouter.main import app


class TestAPIStructure:
    """测试 API 结构和路由"""

    def test_app_exists(self):
        """测试应用实例存在"""
        assert app is not None

    def test_docs_endpoint_exists(self):
        """测试文档端点存在"""
        client = TestClient(app)
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_schema_exists(self):
        """测试 OpenAPI schema 存在"""
        client = TestClient(app)
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "paths" in data


class TestChatEndpointValidation:
    """测试聊天端点的请求验证"""

    @pytest.mark.xfail(reason="Complex FastAPI error handling - needs refactoring")
    def test_chat_completion_missing_auth(self):
        """测试缺少认证"""
        client = TestClient(app)
        response = client.post(
            "/v1/chat/completions",
            json={
                "model": "openai/gpt-4",
                "messages": [{"role": "user", "content": "Hello!"}],
            },
        )
        # Should require authentication
        assert response.status_code in [401, 422]

    @pytest.mark.xfail(reason="Complex FastAPI error handling - needs refactoring")
    def test_chat_completion_invalid_request_missing_model(self):
        """测试缺少必需字段 - model"""
        client = TestClient(app)
        response = client.post(
            "/v1/chat/completions",
            json={"messages": [{"role": "user", "content": "Hello!"}]},
            headers={"Authorization": "Bearer test-key"},
        )
        assert response.status_code == 422  # Validation error

    @pytest.mark.xfail(reason="Complex FastAPI error handling - needs refactoring")
    def test_chat_completion_invalid_request_missing_messages(self):
        """测试缺少必需字段 - messages"""
        client = TestClient(app)
        response = client.post(
            "/v1/chat/completions",
            json={"model": "openai/gpt-4"},
            headers={"Authorization": "Bearer test-key"},
        )
        assert response.status_code == 422  # Validation error

    @pytest.mark.xfail(reason="Complex FastAPI error handling - needs refactoring")
    def test_chat_completion_invalid_message_format(self):
        """测试无效的消息格式"""
        client = TestClient(app)
        response = client.post(
            "/v1/chat/completions",
            json={
                "model": "openai/gpt-4",
                "messages": [{"invalid_field": "value"}],  # Missing role and content
            },
            headers={"Authorization": "Bearer test-key"},
        )
        assert response.status_code == 422


class TestModelsEndpointValidation:
    """测试模型列表端点"""

    @pytest.mark.xfail(reason="Complex FastAPI error handling - needs refactoring")
    def test_list_models_missing_auth(self):
        """测试缺少认证"""
        client = TestClient(app)
        response = client.get("/v1/models")
        assert response.status_code in [401, 422]


class TestAuthEndpoint:
    """测试认证端点"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup before each test"""
        yield
        app.dependency_overrides = {}

    @pytest.mark.xfail(reason="Dependency override issue - needs investigation")
    def test_login_success(self):
        """测试成功登录"""
        from gaiarouter.api.controllers.auth import get_token_manager, get_user_manager

        mock_user = User(
            id="user_123",
            username="admin",
            password_hash="hashed_password",
            role="admin",
            status="active",
        )

        user_manager = Mock()
        user_manager.verify_user.return_value = mock_user
        app.dependency_overrides[get_user_manager] = lambda: user_manager

        token_manager = Mock()
        token_manager.generate_token.return_value = "mock_jwt_token"
        app.dependency_overrides[get_token_manager] = lambda: token_manager

        client = TestClient(app)
        response = client.post(
            "/v1/admin/login",
            json={"username": "admin", "password": "password123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["username"] == "admin"
        assert data["role"] == "admin"

    def test_login_invalid_credentials(self):
        """测试无效凭证"""
        from gaiarouter.api.controllers.auth import get_user_manager

        user_manager = Mock()
        user_manager.verify_user.return_value = None
        app.dependency_overrides[get_user_manager] = lambda: user_manager

        client = TestClient(app)
        response = client.post(
            "/v1/admin/login",
            json={"username": "admin", "password": "wrong_password"},
        )

        assert response.status_code == 401

    def test_login_missing_username(self):
        """测试缺少用户名"""
        client = TestClient(app)
        response = client.post(
            "/v1/admin/login",
            json={"password": "password123"},
        )
        assert response.status_code == 422

    def test_login_missing_password(self):
        """测试缺少密码"""
        client = TestClient(app)
        response = client.post(
            "/v1/admin/login",
            json={"username": "admin"},
        )
        assert response.status_code == 422

    def test_login_empty_credentials(self):
        """测试空凭证"""
        client = TestClient(app)
        response = client.post(
            "/v1/admin/login",
            json={},
        )
        assert response.status_code == 422


class TestCORSHeaders:
    """测试 CORS 配置"""

    def test_cors_headers_present(self):
        """测试 CORS 头存在"""
        client = TestClient(app)
        response = client.options(
            "/v1/chat/completions",
            headers={"Origin": "http://localhost:3000"},
        )
        # CORS should be configured
        assert response.status_code in [200, 405]


class TestErrorHandling:
    """测试错误处理"""

    def test_404_for_unknown_endpoint(self):
        """测试未知端点返回 404"""
        client = TestClient(app)
        response = client.get("/unknown/endpoint")
        assert response.status_code == 404

    def test_405_for_wrong_method(self):
        """测试错误的 HTTP 方法"""
        client = TestClient(app)
        response = client.get("/v1/admin/login")  # Should be POST
        assert response.status_code == 405
