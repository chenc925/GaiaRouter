"""
测试 API Key 管理器

测试 API Key 的完整生命周期管理
"""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from gaiarouter.auth.api_key_manager import APIKeyManager, get_api_key_manager
from gaiarouter.auth.permission import Permission
from gaiarouter.database.models import APIKey
from gaiarouter.utils.errors import AuthenticationError, InvalidRequestError


class TestAPIKeyManager:
    """测试 API Key 管理器"""

    @pytest.fixture
    def api_key_manager(self):
        """创建 API Key 管理器实例"""
        with patch("gaiarouter.auth.api_key_manager.get_key_storage"):
            return APIKeyManager()

    @pytest.fixture
    def mock_storage(self, api_key_manager):
        """Mock storage"""
        return api_key_manager.storage

    def test_initialization(self, api_key_manager):
        """测试初始化"""
        assert api_key_manager.storage is not None
        assert api_key_manager.logger is not None

    def test_generate_key_id(self, api_key_manager):
        """测试生成 API Key ID"""
        key_id = api_key_manager._generate_key_id()

        # 验证格式
        assert key_id.startswith("ak_")
        assert len(key_id) > 3

        # 生成多个 ID 应该都不同
        key_ids = [api_key_manager._generate_key_id() for _ in range(10)]
        assert len(set(key_ids)) == 10  # 所有 ID 都应该唯一

    def test_generate_api_key(self, api_key_manager):
        """测试生成 API Key 值"""
        api_key = api_key_manager._generate_api_key()

        # 验证格式
        assert api_key.startswith("sk-or-v1-")
        assert len(api_key) > 9

        # 生成多个 key 应该都不同
        api_keys = [api_key_manager._generate_api_key() for _ in range(10)]
        assert len(set(api_keys)) == 10  # 所有 key 都应该唯一

    def test_hash_key(self, api_key_manager):
        """测试哈希 API Key"""
        api_key = "sk-or-v1-test123"
        hashed = api_key_manager._hash_key(api_key)

        # 验证哈希值
        assert len(hashed) == 64  # SHA256 输出 64 个十六进制字符
        assert hashed.isalnum()

        # 相同输入应该产生相同哈希
        assert api_key_manager._hash_key(api_key) == hashed

        # 不同输入应该产生不同哈希
        assert api_key_manager._hash_key("different-key") != hashed

    def test_create_key_success(self, api_key_manager, mock_storage):
        """测试成功创建 API Key"""
        mock_storage.save.return_value = True

        api_key, key_value = api_key_manager.create_key(
            organization_id="org_123", name="Test Key", description="Test Description"
        )

        # 验证返回值
        assert isinstance(api_key, APIKey)
        assert isinstance(key_value, str)
        assert key_value.startswith("sk-or-v1-")

        # 验证 API Key 对象属性
        assert api_key.id.startswith("ak_")
        assert api_key.organization_id == "org_123"
        assert api_key.name == "Test Key"
        assert api_key.description == "Test Description"
        assert api_key.status == "active"
        assert api_key.permissions == [Permission.READ, Permission.WRITE]

        # 验证 storage 被调用
        mock_storage.save.assert_called_once()

    def test_create_key_with_custom_permissions(self, api_key_manager, mock_storage):
        """测试创建带自定义权限的 API Key"""
        mock_storage.save.return_value = True

        custom_permissions = [Permission.READ]
        api_key, key_value = api_key_manager.create_key(
            organization_id="org_123", name="Read Only Key", permissions=custom_permissions
        )

        assert api_key.permissions == [Permission.READ]

    def test_create_key_with_expiration(self, api_key_manager, mock_storage):
        """测试创建带过期时间的 API Key"""
        mock_storage.save.return_value = True

        expires_at = datetime.utcnow() + timedelta(days=30)
        api_key, key_value = api_key_manager.create_key(
            organization_id="org_123", name="Expiring Key", expires_at=expires_at
        )

        assert api_key.expires_at == expires_at

    def test_create_key_failure(self, api_key_manager, mock_storage):
        """测试创建 API Key 失败"""
        mock_storage.save.return_value = False

        with pytest.raises(InvalidRequestError, match="Failed to create API Key"):
            api_key_manager.create_key(organization_id="org_123", name="Test Key")

    def test_create_key_exception(self, api_key_manager, mock_storage):
        """测试创建 API Key 异常处理"""
        mock_storage.save.side_effect = Exception("Database error")

        with pytest.raises(Exception, match="Database error"):
            api_key_manager.create_key(organization_id="org_123", name="Test Key")

    def test_get_key(self, api_key_manager, mock_storage):
        """测试获取 API Key"""
        mock_key = APIKey(
            id="ak_123",
            organization_id="org_123",
            name="Test Key",
            key="test-key",
            status="active",
            created_at=datetime.now(),
        )
        mock_storage.get.return_value = mock_key

        result = api_key_manager.get_key("ak_123")

        assert result == mock_key
        mock_storage.get.assert_called_once_with("ak_123")

    def test_get_key_not_found(self, api_key_manager, mock_storage):
        """测试获取不存在的 API Key"""
        mock_storage.get.return_value = None

        result = api_key_manager.get_key("ak_nonexistent")

        assert result is None

    def test_list_keys_no_filters(self, api_key_manager, mock_storage):
        """测试列出 API Keys（无筛选）"""
        mock_keys = [
            APIKey(id="ak_1", organization_id="org_123", name="Key 1", key="key1", status="active"),
            APIKey(id="ak_2", organization_id="org_123", name="Key 2", key="key2", status="active"),
        ]
        mock_storage.list.return_value = (mock_keys, 2)

        keys, total = api_key_manager.list_keys()

        assert len(keys) == 2
        assert total == 2
        mock_storage.list.assert_called_once_with(filters={}, page=1, limit=20)

    def test_list_keys_with_organization_filter(self, api_key_manager, mock_storage):
        """测试列出指定组织的 API Keys"""
        mock_storage.list.return_value = ([], 0)

        api_key_manager.list_keys(organization_id="org_123")

        mock_storage.list.assert_called_once_with(
            filters={"organization_id": "org_123"}, page=1, limit=20
        )

    def test_list_keys_with_status_filter(self, api_key_manager, mock_storage):
        """测试列出指定状态的 API Keys"""
        mock_storage.list.return_value = ([], 0)

        api_key_manager.list_keys(status="active")

        mock_storage.list.assert_called_once_with(filters={"status": "active"}, page=1, limit=20)

    def test_list_keys_with_search(self, api_key_manager, mock_storage):
        """测试搜索 API Keys"""
        mock_storage.list.return_value = ([], 0)

        api_key_manager.list_keys(search="test")

        mock_storage.list.assert_called_once_with(filters={"search": "test"}, page=1, limit=20)

    def test_list_keys_with_pagination(self, api_key_manager, mock_storage):
        """测试分页列出 API Keys"""
        mock_storage.list.return_value = ([], 0)

        api_key_manager.list_keys(page=2, limit=50)

        mock_storage.list.assert_called_once_with(filters={}, page=2, limit=50)

    def test_update_key_success(self, api_key_manager, mock_storage):
        """测试成功更新 API Key"""
        updated_key = APIKey(
            id="ak_123",
            organization_id="org_123",
            name="Updated Key",
            key="test-key",
            status="active",
            created_at=datetime.now(),
        )
        mock_storage.update.return_value = True
        mock_storage.get.return_value = updated_key

        result = api_key_manager.update_key("ak_123", name="Updated Key")

        assert result == updated_key
        mock_storage.update.assert_called_once()
        # 验证 updated_at 被设置
        update_call = mock_storage.update.call_args[0]
        assert "updated_at" in update_call[1]

    def test_update_key_multiple_fields(self, api_key_manager, mock_storage):
        """测试更新多个字段"""
        mock_storage.update.return_value = True
        mock_storage.get.return_value = Mock()

        api_key_manager.update_key(
            "ak_123",
            name="New Name",
            description="New Description",
            permissions=[Permission.READ],
            status="inactive",
        )

        # 验证所有字段都被传递
        update_call = mock_storage.update.call_args[0]
        updates = update_call[1]
        assert updates["name"] == "New Name"
        assert updates["description"] == "New Description"
        assert updates["permissions"] == [Permission.READ]
        assert updates["status"] == "inactive"

    def test_update_key_no_changes(self, api_key_manager, mock_storage):
        """测试不更新任何字段"""
        result = api_key_manager.update_key("ak_123")

        assert result is None
        mock_storage.update.assert_not_called()

    def test_update_key_not_found(self, api_key_manager, mock_storage):
        """测试更新不存在的 API Key"""
        mock_storage.update.return_value = False

        result = api_key_manager.update_key("ak_nonexistent", name="New Name")

        assert result is None

    def test_update_key_exception(self, api_key_manager, mock_storage):
        """测试更新 API Key 异常处理"""
        mock_storage.update.side_effect = Exception("Database error")

        with pytest.raises(Exception, match="Database error"):
            api_key_manager.update_key("ak_123", name="New Name")

    def test_delete_key_success(self, api_key_manager, mock_storage):
        """测试成功删除 API Key"""
        mock_storage.delete.return_value = True

        result = api_key_manager.delete_key("ak_123")

        assert result is True
        mock_storage.delete.assert_called_once_with("ak_123")

    def test_delete_key_not_found(self, api_key_manager, mock_storage):
        """测试删除不存在的 API Key"""
        mock_storage.delete.return_value = False

        result = api_key_manager.delete_key("ak_nonexistent")

        assert result is False

    def test_verify_key_success(self, api_key_manager, mock_storage):
        """测试成功验证 API Key"""
        mock_key = APIKey(
            id="ak_123",
            organization_id="org_123",
            name="Test Key",
            key="sk-or-v1-test123",
            status="active",
            expires_at=None,
            created_at=datetime.now(),
        )
        mock_storage.get_by_key.return_value = mock_key
        mock_storage.update_last_used.return_value = True

        result = api_key_manager.verify_key("sk-or-v1-test123")

        assert result == mock_key
        mock_storage.get_by_key.assert_called_once_with("sk-or-v1-test123")
        mock_storage.update_last_used.assert_called_once_with("ak_123")

    def test_verify_key_not_found(self, api_key_manager, mock_storage):
        """测试验证不存在的 API Key"""
        mock_storage.get_by_key.return_value = None

        with pytest.raises(AuthenticationError, match="Invalid API Key"):
            api_key_manager.verify_key("sk-or-v1-invalid")

    def test_verify_key_inactive(self, api_key_manager, mock_storage):
        """测试验证非活跃的 API Key"""
        mock_key = APIKey(
            id="ak_123",
            organization_id="org_123",
            name="Test Key",
            key="sk-or-v1-test123",
            status="inactive",
            created_at=datetime.now(),
        )
        mock_storage.get_by_key.return_value = mock_key

        with pytest.raises(AuthenticationError, match="API Key is inactive"):
            api_key_manager.verify_key("sk-or-v1-test123")

    def test_verify_key_expired(self, api_key_manager, mock_storage):
        """测试验证已过期的 API Key"""
        mock_key = APIKey(
            id="ak_123",
            organization_id="org_123",
            name="Test Key",
            key="sk-or-v1-test123",
            status="active",
            expires_at=datetime.utcnow() - timedelta(days=1),  # 已过期
            created_at=datetime.now(),
        )
        mock_storage.get_by_key.return_value = mock_key
        mock_storage.update.return_value = True

        with pytest.raises(AuthenticationError, match="API Key has expired"):
            api_key_manager.verify_key("sk-or-v1-test123")

        # 验证状态被更新为 expired
        assert mock_storage.update.called

    def test_verify_key_exception(self, api_key_manager, mock_storage):
        """测试验证 API Key 异常处理"""
        mock_storage.get_by_key.side_effect = Exception("Database error")

        with pytest.raises(AuthenticationError, match="Failed to verify API Key"):
            api_key_manager.verify_key("sk-or-v1-test123")


class TestGetAPIKeyManager:
    """测试获取 API Key 管理器单例"""

    def test_get_api_key_manager_returns_instance(self):
        """测试返回实例"""
        with patch("gaiarouter.auth.api_key_manager.get_key_storage"):
            manager = get_api_key_manager()
            assert isinstance(manager, APIKeyManager)

    def test_get_api_key_manager_singleton(self):
        """测试单例模式"""
        # 重置全局变量
        import gaiarouter.auth.api_key_manager as api_key_module

        api_key_module._api_key_manager = None

        with patch("gaiarouter.auth.api_key_manager.get_key_storage"):
            manager1 = get_api_key_manager()
            manager2 = get_api_key_manager()

            # 应该返回同一个实例
            assert manager1 is manager2


class TestAPIKeyManagerEdgeCases:
    """测试 API Key 管理器边缘情况"""

    @pytest.fixture
    def api_key_manager(self):
        with patch("gaiarouter.auth.api_key_manager.get_key_storage"):
            return APIKeyManager()

    @pytest.fixture
    def mock_storage(self, api_key_manager):
        return api_key_manager.storage

    def test_create_key_with_empty_name(self, api_key_manager, mock_storage):
        """测试创建空名称的 API Key"""
        mock_storage.save.return_value = True

        api_key, key_value = api_key_manager.create_key(organization_id="org_123", name="")

        # 应该允许空名称
        assert api_key.name == ""

    def test_verify_key_near_expiration(self, api_key_manager, mock_storage):
        """测试验证即将过期的 API Key"""
        # 5分钟后过期
        near_expiration = datetime.utcnow() + timedelta(minutes=5)
        mock_key = APIKey(
            id="ak_123",
            organization_id="org_123",
            name="Test Key",
            key="sk-or-v1-test123",
            status="active",
            expires_at=near_expiration,
            created_at=datetime.now(),
        )
        mock_storage.get_by_key.return_value = mock_key
        mock_storage.update_last_used.return_value = True

        # 应该验证成功（还未过期）
        result = api_key_manager.verify_key("sk-or-v1-test123")
        assert result == mock_key

    def test_update_key_status_change(self, api_key_manager, mock_storage):
        """测试更新 API Key 状态"""
        mock_storage.update.return_value = True
        updated_key = APIKey(
            id="ak_123",
            organization_id="org_123",
            name="Test Key",
            key="test-key",
            status="inactive",
            created_at=datetime.now(),
        )
        mock_storage.get.return_value = updated_key

        result = api_key_manager.update_key("ak_123", status="inactive")

        # 验证更新被调用并返回更新后的 key
        assert mock_storage.update.called
        update_call = mock_storage.update.call_args[0]
        updates = update_call[1]
        assert updates["status"] == "inactive"
        assert result == updated_key
