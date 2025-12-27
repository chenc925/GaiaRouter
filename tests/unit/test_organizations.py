"""
测试 Organizations 模块

测试组织管理器的创建、查询、更新、删除等功能
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from gaiarouter.database.models import Organization
from gaiarouter.organizations.manager import OrganizationManager
from gaiarouter.utils.errors import InvalidRequestError


class TestOrganizationManager:
    """测试组织管理器"""

    @pytest.fixture
    def manager(self):
        """创建组织管理器实例"""
        return OrganizationManager()

    def test_generate_org_id(self, manager):
        """测试生成组织 ID"""
        org_id = manager._generate_org_id()

        assert org_id.startswith("org_")
        assert len(org_id) > 10

        # 每次生成的应该不同
        org_id2 = manager._generate_org_id()
        assert org_id != org_id2

    def test_create_organization_basic(self, manager):
        """测试创建基础组织"""
        with patch.object(manager.storage, "save") as mock_save:
            mock_save.return_value = True

            org = manager.create_organization(
                name="Test Org",
                description="Test Description",
            )

        assert org.id.startswith("org_")
        assert org.name == "Test Org"
        assert org.description == "Test Description"
        assert org.status == "active"
        assert isinstance(org.created_at, datetime)

    def test_create_organization_with_limits(self, manager):
        """测试创建带限制的组织"""
        with patch.object(manager.storage, "save") as mock_save:
            mock_save.return_value = True

            org = manager.create_organization(
                name="Test Org",
                monthly_requests_limit=10000,
                monthly_tokens_limit=1000000,
                monthly_cost_limit=100.0,
            )

        assert org.monthly_requests_limit == 10000
        assert org.monthly_tokens_limit == 1000000
        assert org.monthly_cost_limit == 100.0

    def test_create_organization_with_admin(self, manager):
        """测试创建带管理员的组织"""
        with patch.object(manager.storage, "save") as mock_save:
            mock_save.return_value = True

            org = manager.create_organization(
                name="Test Org",
                admin_user_id="user_123",
            )

        assert org.admin_user_id == "user_123"

    def test_create_organization_storage_failure(self, manager):
        """测试创建组织时存储失败"""
        with patch.object(manager.storage, "save") as mock_save:
            mock_save.return_value = False

            with pytest.raises(InvalidRequestError, match="Failed to create organization"):
                manager.create_organization(name="Test Org")

    def test_get_organization(self, manager, sample_organization):
        """测试获取组织"""
        with patch.object(manager.storage, "get") as mock_get:
            mock_get.return_value = sample_organization

            org = manager.get_organization(sample_organization.id)

        assert org is not None
        assert org.id == sample_organization.id
        assert org.name == sample_organization.name

    def test_get_organization_not_found(self, manager):
        """测试获取不存在的组织"""
        with patch.object(manager.storage, "get") as mock_get:
            mock_get.return_value = None

            org = manager.get_organization("nonexistent_id")

        assert org is None

    def test_list_organizations_basic(self, manager):
        """测试查询组织列表"""
        mock_orgs = [
            Organization(id="org_1", name="Org 1", status="active"),
            Organization(id="org_2", name="Org 2", status="active"),
        ]

        with patch.object(manager.storage, "list") as mock_list:
            mock_list.return_value = (mock_orgs, 2)

            orgs, total = manager.list_organizations(page=1, limit=20)

        assert len(orgs) == 2
        assert total == 2
        assert orgs[0].id == "org_1"

    def test_list_organizations_with_filters(self, manager):
        """测试带筛选条件的组织查询"""
        mock_orgs = [Organization(id="org_1", name="Active Org", status="active")]

        with patch.object(manager.storage, "list") as mock_list:
            mock_list.return_value = (mock_orgs, 1)

            orgs, total = manager.list_organizations(
                page=1, limit=20, status="active", search="Active"
            )

        assert len(orgs) == 1
        assert total == 1
        mock_list.assert_called_once_with(
            filters={"status": "active", "search": "Active"}, page=1, limit=20
        )

    def test_list_organizations_pagination(self, manager):
        """测试分页查询"""
        mock_orgs = [
            Organization(id=f"org_{i}", name=f"Org {i}", status="active") for i in range(10)
        ]

        with patch.object(manager.storage, "list") as mock_list:
            mock_list.return_value = (mock_orgs[:10], 25)

            orgs, total = manager.list_organizations(page=1, limit=10)

        assert len(orgs) == 10
        assert total == 25

    def test_update_organization_name(self, manager, sample_organization):
        """测试更新组织名称"""
        with (
            patch.object(manager.storage, "update") as mock_update,
            patch.object(manager.storage, "get") as mock_get,
        ):
            mock_update.return_value = True
            updated_org = Organization(
                id=sample_organization.id,
                name="New Name",
                status=sample_organization.status,
            )
            mock_get.return_value = updated_org

            org = manager.update_organization(sample_organization.id, name="New Name")

        assert org is not None
        assert org.name == "New Name"
        mock_update.assert_called_once()

    def test_update_organization_limits(self, manager, sample_organization):
        """测试更新组织限制"""
        with (
            patch.object(manager.storage, "update") as mock_update,
            patch.object(manager.storage, "get") as mock_get,
        ):
            mock_update.return_value = True
            updated_org = Organization(
                id=sample_organization.id,
                name=sample_organization.name,
                monthly_requests_limit=20000,
                monthly_tokens_limit=2000000,
            )
            mock_get.return_value = updated_org

            org = manager.update_organization(
                sample_organization.id,
                monthly_requests_limit=20000,
                monthly_tokens_limit=2000000,
            )

        assert org is not None
        assert org.monthly_requests_limit == 20000
        assert org.monthly_tokens_limit == 2000000

    def test_update_organization_status(self, manager, sample_organization):
        """测试更新组织状态"""
        with (
            patch.object(manager.storage, "update") as mock_update,
            patch.object(manager.storage, "get") as mock_get,
        ):
            mock_update.return_value = True
            updated_org = Organization(
                id=sample_organization.id,
                name=sample_organization.name,
                status="inactive",
            )
            mock_get.return_value = updated_org

            org = manager.update_organization(sample_organization.id, status="inactive")

        assert org is not None
        assert org.status == "inactive"

    def test_update_organization_no_changes(self, manager, sample_organization):
        """测试更新组织但没有变化"""
        with patch.object(manager.storage, "update") as mock_update:
            org = manager.update_organization(sample_organization.id)

        assert org is None
        mock_update.assert_not_called()

    def test_update_organization_not_found(self, manager):
        """测试更新不存在的组织"""
        with (
            patch.object(manager.storage, "update") as mock_update,
            patch.object(manager.storage, "get") as mock_get,
        ):
            mock_update.return_value = False
            mock_get.return_value = None

            org = manager.update_organization("nonexistent_id", name="New Name")

        assert org is None

    def test_delete_organization(self, manager, sample_organization):
        """测试删除组织"""
        with patch.object(manager.storage, "delete") as mock_delete:
            mock_delete.return_value = True

            result = manager.delete_organization(sample_organization.id)

        assert result is True
        mock_delete.assert_called_once_with(sample_organization.id)

    def test_delete_organization_not_found(self, manager):
        """测试删除不存在的组织"""
        with patch.object(manager.storage, "delete") as mock_delete:
            mock_delete.return_value = False

            result = manager.delete_organization("nonexistent_id")

        assert result is False


class TestOrganizationLifecycle:
    """测试组织完整生命周期"""

    @pytest.fixture
    def manager(self):
        return OrganizationManager()

    def test_create_update_delete_flow(self, manager):
        """测试创建、更新、删除流程"""
        # 创建
        with patch.object(manager.storage, "save") as mock_save:
            mock_save.return_value = True
            org = manager.create_organization(name="Test Org", description="Initial")

        org_id = org.id
        assert org.name == "Test Org"

        # 更新
        with (
            patch.object(manager.storage, "update") as mock_update,
            patch.object(manager.storage, "get") as mock_get,
        ):
            mock_update.return_value = True
            updated_org = Organization(
                id=org_id, name="Updated Org", description="Updated", status="active"
            )
            mock_get.return_value = updated_org

            org = manager.update_organization(org_id, name="Updated Org", description="Updated")

        assert org.name == "Updated Org"

        # 删除
        with patch.object(manager.storage, "delete") as mock_delete:
            mock_delete.return_value = True
            result = manager.delete_organization(org_id)

        assert result is True

    def test_list_with_different_statuses(self, manager):
        """测试列出不同状态的组织"""
        active_orgs = [Organization(id=f"org_{i}", name=f"Active {i}", status="active") for i in range(3)]
        inactive_orgs = [Organization(id=f"org_{i+3}", name=f"Inactive {i}", status="inactive") for i in range(2)]

        # 查询活跃组织
        with patch.object(manager.storage, "list") as mock_list:
            mock_list.return_value = (active_orgs, 3)
            orgs, total = manager.list_organizations(status="active")

        assert len(orgs) == 3
        assert all(org.status == "active" for org in orgs)

        # 查询非活跃组织
        with patch.object(manager.storage, "list") as mock_list:
            mock_list.return_value = (inactive_orgs, 2)
            orgs, total = manager.list_organizations(status="inactive")

        assert len(orgs) == 2
        assert all(org.status == "inactive" for org in orgs)
