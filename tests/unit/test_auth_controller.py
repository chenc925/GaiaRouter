"""
测试 Auth Controller

测试认证端点的各种场景
"""

from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException

from gaiarouter.api.controllers.auth import login
from gaiarouter.database.models import User


class TestLogin:
    """测试用户登录"""

    @pytest.fixture
    def login_request(self):
        """创建登录请求"""
        request = Mock()
        request.username = "admin"
        request.password = "password123"
        return request

    @pytest.fixture
    def mock_user(self):
        """创建 mock 用户"""
        return User(id="user_123", username="admin", role="admin", status="active")

    @pytest.mark.asyncio
    async def test_login_success(self, login_request, mock_user):
        """测试成功登录"""
        with (
            patch("gaiarouter.api.controllers.auth.get_user_manager") as mock_user_mgr,
            patch("gaiarouter.api.controllers.auth.get_token_manager") as mock_token_mgr,
        ):
            # Setup user manager
            user_mgr_instance = Mock()
            user_mgr_instance.verify_user.return_value = mock_user
            mock_user_mgr.return_value = user_mgr_instance

            # Setup token manager
            token_mgr_instance = Mock()
            token_mgr_instance.generate_token.return_value = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            mock_token_mgr.return_value = token_mgr_instance

            # Call login
            response = await login(login_request)

            # Verify
            assert response.token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            assert response.user_id == "user_123"
            assert response.username == "admin"
            assert response.role == "admin"

            # Verify managers were called correctly
            user_mgr_instance.verify_user.assert_called_once_with("admin", "password123")
            token_mgr_instance.generate_token.assert_called_once_with(
                user_id="user_123", username="admin", role="admin"
            )

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, login_request):
        """测试无效的用户名或密码"""
        with patch("gaiarouter.api.controllers.auth.get_user_manager") as mock_user_mgr:
            # Setup user manager to return None (invalid credentials)
            user_mgr_instance = Mock()
            user_mgr_instance.verify_user.return_value = None
            mock_user_mgr.return_value = user_mgr_instance

            # Should raise 401 Unauthorized
            with pytest.raises(HTTPException) as exc_info:
                await login(login_request)

            assert exc_info.value.status_code == 401
            assert "Invalid username or password" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_login_wrong_password(self):
        """测试错误的密码"""
        request = Mock()
        request.username = "admin"
        request.password = "wrongpassword"

        with patch("gaiarouter.api.controllers.auth.get_user_manager") as mock_user_mgr:
            user_mgr_instance = Mock()
            user_mgr_instance.verify_user.return_value = None
            mock_user_mgr.return_value = user_mgr_instance

            with pytest.raises(HTTPException) as exc_info:
                await login(request)

            assert exc_info.value.status_code == 401
            user_mgr_instance.verify_user.assert_called_once_with("admin", "wrongpassword")

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self):
        """测试不存在的用户"""
        request = Mock()
        request.username = "nonexistent"
        request.password = "password123"

        with patch("gaiarouter.api.controllers.auth.get_user_manager") as mock_user_mgr:
            user_mgr_instance = Mock()
            user_mgr_instance.verify_user.return_value = None
            mock_user_mgr.return_value = user_mgr_instance

            with pytest.raises(HTTPException) as exc_info:
                await login(request)

            assert exc_info.value.status_code == 401
            assert "Invalid username or password" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_login_different_roles(self):
        """测试不同角色的用户登录"""
        request = Mock()
        request.username = "testuser"
        request.password = "password"

        # Test regular user
        regular_user = User(id="user_456", username="testuser", role="user", status="active")

        with (
            patch("gaiarouter.api.controllers.auth.get_user_manager") as mock_user_mgr,
            patch("gaiarouter.api.controllers.auth.get_token_manager") as mock_token_mgr,
        ):
            user_mgr_instance = Mock()
            user_mgr_instance.verify_user.return_value = regular_user
            mock_user_mgr.return_value = user_mgr_instance

            token_mgr_instance = Mock()
            token_mgr_instance.generate_token.return_value = "token_for_regular_user"
            mock_token_mgr.return_value = token_mgr_instance

            response = await login(request)

            assert response.role == "user"
            assert response.username == "testuser"
            token_mgr_instance.generate_token.assert_called_once_with(
                user_id="user_456", username="testuser", role="user"
            )

    @pytest.mark.asyncio
    async def test_login_token_generation(self, login_request, mock_user):
        """测试 token 生成"""
        with (
            patch("gaiarouter.api.controllers.auth.get_user_manager") as mock_user_mgr,
            patch("gaiarouter.api.controllers.auth.get_token_manager") as mock_token_mgr,
        ):
            user_mgr_instance = Mock()
            user_mgr_instance.verify_user.return_value = mock_user
            mock_user_mgr.return_value = user_mgr_instance

            # Test with specific token
            token_mgr_instance = Mock()
            expected_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidXNlcl8xMjMifQ.signature"
            token_mgr_instance.generate_token.return_value = expected_token
            mock_token_mgr.return_value = token_mgr_instance

            response = await login(login_request)

            assert response.token == expected_token

    @pytest.mark.asyncio
    async def test_login_error_handling(self, login_request):
        """测试登录错误处理"""
        with patch("gaiarouter.api.controllers.auth.get_user_manager") as mock_user_mgr:
            user_mgr_instance = Mock()
            user_mgr_instance.verify_user.side_effect = Exception("Database connection error")
            mock_user_mgr.return_value = user_mgr_instance

            with pytest.raises(HTTPException) as exc_info:
                await login(login_request)

            assert exc_info.value.status_code == 500
            assert "Login failed" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_login_token_manager_error(self, login_request, mock_user):
        """测试 token 管理器错误"""
        with (
            patch("gaiarouter.api.controllers.auth.get_user_manager") as mock_user_mgr,
            patch("gaiarouter.api.controllers.auth.get_token_manager") as mock_token_mgr,
        ):
            # User verification succeeds
            user_mgr_instance = Mock()
            user_mgr_instance.verify_user.return_value = mock_user
            mock_user_mgr.return_value = user_mgr_instance

            # Token generation fails
            token_mgr_instance = Mock()
            token_mgr_instance.generate_token.side_effect = Exception("Token generation failed")
            mock_token_mgr.return_value = token_mgr_instance

            with pytest.raises(HTTPException) as exc_info:
                await login(login_request)

            assert exc_info.value.status_code == 500
            assert "Login failed" in str(exc_info.value.detail)


class TestLoginEdgeCases:
    """测试登录边缘情况"""

    @pytest.mark.asyncio
    async def test_login_empty_username(self):
        """测试空用户名"""
        request = Mock()
        request.username = ""
        request.password = "password123"

        with patch("gaiarouter.api.controllers.auth.get_user_manager") as mock_user_mgr:
            user_mgr_instance = Mock()
            user_mgr_instance.verify_user.return_value = None
            mock_user_mgr.return_value = user_mgr_instance

            with pytest.raises(HTTPException) as exc_info:
                await login(request)

            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_login_empty_password(self):
        """测试空密码"""
        request = Mock()
        request.username = "admin"
        request.password = ""

        with patch("gaiarouter.api.controllers.auth.get_user_manager") as mock_user_mgr:
            user_mgr_instance = Mock()
            user_mgr_instance.verify_user.return_value = None
            mock_user_mgr.return_value = user_mgr_instance

            with pytest.raises(HTTPException) as exc_info:
                await login(request)

            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_login_special_characters_username(self):
        """测试包含特殊字符的用户名"""
        request = Mock()
        request.username = "admin@example.com"
        request.password = "password123"

        mock_user = User(
            id="user_789", username="admin@example.com", role="admin", status="active"
        )

        with (
            patch("gaiarouter.api.controllers.auth.get_user_manager") as mock_user_mgr,
            patch("gaiarouter.api.controllers.auth.get_token_manager") as mock_token_mgr,
        ):
            user_mgr_instance = Mock()
            user_mgr_instance.verify_user.return_value = mock_user
            mock_user_mgr.return_value = user_mgr_instance

            token_mgr_instance = Mock()
            token_mgr_instance.generate_token.return_value = "token_123"
            mock_token_mgr.return_value = token_mgr_instance

            response = await login(request)

            assert response.username == "admin@example.com"

    @pytest.mark.asyncio
    async def test_login_case_sensitive(self):
        """测试用户名大小写敏感性"""
        request = Mock()
        request.username = "Admin"  # Capital A
        request.password = "password123"

        with patch("gaiarouter.api.controllers.auth.get_user_manager") as mock_user_mgr:
            user_mgr_instance = Mock()
            # Assuming the system is case-sensitive and "Admin" != "admin"
            user_mgr_instance.verify_user.return_value = None
            mock_user_mgr.return_value = user_mgr_instance

            with pytest.raises(HTTPException) as exc_info:
                await login(request)

            assert exc_info.value.status_code == 401
            # Verify the exact username was passed (preserving case)
            user_mgr_instance.verify_user.assert_called_once_with("Admin", "password123")

    @pytest.mark.asyncio
    async def test_login_long_token(self):
        """测试长 token"""
        request = Mock()
        request.username = "admin"
        request.password = "password123"

        mock_user = User(id="user_123", username="admin", role="admin", status="active")

        # Very long token (JWT tokens can be quite long)
        long_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9." + "a" * 500 + ".signature"

        with (
            patch("gaiarouter.api.controllers.auth.get_user_manager") as mock_user_mgr,
            patch("gaiarouter.api.controllers.auth.get_token_manager") as mock_token_mgr,
        ):
            user_mgr_instance = Mock()
            user_mgr_instance.verify_user.return_value = mock_user
            mock_user_mgr.return_value = user_mgr_instance

            token_mgr_instance = Mock()
            token_mgr_instance.generate_token.return_value = long_token
            mock_token_mgr.return_value = token_mgr_instance

            response = await login(request)

            assert response.token == long_token
            assert len(response.token) > 500
