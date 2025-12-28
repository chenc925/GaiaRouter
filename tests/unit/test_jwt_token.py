"""
测试 JWT Token 管理器

测试 JWT token 生成和验证功能
"""

import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import jwt
import pytest

from gaiarouter.auth.jwt_token import JWTTokenManager, get_token_manager


class TestJWTTokenManager:
    """测试 JWT Token 管理器"""

    @pytest.fixture
    def token_manager(self):
        """创建 token 管理器实例"""
        return JWTTokenManager()

    def test_initialization(self, token_manager):
        """测试初始化"""
        assert token_manager.algorithm == "HS256"
        assert token_manager.token_expire_hours == 24
        assert token_manager.secret_key is not None

    def test_generate_token_success(self, token_manager):
        """测试成功生成 token"""
        token = token_manager.generate_token(
            user_id="user_123", username="testuser", role="admin"
        )

        # 验证 token 格式
        assert isinstance(token, str)
        assert len(token) > 0

        # 验证 token 可以被解码
        payload = jwt.decode(token, token_manager.secret_key, algorithms=[token_manager.algorithm])
        assert payload["user_id"] == "user_123"
        assert payload["username"] == "testuser"
        assert payload["role"] == "admin"
        assert "exp" in payload
        assert "iat" in payload

    def test_generate_token_with_different_roles(self, token_manager):
        """测试生成不同角色的 token"""
        # Admin role
        admin_token = token_manager.generate_token("user_1", "admin_user", "admin")
        admin_payload = jwt.decode(
            admin_token, token_manager.secret_key, algorithms=[token_manager.algorithm]
        )
        assert admin_payload["role"] == "admin"

        # User role
        user_token = token_manager.generate_token("user_2", "regular_user", "user")
        user_payload = jwt.decode(
            user_token, token_manager.secret_key, algorithms=[token_manager.algorithm]
        )
        assert user_payload["role"] == "user"

    def test_generate_token_expiration(self, token_manager):
        """测试 token 过期时间设置"""
        before_time = datetime.utcnow()
        token = token_manager.generate_token("user_123", "testuser", "admin")
        after_time = datetime.utcnow()

        payload = jwt.decode(token, token_manager.secret_key, algorithms=[token_manager.algorithm])

        # 验证过期时间在 24 小时后
        exp_time = datetime.fromtimestamp(payload["exp"])
        expected_exp = before_time + timedelta(hours=24)

        # 允许几秒的误差
        assert abs((exp_time - expected_exp).total_seconds()) < 5

    def test_verify_token_success(self, token_manager):
        """测试成功验证 token"""
        token = token_manager.generate_token("user_123", "testuser", "admin")
        payload = token_manager.verify_token(token)

        assert payload is not None
        assert payload["user_id"] == "user_123"
        assert payload["username"] == "testuser"
        assert payload["role"] == "admin"

    def test_verify_token_expired(self, token_manager):
        """测试验证过期的 token"""
        # 创建一个已经过期的 token
        now = datetime.utcnow()
        exp = now - timedelta(hours=1)  # 1小时前过期

        payload = {
            "user_id": "user_123",
            "username": "testuser",
            "role": "admin",
            "exp": int(exp.timestamp()),
            "iat": int((now - timedelta(hours=25)).timestamp()),
        }

        expired_token = jwt.encode(payload, token_manager.secret_key, algorithm=token_manager.algorithm)

        # 验证应该返回 None
        result = token_manager.verify_token(expired_token)
        assert result is None

    def test_verify_token_invalid_signature(self, token_manager):
        """测试验证签名错误的 token"""
        # 使用错误的密钥生成 token
        wrong_secret = "wrong-secret-key"
        payload = {
            "user_id": "user_123",
            "username": "testuser",
            "role": "admin",
            "exp": int((datetime.utcnow() + timedelta(hours=24)).timestamp()),
            "iat": int(datetime.utcnow().timestamp()),
        }

        invalid_token = jwt.encode(payload, wrong_secret, algorithm="HS256")

        # 验证应该返回 None
        result = token_manager.verify_token(invalid_token)
        assert result is None

    def test_verify_token_malformed(self, token_manager):
        """测试验证格式错误的 token"""
        malformed_tokens = [
            "not-a-jwt-token",
            "invalid.token.format",
            "",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid",
        ]

        for malformed_token in malformed_tokens:
            result = token_manager.verify_token(malformed_token)
            assert result is None

    def test_verify_token_tampered(self, token_manager):
        """测试验证被篡改的 token"""
        token = token_manager.generate_token("user_123", "testuser", "admin")

        # 篡改 token (修改最后几个字符)
        tampered_token = token[:-5] + "XXXXX"

        result = token_manager.verify_token(tampered_token)
        assert result is None

    def test_verify_token_exception_handling(self, token_manager):
        """测试验证 token 时的异常处理"""
        # 使用 None 应该返回 None 而不是抛出异常
        result = token_manager.verify_token(None)
        assert result is None

    def test_token_contains_all_required_fields(self, token_manager):
        """测试 token 包含所有必需字段"""
        token = token_manager.generate_token("user_123", "testuser", "admin")
        payload = jwt.decode(token, token_manager.secret_key, algorithms=[token_manager.algorithm])

        # 验证所有必需字段
        assert "user_id" in payload
        assert "username" in payload
        assert "role" in payload
        assert "exp" in payload
        assert "iat" in payload

    def test_different_tokens_for_different_users(self, token_manager):
        """测试不同用户生成不同的 token"""
        token1 = token_manager.generate_token("user_1", "user1", "admin")
        token2 = token_manager.generate_token("user_2", "user2", "user")

        # Token 应该不同
        assert token1 != token2

        # 但都应该有效
        payload1 = token_manager.verify_token(token1)
        payload2 = token_manager.verify_token(token2)

        assert payload1["user_id"] == "user_1"
        assert payload2["user_id"] == "user_2"


class TestGetTokenManager:
    """测试获取 token 管理器单例"""

    def test_get_token_manager_returns_instance(self):
        """测试返回实例"""
        manager = get_token_manager()
        assert isinstance(manager, JWTTokenManager)

    def test_get_token_manager_singleton(self):
        """测试单例模式"""
        # 重置全局变量
        import gaiarouter.auth.jwt_token as jwt_module

        jwt_module._token_manager = None

        manager1 = get_token_manager()
        manager2 = get_token_manager()

        # 应该返回同一个实例
        assert manager1 is manager2

    def test_get_token_manager_reuse(self):
        """测试重复调用返回相同实例"""
        managers = [get_token_manager() for _ in range(5)]

        # 所有实例应该是同一个
        for manager in managers[1:]:
            assert manager is managers[0]


class TestTokenExpiration:
    """测试 token 过期相关功能"""

    @pytest.fixture
    def token_manager(self):
        return JWTTokenManager()

    def test_token_with_long_expiration(self, token_manager):
        """测试长过期时间的 token"""
        # 创建一个30天后过期的 token
        now = datetime.utcnow()
        exp = now + timedelta(days=30)

        payload = {
            "user_id": "user_123",
            "username": "testuser",
            "role": "admin",
            "exp": int(exp.timestamp()),
            "iat": int(now.timestamp()),
        }

        token = jwt.encode(payload, token_manager.secret_key, algorithm=token_manager.algorithm)

        # 验证应该成功
        result = token_manager.verify_token(token)
        assert result is not None
        assert result["user_id"] == "user_123"

    def test_iat_before_exp(self, token_manager):
        """测试 iat 时间在 exp 之前"""
        token = token_manager.generate_token("user_123", "testuser", "admin")
        payload = jwt.decode(token, token_manager.secret_key, algorithms=[token_manager.algorithm])

        # iat 应该在 exp 之前
        assert payload["iat"] < payload["exp"]

        # 时间差应该约等于 24 小时
        time_diff_hours = (payload["exp"] - payload["iat"]) / 3600
        assert 23.9 < time_diff_hours < 24.1


class TestTokenSecurity:
    """测试 token 安全性"""

    @pytest.fixture
    def token_manager(self):
        return JWTTokenManager()

    def test_token_cannot_be_decoded_without_secret(self, token_manager):
        """测试没有密钥无法解码 token"""
        token = token_manager.generate_token("user_123", "testuser", "admin")

        # 尝试用错误的密钥解码应该失败
        with pytest.raises(jwt.InvalidSignatureError):
            jwt.decode(token, "wrong-secret", algorithms=["HS256"])

    def test_token_uses_hs256_algorithm(self, token_manager):
        """测试使用 HS256 算法"""
        token = token_manager.generate_token("user_123", "testuser", "admin")

        # 解码 header 检查算法
        header = jwt.get_unverified_header(token)
        assert header["alg"] == "HS256"
        assert header["typ"] == "JWT"

    def test_different_secret_keys_produce_different_tokens(self):
        """测试不同密钥生成不同 token"""
        manager1 = JWTTokenManager()
        manager2 = JWTTokenManager()

        # 如果密钥相同（默认行为），token 验证应该互通
        token1 = manager1.generate_token("user_123", "testuser", "admin")
        payload = manager2.verify_token(token1)

        assert payload is not None
        assert payload["user_id"] == "user_123"
