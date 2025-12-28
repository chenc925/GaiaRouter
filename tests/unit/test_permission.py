"""
测试权限管理模块

测试 API Key 权限检查功能
"""

from datetime import datetime
from unittest.mock import Mock

import pytest

from gaiarouter.auth.permission import Permission
from gaiarouter.database.models import APIKey


class TestPermissionConstants:
    """测试权限常量"""

    def test_permission_constants(self):
        """测试权限常量值"""
        assert Permission.READ == "read"
        assert Permission.WRITE == "write"
        assert Permission.ADMIN == "admin"


class TestPermissionCheck:
    """测试权限检查"""

    @pytest.fixture
    def api_key_with_read(self):
        """创建有读权限的 API Key"""
        return APIKey(
            id="ak_123",
            organization_id="org_123",
            name="Test Key",
            key="test-key",
            permissions=["read"],
            status="active",
            created_at=datetime.now(),
        )

    @pytest.fixture
    def api_key_with_write(self):
        """创建有写权限的 API Key"""
        return APIKey(
            id="ak_456",
            organization_id="org_123",
            name="Test Key",
            key="test-key",
            permissions=["write"],
            status="active",
            created_at=datetime.now(),
        )

    @pytest.fixture
    def api_key_with_admin(self):
        """创建有管理员权限的 API Key"""
        return APIKey(
            id="ak_789",
            organization_id="org_123",
            name="Test Key",
            key="test-key",
            permissions=["admin"],
            status="active",
            created_at=datetime.now(),
        )

    @pytest.fixture
    def api_key_with_multiple_permissions(self):
        """创建有多个权限的 API Key"""
        return APIKey(
            id="ak_multi",
            organization_id="org_123",
            name="Test Key",
            key="test-key",
            permissions=["read", "write"],
            status="active",
            created_at=datetime.now(),
        )

    @pytest.fixture
    def api_key_without_permissions(self):
        """创建没有权限的 API Key"""
        return APIKey(
            id="ak_none",
            organization_id="org_123",
            name="Test Key",
            key="test-key",
            permissions=[],
            status="active",
            created_at=datetime.now(),
        )

    def test_check_read_permission(self, api_key_with_read):
        """测试检查读权限"""
        assert Permission.check(api_key_with_read, Permission.READ) is True
        assert Permission.check(api_key_with_read, Permission.WRITE) is False
        assert Permission.check(api_key_with_read, Permission.ADMIN) is False

    def test_check_write_permission(self, api_key_with_write):
        """测试检查写权限"""
        assert Permission.check(api_key_with_write, Permission.READ) is False
        assert Permission.check(api_key_with_write, Permission.WRITE) is True
        assert Permission.check(api_key_with_write, Permission.ADMIN) is False

    def test_check_admin_permission_grants_all(self, api_key_with_admin):
        """测试管理员权限拥有所有权限"""
        assert Permission.check(api_key_with_admin, Permission.READ) is True
        assert Permission.check(api_key_with_admin, Permission.WRITE) is True
        assert Permission.check(api_key_with_admin, Permission.ADMIN) is True

    def test_check_multiple_permissions(self, api_key_with_multiple_permissions):
        """测试检查多个权限"""
        assert Permission.check(api_key_with_multiple_permissions, Permission.READ) is True
        assert Permission.check(api_key_with_multiple_permissions, Permission.WRITE) is True
        assert Permission.check(api_key_with_multiple_permissions, Permission.ADMIN) is False

    def test_check_no_permissions(self, api_key_without_permissions):
        """测试没有权限"""
        assert Permission.check(api_key_without_permissions, Permission.READ) is False
        assert Permission.check(api_key_without_permissions, Permission.WRITE) is False
        assert Permission.check(api_key_without_permissions, Permission.ADMIN) is False

    def test_check_null_api_key(self):
        """测试 API Key 为 None"""
        assert Permission.check(None, Permission.READ) is False
        assert Permission.check(None, Permission.WRITE) is False
        assert Permission.check(None, Permission.ADMIN) is False

    def test_check_api_key_with_none_permissions(self):
        """测试 permissions 为 None 的 API Key"""
        api_key = APIKey(
            id="ak_null",
            organization_id="org_123",
            name="Test Key",
            key="test-key",
            permissions=None,
            status="active",
            created_at=datetime.now(),
        )

        assert Permission.check(api_key, Permission.READ) is False
        assert Permission.check(api_key, Permission.WRITE) is False
        assert Permission.check(api_key, Permission.ADMIN) is False


class TestPermissionHelpers:
    """测试权限辅助方法"""

    @pytest.fixture
    def api_key_read_only(self):
        """只读权限的 API Key"""
        return APIKey(
            id="ak_read",
            organization_id="org_123",
            name="Read Only Key",
            key="test-key",
            permissions=["read"],
            status="active",
            created_at=datetime.now(),
        )

    @pytest.fixture
    def api_key_full_access(self):
        """完全访问权限的 API Key"""
        return APIKey(
            id="ak_full",
            organization_id="org_123",
            name="Full Access Key",
            key="test-key",
            permissions=["read", "write", "admin"],
            status="active",
            created_at=datetime.now(),
        )

    @pytest.fixture
    def api_key_admin_only(self):
        """只有管理员权限的 API Key"""
        return APIKey(
            id="ak_admin",
            organization_id="org_123",
            name="Admin Key",
            key="test-key",
            permissions=["admin"],
            status="active",
            created_at=datetime.now(),
        )

    def test_has_read(self, api_key_read_only, api_key_full_access):
        """测试 has_read 方法"""
        assert Permission.has_read(api_key_read_only) is True
        assert Permission.has_read(api_key_full_access) is True

        # Admin 权限也应该有读权限
        api_key_admin = APIKey(
            id="ak_admin",
            organization_id="org_123",
            name="Admin Key",
            key="test-key",
            permissions=["admin"],
            status="active",
            created_at=datetime.now(),
        )
        assert Permission.has_read(api_key_admin) is True

    def test_has_write(self, api_key_read_only, api_key_full_access):
        """测试 has_write 方法"""
        assert Permission.has_write(api_key_read_only) is False
        assert Permission.has_write(api_key_full_access) is True

        # Admin 权限也应该有写权限
        api_key_admin = APIKey(
            id="ak_admin",
            organization_id="org_123",
            name="Admin Key",
            key="test-key",
            permissions=["admin"],
            status="active",
            created_at=datetime.now(),
        )
        assert Permission.has_write(api_key_admin) is True

    def test_has_admin(self, api_key_read_only, api_key_admin_only):
        """测试 has_admin 方法"""
        assert Permission.has_admin(api_key_read_only) is False
        assert Permission.has_admin(api_key_admin_only) is True

    def test_has_read_with_none(self):
        """测试 has_read 处理 None"""
        assert Permission.has_read(None) is False

    def test_has_write_with_none(self):
        """测试 has_write 处理 None"""
        assert Permission.has_write(None) is False

    def test_has_admin_with_none(self):
        """测试 has_admin 处理 None"""
        assert Permission.has_admin(None) is False


class TestPermissionEdgeCases:
    """测试权限边缘情况"""

    def test_case_sensitive_permissions(self):
        """测试权限大小写敏感"""
        api_key = APIKey(
            id="ak_case",
            organization_id="org_123",
            name="Test Key",
            key="test-key",
            permissions=["READ"],  # 大写
            status="active",
            created_at=datetime.now(),
        )

        # 权限是大小写敏感的，"READ" != "read"
        assert Permission.check(api_key, Permission.READ) is False
        assert Permission.check(api_key, "READ") is True

    def test_empty_permission_string(self):
        """测试空字符串权限"""
        api_key = APIKey(
            id="ak_empty",
            organization_id="org_123",
            name="Test Key",
            key="test-key",
            permissions=["read", ""],
            status="active",
            created_at=datetime.now(),
        )

        assert Permission.check(api_key, "") is True
        assert Permission.check(api_key, Permission.READ) is True

    def test_unknown_permission(self):
        """测试未知权限"""
        api_key = APIKey(
            id="ak_unknown",
            organization_id="org_123",
            name="Test Key",
            key="test-key",
            permissions=["read", "write"],
            status="active",
            created_at=datetime.now(),
        )

        # 检查一个不存在的权限
        assert Permission.check(api_key, "unknown_permission") is False

    def test_admin_permission_precedence(self):
        """测试管理员权限优先级"""
        # Admin 权限即使单独存在也应该授予所有权限
        api_key = APIKey(
            id="ak_admin_only",
            organization_id="org_123",
            name="Admin Only Key",
            key="test-key",
            permissions=["admin"],  # 只有 admin
            status="active",
            created_at=datetime.now(),
        )

        # 应该拥有所有权限
        assert Permission.has_read(api_key) is True
        assert Permission.has_write(api_key) is True
        assert Permission.has_admin(api_key) is True

        # 检查任意权限都应该通过
        assert Permission.check(api_key, "custom_permission") is True

    def test_duplicate_permissions(self):
        """测试重复权限"""
        api_key = APIKey(
            id="ak_dup",
            organization_id="org_123",
            name="Test Key",
            key="test-key",
            permissions=["read", "read", "write"],
            status="active",
            created_at=datetime.now(),
        )

        # 重复的权限不应该影响检查结果
        assert Permission.has_read(api_key) is True
        assert Permission.has_write(api_key) is True
        assert Permission.has_admin(api_key) is False

    def test_whitespace_in_permissions(self):
        """测试权限中的空白字符"""
        api_key = APIKey(
            id="ak_space",
            organization_id="org_123",
            name="Test Key",
            key="test-key",
            permissions=[" read ", "write"],
            status="active",
            created_at=datetime.now(),
        )

        # 权限是精确匹配的，" read " != "read"
        assert Permission.check(api_key, "read") is False
        assert Permission.check(api_key, " read ") is True
        assert Permission.check(api_key, "write") is True
