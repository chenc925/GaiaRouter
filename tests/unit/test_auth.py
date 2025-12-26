"""
测试 Auth 模块

测试 API Key 管理、验证、权限检查等
"""

import hashlib
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from gaiarouter.auth.api_key_manager import APIKeyManager
from gaiarouter.auth.permission import Permission
from gaiarouter.database.models import APIKey
from gaiarouter.utils.errors import AuthenticationError, InvalidRequestError


class TestAPIKeyManager:
    """测试 API Key 管理器"""

    @pytest.fixture
    def manager(self):
        """创建 API Key 管理器实例"""
        return APIKeyManager()

    def test_generate_key_id(self, manager):
        """测试生成 API Key ID"""
        key_id = manager._generate_key_id()

        assert key_id.startswith("ak_")
        assert len(key_id) > 10

        # 每次生成的应该不同
        key_id2 = manager._generate_key_id()
        assert key_id != key_id2

    def test_generate_api_key(self, manager):
        """测试生成 API Key 值"""
        api_key = manager._generate_api_key()

        assert api_key.startswith("sk-or-v1-")
        assert len(api_key) > 20

        # 每次生成的应该不同
        api_key2 = manager._generate_api_key()
        assert api_key != api_key2

    def test_hash_key(self, manager):
        """测试 API Key 哈希"""
        api_key = "sk-or-v1-test-key"
        hashed = manager._hash_key(api_key)

        # 应该是 SHA256 哈希
        assert len(hashed) == 64
        assert hashed == hashlib.sha256(api_key.encode()).hexdigest()

        # 相同输入产生相同哈希
        hashed2 = manager._hash_key(api_key)
        assert hashed == hashed2

    def test_create_key_basic(self, manager, sample_organization):
        """测试创建基础 API Key"""
        with patch.object(manager.storage, "save") as mock_save:
            mock_save.return_value = True

            api_key, key_value = manager.create_key(
                organization_id=sample_organization.id,
                name="Test Key",
                description="Test description",
            )

        assert api_key.id.startswith("ak_")
        assert api_key.name == "Test Key"
        assert api_key.description == "Test description"
        assert api_key.organization_id == sample_organization.id
        assert key_value.startswith("sk-or-v1-")

    def test_verify_key_success(self, manager, sample_api_key):
        """测试验证有效的 API Key"""
        with (
            patch.object(manager.storage, "get_by_key") as mock_get,
            patch.object(manager.storage, "update_last_used") as mock_update,
        ):
            mock_get.return_value = sample_api_key
            mock_update.return_value = True

            result = manager.verify_key(sample_api_key.key)

        assert result == sample_api_key

    def test_verify_key_not_found(self, manager):
        """测试验证不存在的 API Key"""
        with patch.object(manager.storage, "get_by_key") as mock_get:
            mock_get.return_value = None

            with pytest.raises(AuthenticationError, match="Invalid API Key"):
                manager.verify_key("invalid-key")

    def test_verify_key_inactive(self, manager, sample_api_key):
        """测试验证已禁用的 API Key"""
        sample_api_key.status = "inactive"

        with patch.object(manager.storage, "get_by_key") as mock_get:
            mock_get.return_value = sample_api_key

            with pytest.raises(AuthenticationError, match="inactive"):
                manager.verify_key(sample_api_key.key)

    def test_verify_key_expired(self, manager, sample_api_key):
        """测试验证已过期的 API Key"""
        sample_api_key.expires_at = datetime.utcnow() - timedelta(days=1)

        with (
            patch.object(manager.storage, "get_by_key") as mock_get,
            patch.object(manager, "update_key") as mock_update,
        ):
            mock_get.return_value = sample_api_key
            mock_update.return_value = sample_api_key

            with pytest.raises(AuthenticationError, match="expired"):
                manager.verify_key(sample_api_key.key)


class TestPermission:
    """测试权限枚举"""

    def test_permission_values(self):
        """测试权限值"""
        assert Permission.READ == "read"
        assert Permission.WRITE == "write"
        assert Permission.ADMIN == "admin"

    def test_permission_comparison(self):
        """测试权限比较"""
        assert Permission.READ == "read"
        assert Permission.READ != "write"
        assert Permission.READ in [Permission.READ, Permission.WRITE]


class TestAPIKeyLifecycle:
    """测试 API Key 完整生命周期"""

    @pytest.fixture
    def manager(self):
        return APIKeyManager()

    def test_create_and_verify(self, manager, sample_organization):
        """测试创建和验证流程"""
        # 1. 创建
        with patch.object(manager.storage, "save") as mock_save:
            mock_save.return_value = True
            api_key, key_value = manager.create_key(
                organization_id=sample_organization.id, name="Lifecycle Test"
            )

        assert api_key.id
        assert key_value

        # 2. 验证
        with (
            patch.object(manager.storage, "get_by_key") as mock_get,
            patch.object(manager.storage, "update_last_used") as mock_update,
        ):
            mock_get.return_value = api_key
            mock_update.return_value = True
            verified = manager.verify_key(key_value)

        assert verified.id == api_key.id

    def test_expired_key_lifecycle(self, manager, sample_organization):
        """测试过期 API Key 的生命周期"""
        # 创建即将过期的 Key
        expires_at = datetime.utcnow() + timedelta(seconds=1)

        with patch.object(manager.storage, "save") as mock_save:
            mock_save.return_value = True
            api_key, key_value = manager.create_key(
                organization_id=sample_organization.id,
                name="Expiring Key",
                expires_at=expires_at,
            )

        # 立即验证应该成功
        with (
            patch.object(manager.storage, "get_by_key") as mock_get,
            patch.object(manager.storage, "update_last_used") as mock_update,
        ):
            mock_get.return_value = api_key
            mock_update.return_value = True
            verified = manager.verify_key(key_value)
        assert verified.id == api_key.id

        # 模拟过期
        api_key.expires_at = datetime.utcnow() - timedelta(seconds=1)

        with (
            patch.object(manager.storage, "get_by_key") as mock_get,
            patch.object(manager, "update_key") as mock_update_key,
        ):
            mock_get.return_value = api_key
            mock_update_key.return_value = api_key

            with pytest.raises(AuthenticationError, match="expired"):
                manager.verify_key(key_value)
