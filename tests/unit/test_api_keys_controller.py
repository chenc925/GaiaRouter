"""
测试 API Keys Controller

测试 API Key 管理端点的各种场景
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException

from gaiarouter.api.controllers.api_keys import (
    _api_key_to_response,
    create_api_key,
    delete_api_key,
    get_api_key,
    list_api_keys,
    update_api_key,
)
from gaiarouter.database.models import APIKey, Organization, User
from gaiarouter.utils.errors import AuthenticationError, InvalidRequestError


class TestApiKeyToResponse:
    """测试 API Key 转响应函数"""

    def test_convert_with_key(self):
        """测试包含 key 的转换"""
        api_key = APIKey(
            id="ak_123",
            organization_id="org_123",
            name="Test Key",
            description="Test Description",
            key="sk-test123",
            permissions=["read", "write"],
            status="active",
            created_at=datetime(2024, 1, 1),
        )

        response = _api_key_to_response(api_key, include_key=True, organization_name="Test Org")

        assert response.id == "ak_123"
        assert response.organization_id == "org_123"
        assert response.organization_name == "Test Org"
        assert response.name == "Test Key"
        assert response.key == "sk-test123"
        assert response.permissions == ["read", "write"]
        assert response.status == "active"

    def test_convert_without_key(self):
        """测试不包含 key 的转换"""
        api_key = APIKey(
            id="ak_123",
            organization_id="org_123",
            name="Test Key",
            status="active",
            created_at=datetime(2024, 1, 1),
        )

        response = _api_key_to_response(api_key, include_key=False)

        assert response.id == "ak_123"
        assert response.key is None

    def test_convert_with_optional_values(self):
        """测试可选值的转换"""
        api_key = APIKey(
            id="ak_123",
            organization_id="org_123",
            name="Test Key",
            status="active",
            created_at=datetime(2024, 1, 1),
            expires_at=None,
            last_used_at=None,
        )

        response = _api_key_to_response(api_key)

        assert response.created_at == "2024-01-01T00:00:00Z"
        assert response.expires_at is None
        assert response.last_used_at is None


class TestCreateApiKey:
    """测试创建 API Key"""

    @pytest.fixture
    def mock_user(self):
        """创建 mock admin 用户"""
        return User(id="user_123", username="admin", role="admin", status="active")

    @pytest.fixture
    def mock_org(self):
        """创建 mock 组织"""
        return Organization(id="org_123", name="Test Org", status="active")

    @pytest.fixture
    def create_request(self):
        """创建请求对象"""
        request = Mock()
        request.organization_id = "org_123"
        return request

    @pytest.mark.asyncio
    async def test_create_api_key_success(self, mock_user, mock_org, create_request):
        """测试成功创建 API Key"""
        with (
            patch("gaiarouter.organizations.manager.get_organization_manager") as mock_org_mgr,
            patch("gaiarouter.api.controllers.api_keys.get_api_key_manager") as mock_key_mgr,
        ):
            # Mock organization manager
            org_mgr_instance = Mock()
            org_mgr_instance.get_organization.return_value = mock_org
            mock_org_mgr.return_value = org_mgr_instance

            # Mock API key manager
            key_mgr_instance = Mock()
            key_mgr_instance.list_keys.return_value = ([], 0)  # No existing keys

            new_key = APIKey(
                id="ak_new",
                organization_id="org_123",
                name="Test Org API Key",
                description="Auto-generated API Key for Test Org",
                permissions=["read", "write"],
                status="active",
                created_at=datetime.now(),
            )
            key_mgr_instance.create_key.return_value = (new_key, "sk-test123")
            mock_key_mgr.return_value = key_mgr_instance

            # Call the endpoint
            response = await create_api_key(create_request, mock_user)

            # Verify
            assert response.id == "ak_new"
            assert response.organization_id == "org_123"
            assert response.key == "sk-test123"
            assert response.organization_name == "Test Org"
            key_mgr_instance.create_key.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_api_key_non_admin(self, create_request):
        """测试非 admin 用户创建 API Key"""
        non_admin_user = User(id="user_123", username="user", role="user", status="active")

        with pytest.raises(AuthenticationError, match="Insufficient permissions"):
            await create_api_key(create_request, non_admin_user)

    @pytest.mark.asyncio
    async def test_create_api_key_org_not_found(self, mock_user, create_request):
        """测试组织不存在"""
        with patch("gaiarouter.organizations.manager.get_organization_manager") as mock_org_mgr:
            org_mgr_instance = Mock()
            org_mgr_instance.get_organization.return_value = None
            mock_org_mgr.return_value = org_mgr_instance

            with pytest.raises(InvalidRequestError, match="Organization not found"):
                await create_api_key(create_request, mock_user)

    @pytest.mark.asyncio
    async def test_create_api_key_already_exists(self, mock_user, mock_org, create_request):
        """测试组织已有 API Key"""
        with (
            patch("gaiarouter.organizations.manager.get_organization_manager") as mock_org_mgr,
            patch("gaiarouter.api.controllers.api_keys.get_api_key_manager") as mock_key_mgr,
        ):
            org_mgr_instance = Mock()
            org_mgr_instance.get_organization.return_value = mock_org
            mock_org_mgr.return_value = org_mgr_instance

            key_mgr_instance = Mock()
            existing_key = APIKey(id="ak_existing", organization_id="org_123", name="Existing Key")
            key_mgr_instance.list_keys.return_value = ([existing_key], 1)
            mock_key_mgr.return_value = key_mgr_instance

            with pytest.raises(InvalidRequestError, match="already has an API Key"):
                await create_api_key(create_request, mock_user)


class TestListApiKeys:
    """测试列出 API Keys"""

    @pytest.fixture
    def mock_user(self):
        return User(id="user_123", username="admin", role="admin", status="active")

    @pytest.mark.asyncio
    async def test_list_api_keys_success(self, mock_user):
        """测试成功列出 API Keys"""
        mock_keys = [
            APIKey(
                id="ak_1",
                organization_id="org_1",
                name="Key 1",
                status="active",
                created_at=datetime.now(),
            ),
            APIKey(
                id="ak_2",
                organization_id="org_2",
                name="Key 2",
                status="active",
                created_at=datetime.now(),
            ),
        ]

        with (
            patch("gaiarouter.api.controllers.api_keys.get_api_key_manager") as mock_key_mgr,
            patch("gaiarouter.organizations.manager.get_organization_manager") as mock_org_mgr,
        ):
            key_mgr_instance = Mock()
            key_mgr_instance.list_keys.return_value = (mock_keys, 2)
            mock_key_mgr.return_value = key_mgr_instance

            org_mgr_instance = Mock()
            org_mgr_instance.get_organization.side_effect = [
                Organization(id="org_1", name="Org 1"),
                Organization(id="org_2", name="Org 2"),
            ]
            mock_org_mgr.return_value = org_mgr_instance

            response = await list_api_keys(
                page=1, limit=20, status=None, search=None, organization_id=None, user=mock_user
            )

            assert len(response.data) == 2
            assert response.pagination["total"] == 2
            assert response.pagination["page"] == 1
            assert response.data[0].id == "ak_1"

    @pytest.mark.asyncio
    async def test_list_api_keys_with_filters(self, mock_user):
        """测试带筛选条件列出 API Keys"""
        with patch("gaiarouter.api.controllers.api_keys.get_api_key_manager") as mock_key_mgr:
            key_mgr_instance = Mock()
            key_mgr_instance.list_keys.return_value = ([], 0)
            mock_key_mgr.return_value = key_mgr_instance

            await list_api_keys(
                page=1,
                limit=10,
                status="active",
                search="test",
                organization_id="org_123",
                user=mock_user,
            )

            key_mgr_instance.list_keys.assert_called_once_with(
                organization_id="org_123", page=1, limit=10, status="active", search="test"
            )

    @pytest.mark.asyncio
    async def test_list_api_keys_pagination(self, mock_user):
        """测试分页"""
        with (
            patch("gaiarouter.api.controllers.api_keys.get_api_key_manager") as mock_key_mgr,
            patch("gaiarouter.organizations.manager.get_organization_manager") as mock_org_mgr,
        ):
            key_mgr_instance = Mock()
            key_mgr_instance.list_keys.return_value = ([], 25)
            mock_key_mgr.return_value = key_mgr_instance

            org_mgr_instance = Mock()
            mock_org_mgr.return_value = org_mgr_instance

            response = await list_api_keys(
                page=2, limit=10, status=None, search=None, organization_id=None, user=mock_user
            )

            assert response.pagination["page"] == 2
            assert response.pagination["total"] == 25
            assert response.pagination["pages"] == 3  # ceiling(25/10)


class TestGetApiKey:
    """测试获取单个 API Key"""

    @pytest.fixture
    def mock_user(self):
        return User(id="user_123", username="admin", role="admin", status="active")

    @pytest.mark.asyncio
    async def test_get_api_key_success(self, mock_user):
        """测试成功获取 API Key"""
        mock_key = APIKey(
            id="ak_123",
            organization_id="org_123",
            name="Test Key",
            status="active",
            created_at=datetime.now(),
        )

        with patch("gaiarouter.api.controllers.api_keys.get_api_key_manager") as mock_key_mgr:
            key_mgr_instance = Mock()
            key_mgr_instance.get_key.return_value = mock_key
            mock_key_mgr.return_value = key_mgr_instance

            response = await get_api_key("ak_123", mock_user)

            assert response.id == "ak_123"
            assert response.name == "Test Key"

    @pytest.mark.asyncio
    async def test_get_api_key_not_found(self, mock_user):
        """测试 API Key 不存在"""
        with patch("gaiarouter.api.controllers.api_keys.get_api_key_manager") as mock_key_mgr:
            key_mgr_instance = Mock()
            key_mgr_instance.get_key.return_value = None
            mock_key_mgr.return_value = key_mgr_instance

            with pytest.raises(HTTPException) as exc_info:
                await get_api_key("ak_nonexistent", mock_user)

            assert exc_info.value.status_code == 404
            assert "not found" in str(exc_info.value.detail)


class TestUpdateApiKey:
    """测试更新 API Key"""

    @pytest.fixture
    def mock_user(self):
        return User(id="user_123", username="admin", role="admin", status="active")

    @pytest.fixture
    def update_request(self):
        request = Mock()
        request.name = "Updated Key"
        request.description = "Updated Description"
        request.permissions = ["read"]
        request.status = "inactive"
        request.expires_at = None
        return request

    @pytest.mark.asyncio
    async def test_update_api_key_success(self, mock_user, update_request):
        """测试成功更新 API Key"""
        existing_key = APIKey(id="ak_123", organization_id="org_123", name="Old Key", status="active")
        updated_key = APIKey(
            id="ak_123",
            organization_id="org_123",
            name="Updated Key",
            description="Updated Description",
            permissions=["read"],
            status="inactive",
            created_at=datetime.now(),
        )

        with patch("gaiarouter.api.controllers.api_keys.get_api_key_manager") as mock_key_mgr:
            key_mgr_instance = Mock()
            key_mgr_instance.get_key.return_value = existing_key
            key_mgr_instance.update_key.return_value = updated_key
            mock_key_mgr.return_value = key_mgr_instance

            response = await update_api_key("ak_123", update_request, mock_user)

            assert response.id == "ak_123"
            assert response.name == "Updated Key"
            key_mgr_instance.update_key.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_api_key_non_admin(self, update_request):
        """测试非 admin 用户更新 API Key"""
        non_admin_user = User(id="user_123", username="user", role="user", status="active")

        with pytest.raises(AuthenticationError, match="Insufficient permissions"):
            await update_api_key("ak_123", update_request, non_admin_user)

    @pytest.mark.asyncio
    async def test_update_api_key_not_found(self, mock_user, update_request):
        """测试更新不存在的 API Key"""
        with patch("gaiarouter.api.controllers.api_keys.get_api_key_manager") as mock_key_mgr:
            key_mgr_instance = Mock()
            key_mgr_instance.get_key.return_value = None
            mock_key_mgr.return_value = key_mgr_instance

            with pytest.raises(HTTPException) as exc_info:
                await update_api_key("ak_nonexistent", update_request, mock_user)

            assert exc_info.value.status_code == 404


class TestDeleteApiKey:
    """测试删除 API Key"""

    @pytest.fixture
    def mock_user(self):
        return User(id="user_123", username="admin", role="admin", status="active")

    @pytest.mark.asyncio
    async def test_delete_api_key_success(self, mock_user):
        """测试成功删除 API Key"""
        existing_key = APIKey(id="ak_123", organization_id="org_123", name="Test Key", status="active")

        with patch("gaiarouter.api.controllers.api_keys.get_api_key_manager") as mock_key_mgr:
            key_mgr_instance = Mock()
            key_mgr_instance.get_key.return_value = existing_key
            key_mgr_instance.delete_key.return_value = True
            mock_key_mgr.return_value = key_mgr_instance

            response = await delete_api_key("ak_123", mock_user)

            assert response["message"] == "API Key deleted successfully"
            key_mgr_instance.delete_key.assert_called_once_with("ak_123")

    @pytest.mark.asyncio
    async def test_delete_api_key_non_admin(self):
        """测试非 admin 用户删除 API Key"""
        non_admin_user = User(id="user_123", username="user", role="user", status="active")

        with pytest.raises(AuthenticationError, match="Insufficient permissions"):
            await delete_api_key("ak_123", non_admin_user)

    @pytest.mark.asyncio
    async def test_delete_api_key_not_found(self, mock_user):
        """测试删除不存在的 API Key"""
        with patch("gaiarouter.api.controllers.api_keys.get_api_key_manager") as mock_key_mgr:
            key_mgr_instance = Mock()
            key_mgr_instance.get_key.return_value = None
            mock_key_mgr.return_value = key_mgr_instance

            with pytest.raises(HTTPException) as exc_info:
                await delete_api_key("ak_nonexistent", mock_user)

            assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_api_key_failure(self, mock_user):
        """测试删除失败"""
        existing_key = APIKey(id="ak_123", organization_id="org_123", name="Test Key")

        with patch("gaiarouter.api.controllers.api_keys.get_api_key_manager") as mock_key_mgr:
            key_mgr_instance = Mock()
            key_mgr_instance.get_key.return_value = existing_key
            key_mgr_instance.delete_key.return_value = False
            mock_key_mgr.return_value = key_mgr_instance

            with pytest.raises(HTTPException) as exc_info:
                await delete_api_key("ak_123", mock_user)

            assert exc_info.value.status_code == 500
