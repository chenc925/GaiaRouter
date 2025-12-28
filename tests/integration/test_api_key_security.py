"""
API Key 安全性集成测试

测试 API Key 的安全处理：
1. 列表接口不返回完整 key（返回 null）
2. 详情接口不返回完整 key（返回 null）
3. 创建接口返回完整 key（仅一次）
4. 一个组织一个 API Key 限制
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException

from gaiarouter.api.controllers.api_keys import (
    create_api_key,
    get_api_key,
    list_api_keys,
)
from gaiarouter.database.models import APIKey, Organization, User
from gaiarouter.utils.errors import InvalidRequestError


@pytest.fixture
def admin_user():
    """创建 admin 用户"""
    return User(id="admin_001", username="admin", role="admin", status="active")


@pytest.fixture
def test_organization():
    """创建测试组织"""
    return Organization(id="org_test_001", name="Test Security Org", status="active")


@pytest.fixture
def existing_api_key():
    """创建已存在的 API Key"""
    return APIKey(
        id="ak_existing_001",
        organization_id="org_test_001",
        name="Existing API Key",
        key="sk-or-v1-existing-key-full-value",
        permissions=["read", "write"],
        status="active",
        created_at=datetime(2024, 1, 1),
    )


class TestApiKeySecurityListEndpoint:
    """测试场景 1：查询 API Key 列表 - key 字段应为 null"""

    @pytest.mark.asyncio
    async def test_list_api_keys_returns_null_key(self, admin_user, existing_api_key):
        """验证列表接口返回 key: null"""
        with (
            patch("gaiarouter.api.controllers.api_keys.get_api_key_manager") as mock_key_mgr,
            patch("gaiarouter.organizations.manager.get_organization_manager") as mock_org_mgr,
        ):
            # 模拟返回已存在的 API Keys
            key_mgr_instance = Mock()
            key_mgr_instance.list_keys.return_value = ([existing_api_key], 1)
            mock_key_mgr.return_value = key_mgr_instance

            org_mgr_instance = Mock()
            org_mgr_instance.get_organization.return_value = Organization(
                id="org_test_001", name="Test Security Org"
            )
            mock_org_mgr.return_value = org_mgr_instance

            # 调用列表接口
            response = await list_api_keys(
                page=1, limit=20, status=None, search=None, organization_id=None, user=admin_user
            )

            # 验证返回结果
            assert len(response.data) == 1
            api_key_response = response.data[0]

            # 关键验证：key 字段应该为 None（后端不返回完整 key）
            assert api_key_response.key is None, "列表接口不应该返回完整的 API Key"
            assert api_key_response.id == "ak_existing_001"
            assert api_key_response.organization_id == "org_test_001"
            assert api_key_response.name == "Existing API Key"

    @pytest.mark.asyncio
    async def test_list_multiple_keys_all_null(self, admin_user):
        """验证多个 API Key 的 key 字段都为 null"""
        mock_keys = [
            APIKey(
                id=f"ak_{i}",
                organization_id=f"org_{i}",
                name=f"Key {i}",
                key=f"sk-or-v1-key-{i}-full-value",
                status="active",
                created_at=datetime.now(),
            )
            for i in range(3)
        ]

        with (
            patch("gaiarouter.api.controllers.api_keys.get_api_key_manager") as mock_key_mgr,
            patch("gaiarouter.organizations.manager.get_organization_manager") as mock_org_mgr,
        ):
            key_mgr_instance = Mock()
            key_mgr_instance.list_keys.return_value = (mock_keys, 3)
            mock_key_mgr.return_value = key_mgr_instance

            org_mgr_instance = Mock()
            org_mgr_instance.get_organization.side_effect = [
                Organization(id=f"org_{i}", name=f"Org {i}") for i in range(3)
            ]
            mock_org_mgr.return_value = org_mgr_instance

            response = await list_api_keys(
                page=1, limit=20, status=None, search=None, organization_id=None, user=admin_user
            )

            # 验证所有 key 字段都为 None
            assert len(response.data) == 3
            for api_key in response.data:
                assert api_key.key is None, f"API Key {api_key.id} 的 key 字段应该为 null"


class TestApiKeySecurityDetailEndpoint:
    """测试场景 2：查询 API Key 详情 - key 字段应为 null"""

    @pytest.mark.asyncio
    async def test_get_api_key_returns_null_key(self, admin_user, existing_api_key):
        """验证详情接口返回 key: null"""
        with patch("gaiarouter.api.controllers.api_keys.get_api_key_manager") as mock_key_mgr:
            key_mgr_instance = Mock()
            key_mgr_instance.get_key.return_value = existing_api_key
            mock_key_mgr.return_value = key_mgr_instance

            # 调用详情接口
            response = await get_api_key("ak_existing_001", admin_user)

            # 关键验证：key 字段应该为 None
            assert response.key is None, "详情接口不应该返回完整的 API Key"
            assert response.id == "ak_existing_001"
            assert response.organization_id == "org_test_001"
            assert response.name == "Existing API Key"

    @pytest.mark.asyncio
    async def test_get_api_key_other_fields_present(self, admin_user, existing_api_key):
        """验证除 key 外的其他字段正常返回"""
        with patch("gaiarouter.api.controllers.api_keys.get_api_key_manager") as mock_key_mgr:
            key_mgr_instance = Mock()
            key_mgr_instance.get_key.return_value = existing_api_key
            mock_key_mgr.return_value = key_mgr_instance

            response = await get_api_key("ak_existing_001", admin_user)

            # 验证其他字段正常
            assert response.key is None
            assert response.permissions == ["read", "write"]
            assert response.status == "active"
            assert response.created_at is not None


class TestApiKeySecurityCreateEndpoint:
    """测试场景 3：创建 API Key - 应返回完整 key（仅一次）"""

    @pytest.mark.asyncio
    async def test_create_api_key_returns_full_key(self, admin_user, test_organization):
        """验证创建接口返回完整的 API Key（唯一一次）"""
        create_request = Mock()
        create_request.organization_id = "org_test_001"

        with (
            patch("gaiarouter.organizations.manager.get_organization_manager") as mock_org_mgr,
            patch("gaiarouter.api.controllers.api_keys.get_api_key_manager") as mock_key_mgr,
        ):
            # Mock organization manager
            org_mgr_instance = Mock()
            org_mgr_instance.get_organization.return_value = test_organization
            mock_org_mgr.return_value = org_mgr_instance

            # Mock API key manager - 组织还没有 API Key
            key_mgr_instance = Mock()
            key_mgr_instance.list_keys.return_value = ([], 0)

            # 模拟创建成功，返回完整 key
            new_api_key = APIKey(
                id="ak_new_001",
                organization_id="org_test_001",
                name="Test Security Org API Key",
                description="Auto-generated API Key for Test Security Org",
                permissions=["read", "write"],
                status="active",
                created_at=datetime.now(),
            )
            full_key = "sk-or-v1-new-key-full-secret-value-12345"
            key_mgr_instance.create_key.return_value = (new_api_key, full_key)
            mock_key_mgr.return_value = key_mgr_instance

            # 调用创建接口
            response = await create_api_key(create_request, admin_user)

            # 关键验证：创建时应该返回完整的 key
            assert response.key == full_key, "创建接口应该返回完整的 API Key（仅此一次）"
            assert response.id == "ak_new_001"
            assert response.organization_id == "org_test_001"
            assert response.organization_name == "Test Security Org"
            assert "sk-or-v1-" in response.key, "返回的 key 应该是完整格式"

    @pytest.mark.asyncio
    async def test_create_api_key_full_key_format(self, admin_user, test_organization):
        """验证创建返回的 key 是完整格式"""
        create_request = Mock()
        create_request.organization_id = "org_test_001"

        with (
            patch("gaiarouter.organizations.manager.get_organization_manager") as mock_org_mgr,
            patch("gaiarouter.api.controllers.api_keys.get_api_key_manager") as mock_key_mgr,
        ):
            org_mgr_instance = Mock()
            org_mgr_instance.get_organization.return_value = test_organization
            mock_org_mgr.return_value = org_mgr_instance

            key_mgr_instance = Mock()
            key_mgr_instance.list_keys.return_value = ([], 0)

            new_key = APIKey(
                id="ak_new",
                organization_id="org_test_001",
                name="Test Key",
                status="active",
                created_at=datetime.now(),
            )
            full_key = "sk-or-v1-1234567890abcdef"
            key_mgr_instance.create_key.return_value = (new_key, full_key)
            mock_key_mgr.return_value = key_mgr_instance

            response = await create_api_key(create_request, admin_user)

            # 验证 key 格式
            assert response.key is not None
            assert len(response.key) > 20, "完整 key 应该有足够长度"
            assert response.key.startswith("sk-or-v1-"), "key 应该以 sk-or-v1- 开头"


class TestApiKeySecurityOneKeyPerOrg:
    """测试场景 4：一个组织一个 API Key 限制"""

    @pytest.mark.asyncio
    async def test_create_second_key_for_org_fails(self, admin_user, test_organization, existing_api_key):
        """验证为已有 API Key 的组织创建第二个 key 会失败"""
        create_request = Mock()
        create_request.organization_id = "org_test_001"

        with (
            patch("gaiarouter.organizations.manager.get_organization_manager") as mock_org_mgr,
            patch("gaiarouter.api.controllers.api_keys.get_api_key_manager") as mock_key_mgr,
        ):
            org_mgr_instance = Mock()
            org_mgr_instance.get_organization.return_value = test_organization
            mock_org_mgr.return_value = org_mgr_instance

            # Mock - 组织已经有一个 API Key
            key_mgr_instance = Mock()
            key_mgr_instance.list_keys.return_value = ([existing_api_key], 1)
            mock_key_mgr.return_value = key_mgr_instance

            # 尝试创建第二个 key 应该失败
            with pytest.raises(InvalidRequestError) as exc_info:
                await create_api_key(create_request, admin_user)

            # 验证错误信息
            assert "already has an API Key" in str(exc_info.value)
            assert "only have one" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_key_for_org_without_key_succeeds(self, admin_user, test_organization):
        """验证为没有 API Key 的组织创建 key 成功"""
        create_request = Mock()
        create_request.organization_id = "org_test_001"

        with (
            patch("gaiarouter.organizations.manager.get_organization_manager") as mock_org_mgr,
            patch("gaiarouter.api.controllers.api_keys.get_api_key_manager") as mock_key_mgr,
        ):
            org_mgr_instance = Mock()
            org_mgr_instance.get_organization.return_value = test_organization
            mock_org_mgr.return_value = org_mgr_instance

            # Mock - 组织没有 API Key
            key_mgr_instance = Mock()
            key_mgr_instance.list_keys.return_value = ([], 0)

            new_key = APIKey(
                id="ak_new",
                organization_id="org_test_001",
                name="New Key",
                status="active",
                created_at=datetime.now(),
            )
            key_mgr_instance.create_key.return_value = (new_key, "sk-or-v1-newkey")
            mock_key_mgr.return_value = key_mgr_instance

            # 应该成功创建
            response = await create_api_key(create_request, admin_user)

            assert response.id == "ak_new"
            assert response.key == "sk-or-v1-newkey"


class TestApiKeySecurityCompleteWorkflow:
    """测试完整的 API Key 安全工作流程"""

    @pytest.mark.asyncio
    async def test_complete_security_workflow(self, admin_user, test_organization):
        """
        测试完整流程：
        1. 创建 API Key（返回完整 key）
        2. 列表查询（返回 key: null）
        3. 详情查询（返回 key: null）
        4. 尝试再次创建（失败）
        """
        create_request = Mock()
        create_request.organization_id = "org_test_001"

        with (
            patch("gaiarouter.organizations.manager.get_organization_manager") as mock_org_mgr,
            patch("gaiarouter.api.controllers.api_keys.get_api_key_manager") as mock_key_mgr,
        ):
            org_mgr_instance = Mock()
            org_mgr_instance.get_organization.return_value = test_organization
            mock_org_mgr.return_value = org_mgr_instance

            key_mgr_instance = Mock()
            mock_key_mgr.return_value = key_mgr_instance

            # 步骤 1: 创建 API Key（第一次，组织没有 key）
            key_mgr_instance.list_keys.return_value = ([], 0)
            new_key = APIKey(
                id="ak_workflow_test",
                organization_id="org_test_001",
                name="Workflow Test Key",
                key="sk-or-v1-workflow-secret",
                status="active",
                created_at=datetime.now(),
            )
            full_secret_key = "sk-or-v1-workflow-secret"
            key_mgr_instance.create_key.return_value = (new_key, full_secret_key)

            create_response = await create_api_key(create_request, admin_user)

            # 验证创建时返回完整 key
            assert create_response.key == full_secret_key, "步骤1: 创建时应返回完整 key"

            # 步骤 2: 查询列表（模拟 key 已存在于数据库）
            key_mgr_instance.list_keys.return_value = ([new_key], 1)

            list_response = await list_api_keys(
                page=1, limit=20, status=None, search=None, organization_id=None, user=admin_user
            )

            # 验证列表查询返回 null
            assert list_response.data[0].key is None, "步骤2: 列表查询应返回 key: null"

            # 步骤 3: 查询详情
            key_mgr_instance.get_key.return_value = new_key

            detail_response = await get_api_key("ak_workflow_test", admin_user)

            # 验证详情查询返回 null
            assert detail_response.key is None, "步骤3: 详情查询应返回 key: null"

            # 步骤 4: 尝试再次创建（应该失败）
            key_mgr_instance.list_keys.return_value = ([new_key], 1)

            with pytest.raises(InvalidRequestError) as exc_info:
                await create_api_key(create_request, admin_user)

            assert "already has an API Key" in str(exc_info.value), "步骤4: 重复创建应该失败"


class TestApiKeySecurityEdgeCases:
    """测试边界情况"""

    @pytest.mark.asyncio
    async def test_key_field_never_leaked_in_updates(self, admin_user):
        """验证更新操作也不会泄露 key（如果实现了更新接口）"""
        # 这是一个提醒：如果将来实现了更新接口，也要确保不返回 key
        # 当前版本不支持更新，所以这个测试作为文档记录
        pass

    @pytest.mark.asyncio
    async def test_multiple_orgs_each_can_have_one_key(self, admin_user):
        """验证多个组织各自可以有一个 key"""
        with (
            patch("gaiarouter.organizations.manager.get_organization_manager") as mock_org_mgr,
            patch("gaiarouter.api.controllers.api_keys.get_api_key_manager") as mock_key_mgr,
        ):
            key_mgr_instance = Mock()
            mock_key_mgr.return_value = key_mgr_instance

            org_mgr_instance = Mock()
            mock_org_mgr.return_value = org_mgr_instance

            # 为组织 1 创建 key
            org1 = Organization(id="org_1", name="Org 1", status="active")
            org_mgr_instance.get_organization.return_value = org1
            key_mgr_instance.list_keys.return_value = ([], 0)
            key_mgr_instance.create_key.return_value = (
                APIKey(
                    id="ak_1",
                    organization_id="org_1",
                    name="Key 1",
                    status="active",
                    permissions=["read", "write"],
                    created_at=datetime.now(),
                ),
                "sk-key-1",
            )

            request1 = Mock()
            request1.organization_id = "org_1"
            response1 = await create_api_key(request1, admin_user)
            assert response1.key == "sk-key-1"

            # 为组织 2 创建 key
            org2 = Organization(id="org_2", name="Org 2", status="active")
            org_mgr_instance.get_organization.return_value = org2
            key_mgr_instance.list_keys.return_value = ([], 0)
            key_mgr_instance.create_key.return_value = (
                APIKey(
                    id="ak_2",
                    organization_id="org_2",
                    name="Key 2",
                    status="active",
                    permissions=["read", "write"],
                    created_at=datetime.now(),
                ),
                "sk-key-2",
            )

            request2 = Mock()
            request2.organization_id = "org_2"
            response2 = await create_api_key(request2, admin_user)
            assert response2.key == "sk-key-2"

            # 两个组织都成功创建了各自的 key
            assert response1.organization_id == "org_1"
            assert response2.organization_id == "org_2"
