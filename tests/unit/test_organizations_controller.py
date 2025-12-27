"""
测试 Organizations Controller

测试组织管理端点的各种场景
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException

from gaiarouter.api.controllers.organizations import (
    _organization_to_dict,
    create_organization,
    delete_organization,
    get_organization,
    get_organization_stats,
    list_organizations,
    update_organization,
)
from gaiarouter.database.models import Organization, User
from gaiarouter.utils.errors import AuthenticationError, InvalidRequestError


class TestOrganizationToDict:
    """测试组织转字典函数"""

    def test_convert_full_organization(self):
        """测试完整组织转换"""
        org = Organization(
            id="org_123",
            name="Test Org",
            description="Test Description",
            admin_user_id="user_123",
            status="active",
            monthly_requests_limit=10000,
            monthly_tokens_limit=1000000,
            monthly_cost_limit=100.50,
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 2),
        )

        result = _organization_to_dict(org)

        assert result["id"] == "org_123"
        assert result["name"] == "Test Org"
        assert result["description"] == "Test Description"
        assert result["admin_user_id"] == "user_123"
        assert result["status"] == "active"
        assert result["monthly_requests_limit"] == 10000
        assert result["monthly_tokens_limit"] == 1000000
        assert result["monthly_cost_limit"] == 100.50
        assert result["created_at"] == "2024-01-01T00:00:00Z"
        assert result["updated_at"] == "2024-01-02T00:00:00Z"

    def test_convert_minimal_organization(self):
        """测试最小组织转换"""
        org = Organization(
            id="org_123",
            name="Test Org",
            status="active",
        )

        result = _organization_to_dict(org)

        assert result["id"] == "org_123"
        assert result["name"] == "Test Org"
        assert result["description"] is None
        assert result["monthly_cost_limit"] is None


class TestCreateOrganization:
    """测试创建组织"""

    @pytest.fixture
    def mock_user(self):
        return User(id="user_123", username="admin", role="admin", status="active")

    @pytest.fixture
    def create_request(self):
        request = Mock()
        request.name = "New Org"
        request.description = "New Description"
        request.monthly_requests_limit = 10000
        request.monthly_tokens_limit = 1000000
        request.monthly_cost_limit = 100.0
        return request

    @pytest.mark.asyncio
    async def test_create_organization_success(self, mock_user, create_request):
        """测试成功创建组织"""
        new_org = Organization(
            id="org_new",
            name="New Org",
            description="New Description",
            status="active",
            monthly_requests_limit=10000,
            monthly_tokens_limit=1000000,
            monthly_cost_limit=100.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        with patch(
            "gaiarouter.api.controllers.organizations.get_organization_manager"
        ) as mock_org_mgr:
            org_mgr_instance = Mock()
            org_mgr_instance.create_organization.return_value = new_org
            mock_org_mgr.return_value = org_mgr_instance

            response = await create_organization(create_request, mock_user)

            assert response.id == "org_new"
            assert response.name == "New Org"
            assert response.monthly_requests_limit == 10000
            org_mgr_instance.create_organization.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_organization_non_admin(self, create_request):
        """测试非 admin 用户创建组织"""
        non_admin_user = User(id="user_123", username="user", role="user", status="active")

        with pytest.raises(AuthenticationError, match="Insufficient permissions"):
            await create_organization(create_request, non_admin_user)

    @pytest.mark.asyncio
    async def test_create_organization_error_handling(self, mock_user, create_request):
        """测试创建组织错误处理"""
        with patch(
            "gaiarouter.api.controllers.organizations.get_organization_manager"
        ) as mock_org_mgr:
            org_mgr_instance = Mock()
            org_mgr_instance.create_organization.side_effect = Exception("Database error")
            mock_org_mgr.return_value = org_mgr_instance

            with pytest.raises(HTTPException) as exc_info:
                await create_organization(create_request, mock_user)

            assert exc_info.value.status_code == 500


class TestListOrganizations:
    """测试列出组织"""

    @pytest.fixture
    def mock_user(self):
        return User(id="user_123", username="admin", role="admin", status="active")

    @pytest.mark.asyncio
    async def test_list_organizations_success(self, mock_user):
        """测试成功列出组织"""
        mock_orgs = [
            Organization(id="org_1", name="Org 1", status="active", created_at=datetime.now(), updated_at=datetime.now()),
            Organization(id="org_2", name="Org 2", status="active", created_at=datetime.now(), updated_at=datetime.now()),
        ]

        with patch(
            "gaiarouter.api.controllers.organizations.get_organization_manager"
        ) as mock_org_mgr:
            org_mgr_instance = Mock()
            org_mgr_instance.list_organizations.return_value = (mock_orgs, 2)
            mock_org_mgr.return_value = org_mgr_instance

            response = await list_organizations(
                page=1, limit=20, status=None, search=None, user=mock_user
            )

            assert len(response.data) == 2
            assert response.pagination["total"] == 2
            assert response.pagination["page"] == 1
            assert response.data[0].id == "org_1"

    @pytest.mark.asyncio
    async def test_list_organizations_with_filters(self, mock_user):
        """测试带筛选条件列出组织"""
        with patch(
            "gaiarouter.api.controllers.organizations.get_organization_manager"
        ) as mock_org_mgr:
            org_mgr_instance = Mock()
            org_mgr_instance.list_organizations.return_value = ([], 0)
            mock_org_mgr.return_value = org_mgr_instance

            await list_organizations(page=1, limit=10, status="active", search="test", user=mock_user)

            org_mgr_instance.list_organizations.assert_called_once_with(
                page=1, limit=10, status="active", search="test"
            )

    @pytest.mark.asyncio
    async def test_list_organizations_pagination(self, mock_user):
        """测试分页"""
        with patch(
            "gaiarouter.api.controllers.organizations.get_organization_manager"
        ) as mock_org_mgr:
            org_mgr_instance = Mock()
            org_mgr_instance.list_organizations.return_value = ([], 25)
            mock_org_mgr.return_value = org_mgr_instance

            response = await list_organizations(
                page=2, limit=10, status=None, search=None, user=mock_user
            )

            assert response.pagination["page"] == 2
            assert response.pagination["total"] == 25
            assert response.pagination["pages"] == 3


class TestGetOrganization:
    """测试获取单个组织"""

    @pytest.fixture
    def mock_user(self):
        return User(id="user_123", username="admin", role="admin", status="active")

    @pytest.mark.asyncio
    async def test_get_organization_success(self, mock_user):
        """测试成功获取组织"""
        mock_org = Organization(
            id="org_123", name="Test Org", status="active", created_at=datetime.now(), updated_at=datetime.now()
        )

        with patch(
            "gaiarouter.api.controllers.organizations.get_organization_manager"
        ) as mock_org_mgr:
            org_mgr_instance = Mock()
            org_mgr_instance.get_organization.return_value = mock_org
            mock_org_mgr.return_value = org_mgr_instance

            response = await get_organization("org_123", mock_user)

            assert response.id == "org_123"
            assert response.name == "Test Org"

    @pytest.mark.asyncio
    async def test_get_organization_not_found(self, mock_user):
        """测试组织不存在"""
        with patch(
            "gaiarouter.api.controllers.organizations.get_organization_manager"
        ) as mock_org_mgr:
            org_mgr_instance = Mock()
            org_mgr_instance.get_organization.return_value = None
            mock_org_mgr.return_value = org_mgr_instance

            with pytest.raises(HTTPException) as exc_info:
                await get_organization("org_nonexistent", mock_user)

            assert exc_info.value.status_code == 404
            assert "not found" in str(exc_info.value.detail)


class TestUpdateOrganization:
    """测试更新组织"""

    @pytest.fixture
    def mock_user(self):
        return User(id="user_123", username="admin", role="admin", status="active")

    @pytest.fixture
    def update_request(self):
        request = Mock()
        request.name = "Updated Org"
        request.description = "Updated Description"
        request.admin_user_id = None
        request.status = "inactive"
        request.monthly_requests_limit = 20000
        request.monthly_tokens_limit = 2000000
        request.monthly_cost_limit = 200.0
        return request

    @pytest.mark.asyncio
    async def test_update_organization_success(self, mock_user, update_request):
        """测试成功更新组织"""
        existing_org = Organization(id="org_123", name="Old Org", status="active")
        updated_org = Organization(
            id="org_123",
            name="Updated Org",
            description="Updated Description",
            status="inactive",
            monthly_requests_limit=20000,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        with patch(
            "gaiarouter.api.controllers.organizations.get_organization_manager"
        ) as mock_org_mgr:
            org_mgr_instance = Mock()
            org_mgr_instance.get_organization.return_value = existing_org
            org_mgr_instance.update_organization.return_value = updated_org
            mock_org_mgr.return_value = org_mgr_instance

            response = await update_organization("org_123", update_request, mock_user)

            assert response.id == "org_123"
            assert response.name == "Updated Org"
            org_mgr_instance.update_organization.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_organization_non_admin(self, update_request):
        """测试非 admin 用户更新组织"""
        non_admin_user = User(id="user_123", username="user", role="user", status="active")

        with pytest.raises(AuthenticationError, match="Insufficient permissions"):
            await update_organization("org_123", update_request, non_admin_user)

    @pytest.mark.asyncio
    async def test_update_organization_not_found(self, mock_user, update_request):
        """测试更新不存在的组织"""
        with patch(
            "gaiarouter.api.controllers.organizations.get_organization_manager"
        ) as mock_org_mgr:
            org_mgr_instance = Mock()
            org_mgr_instance.get_organization.return_value = None
            mock_org_mgr.return_value = org_mgr_instance

            with pytest.raises(HTTPException) as exc_info:
                await update_organization("org_nonexistent", update_request, mock_user)

            assert exc_info.value.status_code == 404


class TestDeleteOrganization:
    """测试删除组织"""

    @pytest.fixture
    def mock_user(self):
        return User(id="user_123", username="admin", role="admin", status="active")

    @pytest.mark.asyncio
    async def test_delete_organization_success(self, mock_user):
        """测试成功删除组织"""
        existing_org = Organization(id="org_123", name="Test Org", status="active")

        with patch(
            "gaiarouter.api.controllers.organizations.get_organization_manager"
        ) as mock_org_mgr:
            org_mgr_instance = Mock()
            org_mgr_instance.get_organization.return_value = existing_org
            org_mgr_instance.delete_organization.return_value = True
            mock_org_mgr.return_value = org_mgr_instance

            response = await delete_organization("org_123", mock_user)

            assert response["message"] == "Organization deleted successfully"
            org_mgr_instance.delete_organization.assert_called_once_with("org_123")

    @pytest.mark.asyncio
    async def test_delete_organization_non_admin(self):
        """测试非 admin 用户删除组织"""
        non_admin_user = User(id="user_123", username="user", role="user", status="active")

        with pytest.raises(AuthenticationError, match="Insufficient permissions"):
            await delete_organization("org_123", non_admin_user)

    @pytest.mark.asyncio
    async def test_delete_organization_not_found(self, mock_user):
        """测试删除不存在的组织"""
        with patch(
            "gaiarouter.api.controllers.organizations.get_organization_manager"
        ) as mock_org_mgr:
            org_mgr_instance = Mock()
            org_mgr_instance.get_organization.return_value = None
            mock_org_mgr.return_value = org_mgr_instance

            with pytest.raises(HTTPException) as exc_info:
                await delete_organization("org_nonexistent", mock_user)

            assert exc_info.value.status_code == 404


class TestGetOrganizationStats:
    """测试获取组织统计"""

    @pytest.fixture
    def mock_user(self):
        return User(id="user_123", username="admin", role="admin", status="active")

    @pytest.mark.asyncio
    async def test_get_organization_stats_success(self, mock_user):
        """测试成功获取组织统计"""
        with (
            patch("gaiarouter.auth.key_storage.get_key_storage") as mock_key_storage,
            patch("gaiarouter.stats.storage.get_stats_storage") as mock_stats_storage,
        ):
            # Mock key storage
            key_storage_instance = Mock()
            mock_key = Mock()
            mock_key.id = "ak_123"
            key_storage_instance.list.return_value = ([mock_key], 1)
            mock_key_storage.return_value = key_storage_instance

            # Mock stats storage
            stats_storage_instance = Mock()
            stats_storage_instance.get_key_stats.return_value = []
            stats_storage_instance.get_summary.return_value = {
                "total_requests": 100,
                "total_tokens": 10000,
                "total_cost": 5.0,
            }
            stats_storage_instance.aggregate_by_date.return_value = {}
            mock_stats_storage.return_value = stats_storage_instance

            response = await get_organization_stats(
                org_id="org_123",
                start_date="2024-01-01T00:00:00Z",
                end_date="2024-01-31T23:59:59Z",
                group_by="day",
                user=mock_user,
            )

            assert response["organization_id"] == "org_123"
            assert "summary" in response
            assert "period" in response

    @pytest.mark.asyncio
    async def test_get_organization_stats_invalid_date(self, mock_user):
        """测试无效日期格式"""
        with pytest.raises(InvalidRequestError, match="Invalid start_date format"):
            await get_organization_stats(
                org_id="org_123",
                start_date="invalid-date",
                end_date=None,
                group_by="day",
                user=mock_user,
            )

    @pytest.mark.asyncio
    async def test_get_organization_stats_invalid_group_by(self, mock_user):
        """测试无效分组方式"""
        with pytest.raises(InvalidRequestError, match="Invalid group_by"):
            await get_organization_stats(
                org_id="org_123",
                start_date=None,
                end_date=None,
                group_by="invalid",
                user=mock_user,
            )

    @pytest.mark.asyncio
    async def test_get_organization_stats_by_model(self, mock_user):
        """测试按模型分组"""
        with (
            patch("gaiarouter.auth.key_storage.get_key_storage") as mock_key_storage,
            patch("gaiarouter.stats.storage.get_stats_storage") as mock_stats_storage,
        ):
            key_storage_instance = Mock()
            key_storage_instance.list.return_value = ([], 0)
            mock_key_storage.return_value = key_storage_instance

            stats_storage_instance = Mock()
            stats_storage_instance.get_summary.return_value = {}
            stats_storage_instance.aggregate_by_model.return_value = {}
            mock_stats_storage.return_value = stats_storage_instance

            response = await get_organization_stats(
                org_id="org_123",
                start_date=None,
                end_date=None,
                group_by="model",
                user=mock_user,
            )

            assert "by_model" in response
            stats_storage_instance.aggregate_by_model.assert_called_once()
