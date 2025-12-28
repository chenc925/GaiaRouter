"""
测试用户管理器

测试用户认证和用户管理功能
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from bcrypt import gensalt, hashpw

from gaiarouter.auth.user_manager import UserManager, get_user_manager
from gaiarouter.database.models import User


class TestUserManager:
    """测试用户管理器"""

    @pytest.fixture
    def user_manager(self):
        """创建用户管理器实例"""
        return UserManager()

    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        db = Mock()
        db.query.return_value = Mock()
        db.commit.return_value = None
        db.rollback.return_value = None
        db.close.return_value = None
        db.add.return_value = None
        db.refresh.return_value = None
        db.expunge.return_value = None
        return db

    def test_initialization(self, user_manager):
        """测试初始化"""
        assert user_manager.logger is not None

    def test_hash_password(self, user_manager):
        """测试密码哈希"""
        password = "test_password123"
        hashed = user_manager._hash_password(password)

        # 验证哈希值
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password  # 哈希后应该不同

        # 相同密码应该产生不同哈希（因为有盐）
        hashed2 = user_manager._hash_password(password)
        assert hashed != hashed2

    def test_verify_password_correct(self, user_manager):
        """测试验证正确的密码"""
        password = "correct_password"
        hashed = user_manager._hash_password(password)

        result = user_manager._verify_password(password, hashed)
        assert result is True

    def test_verify_password_incorrect(self, user_manager):
        """测试验证错误的密码"""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = user_manager._hash_password(password)

        result = user_manager._verify_password(wrong_password, hashed)
        assert result is False

    def test_verify_password_exception(self, user_manager):
        """测试密码验证异常处理"""
        # 无效的哈希值
        result = user_manager._verify_password("password", "invalid_hash")
        assert result is False

    def test_generate_user_id(self, user_manager):
        """测试生成用户 ID"""
        user_id = user_manager._generate_user_id()

        # 验证格式
        assert user_id.startswith("user_")
        assert len(user_id) > 5

        # 生成多个 ID 应该都不同
        user_ids = [user_manager._generate_user_id() for _ in range(10)]
        assert len(set(user_ids)) == 10

    @patch("gaiarouter.auth.user_manager.get_db")
    def test_create_user_success(self, mock_get_db, user_manager, mock_db):
        """测试成功创建用户"""
        mock_get_db.return_value = iter([mock_db])

        # Mock query result - 用户不存在
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # Mock created user
        def mock_add(user):
            user.id = "user_123"
            user.created_at = datetime.utcnow()

        mock_db.add.side_effect = mock_add

        user = user_manager.create_user(
            username="testuser",
            password="password123",
            email="test@example.com",
            full_name="Test User",
            role="admin",
        )

        # 验证用户对象
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.role == "admin"
        assert user.status == "active"
        assert hasattr(user, "password_hash")

        # 验证数据库操作
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    @patch("gaiarouter.auth.user_manager.get_db")
    def test_create_user_duplicate_username(self, mock_get_db, user_manager, mock_db):
        """测试创建重复用户名的用户"""
        mock_get_db.return_value = iter([mock_db])

        # Mock query result - 用户已存在
        existing_user = User(
            id="user_existing",
            username="testuser",
            password_hash="hash",
            role="admin",
            status="active",
        )
        mock_db.query.return_value.filter.return_value.first.return_value = existing_user

        with pytest.raises(ValueError, match="Username testuser already exists"):
            user_manager.create_user(username="testuser", password="password123")

    @patch("gaiarouter.auth.user_manager.get_db")
    def test_create_user_database_error(self, mock_get_db, user_manager, mock_db):
        """测试创建用户时数据库错误"""
        mock_get_db.return_value = iter([mock_db])

        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.commit.side_effect = Exception("Database error")

        with pytest.raises(Exception, match="Database error"):
            user_manager.create_user(username="testuser", password="password123")

        # 验证 rollback 被调用
        mock_db.rollback.assert_called_once()

    @patch("gaiarouter.auth.user_manager.get_db")
    def test_verify_user_success(self, mock_get_db, user_manager, mock_db):
        """测试成功验证用户"""
        mock_get_db.return_value = iter([mock_db])

        # 创建真实的密码哈希
        password = "password123"
        password_hash = hashpw(password.encode("utf-8"), gensalt()).decode("utf-8")

        mock_user = User(
            id="user_123",
            username="testuser",
            password_hash=password_hash,
            role="admin",
            status="active",
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        result = user_manager.verify_user("testuser", password)

        assert result is not None
        assert result.username == "testuser"
        assert result.id == "user_123"

        # 验证最后登录时间被更新
        mock_db.commit.assert_called_once()

    @patch("gaiarouter.auth.user_manager.get_db")
    def test_verify_user_not_found(self, mock_get_db, user_manager, mock_db):
        """测试验证不存在的用户"""
        mock_get_db.return_value = iter([mock_db])

        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = user_manager.verify_user("nonexistent", "password123")

        assert result is None

    @patch("gaiarouter.auth.user_manager.get_db")
    def test_verify_user_wrong_password(self, mock_get_db, user_manager, mock_db):
        """测试验证错误密码"""
        mock_get_db.return_value = iter([mock_db])

        password_hash = hashpw("correct_password".encode("utf-8"), gensalt()).decode("utf-8")

        mock_user = User(
            id="user_123",
            username="testuser",
            password_hash=password_hash,
            role="admin",
            status="active",
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        result = user_manager.verify_user("testuser", "wrong_password")

        assert result is None

    @patch("gaiarouter.auth.user_manager.get_db")
    def test_verify_user_inactive(self, mock_get_db, user_manager, mock_db):
        """测试验证非活跃用户"""
        mock_get_db.return_value = iter([mock_db])

        mock_user = User(
            id="user_123",
            username="testuser",
            password_hash="hash",
            role="admin",
            status="inactive",  # 非活跃
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        result = user_manager.verify_user("testuser", "password123")

        assert result is None

    @patch("gaiarouter.auth.user_manager.get_db")
    def test_verify_user_exception(self, mock_get_db, user_manager, mock_db):
        """测试验证用户异常处理"""
        mock_get_db.return_value = iter([mock_db])

        mock_db.query.side_effect = Exception("Database error")

        result = user_manager.verify_user("testuser", "password123")

        assert result is None

    @patch("gaiarouter.auth.user_manager.get_db")
    def test_get_user_success(self, mock_get_db, user_manager, mock_db):
        """测试成功获取用户"""
        mock_get_db.return_value = iter([mock_db])

        mock_user = User(
            id="user_123", username="testuser", password_hash="hash", role="admin", status="active"
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        result = user_manager.get_user("user_123")

        assert result is not None
        assert result.id == "user_123"
        assert result.username == "testuser"

    @patch("gaiarouter.auth.user_manager.get_db")
    def test_get_user_not_found(self, mock_get_db, user_manager, mock_db):
        """测试获取不存在的用户"""
        mock_get_db.return_value = iter([mock_db])

        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = user_manager.get_user("user_nonexistent")

        assert result is None

    @patch("gaiarouter.auth.user_manager.get_db")
    def test_get_user_by_username_success(self, mock_get_db, user_manager, mock_db):
        """测试成功根据用户名获取用户"""
        mock_get_db.return_value = iter([mock_db])

        mock_user = User(
            id="user_123", username="testuser", password_hash="hash", role="admin", status="active"
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        result = user_manager.get_user_by_username("testuser")

        assert result is not None
        assert result.username == "testuser"
        assert result.id == "user_123"

    @patch("gaiarouter.auth.user_manager.get_db")
    def test_get_user_by_username_not_found(self, mock_get_db, user_manager, mock_db):
        """测试根据用户名获取不存在的用户"""
        mock_get_db.return_value = iter([mock_db])

        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = user_manager.get_user_by_username("nonexistent")

        assert result is None


class TestGetUserManager:
    """测试获取用户管理器单例"""

    def test_get_user_manager_returns_instance(self):
        """测试返回实例"""
        manager = get_user_manager()
        assert isinstance(manager, UserManager)

    def test_get_user_manager_singleton(self):
        """测试单例模式"""
        # 重置全局变量
        import gaiarouter.auth.user_manager as user_module

        user_module._user_manager = None

        manager1 = get_user_manager()
        manager2 = get_user_manager()

        # 应该返回同一个实例
        assert manager1 is manager2


class TestUserManagerEdgeCases:
    """测试用户管理器边缘情况"""

    @pytest.fixture
    def user_manager(self):
        return UserManager()

    @pytest.fixture
    def mock_db(self):
        db = Mock()
        db.query.return_value = Mock()
        db.commit.return_value = None
        db.close.return_value = None
        db.add.return_value = None
        db.refresh.return_value = None
        db.expunge.return_value = None
        return db

    @patch("gaiarouter.auth.user_manager.get_db")
    def test_create_user_with_minimal_info(self, mock_get_db, user_manager, mock_db):
        """测试创建最小信息的用户"""
        mock_get_db.return_value = iter([mock_db])

        mock_db.query.return_value.filter.return_value.first.return_value = None

        def mock_add(user):
            user.id = "user_123"

        mock_db.add.side_effect = mock_add

        # 只提供必需字段
        user = user_manager.create_user(username="testuser", password="password123")

        assert user.username == "testuser"
        assert user.email is None
        assert user.full_name is None
        assert user.role == "admin"  # 默认角色

    @patch("gaiarouter.auth.user_manager.get_db")
    def test_create_user_with_different_roles(self, mock_get_db, user_manager, mock_db):
        """测试创建不同角色的用户"""
        mock_get_db.return_value = iter([mock_db])

        mock_db.query.return_value.filter.return_value.first.return_value = None

        def mock_add(user):
            user.id = "user_123"

        mock_db.add.side_effect = mock_add

        # 创建普通用户
        user = user_manager.create_user(username="testuser", password="password123", role="user")

        assert user.role == "user"

    def test_hash_password_special_characters(self, user_manager):
        """测试哈希包含特殊字符的密码"""
        passwords = [
            "p@ssw0rd!",
            "密码123",
            "пароль",
            "🔑password🔐",
            "password with spaces",
        ]

        for password in passwords:
            hashed = user_manager._hash_password(password)
            assert user_manager._verify_password(password, hashed) is True

    def test_verify_password_empty_string(self, user_manager):
        """测试验证空密码"""
        hashed = user_manager._hash_password("password")
        result = user_manager._verify_password("", hashed)
        assert result is False

    @patch("gaiarouter.auth.user_manager.get_db")
    def test_verify_user_case_sensitive_username(self, mock_get_db, user_manager, mock_db):
        """测试用户名大小写敏感"""
        password_hash = hashpw("password".encode("utf-8"), gensalt()).decode("utf-8")

        mock_user = User(
            id="user_123",
            username="TestUser",  # 混合大小写
            password_hash=password_hash,
            role="admin",
            status="active",
        )

        # 第一次调用 - 精确匹配
        mock_db_first = Mock()
        mock_db_first.query.return_value = Mock()
        mock_db_first.query.return_value.filter.return_value.first.return_value = mock_user
        mock_db_first.commit.return_value = None
        mock_db_first.close.return_value = None
        mock_get_db.return_value = iter([mock_db_first])

        # 精确匹配应该成功
        result = user_manager.verify_user("TestUser", "password")
        assert result is not None

        # 第二次调用 - 不同大小写
        mock_db_second = Mock()
        mock_db_second.query.return_value = Mock()
        mock_db_second.query.return_value.filter.return_value.first.return_value = None
        mock_db_second.close.return_value = None
        mock_get_db.return_value = iter([mock_db_second])

        # 不同大小写应该失败（取决于数据库配置）
        result = user_manager.verify_user("testuser", "password")
        assert result is None
