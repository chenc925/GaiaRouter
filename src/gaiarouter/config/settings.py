"""
配置管理模块

支持环境变量和配置文件读取
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# 获取项目根目录（.env 文件所在位置）
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

# 手动加载 .env 文件到环境变量
if ENV_FILE.exists():
    # 使用 override=True 确保 .env 文件中的值优先
    load_dotenv(ENV_FILE, override=True)
    # 调试：验证关键环境变量是否被加载
    db_vars = ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"]
    missing_vars = [var for var in db_vars if not os.getenv(var)]
    if missing_vars:
        import warnings

        warnings.warn(
            f".env 文件中缺少以下必需的环境变量: {', '.join(missing_vars)}\n"
            f".env 文件路径: {ENV_FILE}",
            UserWarning,
        )
else:
    import warnings

    warnings.warn(
        f".env 文件不存在: {ENV_FILE}\n" f"请确保 .env 文件存在于项目根目录，或设置环境变量。",
        UserWarning,
    )


class DatabaseSettings(BaseSettings):
    """数据库配置"""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) if ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_prefix="DB_",  # 只读取 DB_ 开头的环境变量
        populate_by_name=True,  # 允许通过字段名和 env 参数匹配
    )

    host: str = Field(..., description="数据库主机")  # 自动匹配 DB_HOST
    port: int = Field(3306, description="数据库端口")  # 自动匹配 DB_PORT
    user: str = Field(..., description="数据库用户名")  # 自动匹配 DB_USER
    password: str = Field(..., description="数据库密码")  # 自动匹配 DB_PASSWORD
    name: str = Field(..., description="数据库名称")  # 自动匹配 DB_NAME

    @property
    def database(self) -> str:
        """数据库名称（兼容性属性）"""
        return self.name

    pool_size: int = Field(10, env="DB_POOL_SIZE", description="连接池大小")
    max_overflow: int = Field(20, env="DB_MAX_OVERFLOW", description="最大溢出连接数")

    @property
    def database_url(self) -> str:
        """获取数据库连接URL"""
        return (
            f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        )


class ProviderSettings(BaseSettings):
    """提供商配置"""

    class Config:
        env_file = str(ENV_FILE) if ENV_FILE.exists() else None
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # 忽略额外的环境变量

    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    google_api_key: Optional[str] = Field(None, env="GOOGLE_API_KEY")
    openrouter_api_key: Optional[str] = Field(None, env="OPENROUTER_API_KEY")


class ServerSettings(BaseSettings):
    """服务器配置"""

    class Config:
        env_file = str(ENV_FILE) if ENV_FILE.exists() else None
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # 忽略额外的环境变量

    host: str = Field("0.0.0.0", env="HOST", description="服务器主机")
    port: int = Field(8000, env="PORT", description="服务器端口")
    debug: bool = Field(False, env="DEBUG", description="调试模式")
    log_level: str = Field("INFO", env="LOG_LEVEL", description="日志级别")


class Settings(BaseSettings):
    """应用配置"""

    class Config:
        env_file = str(ENV_FILE) if ENV_FILE.exists() else None
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # 忽略额外的环境变量

    # 使用 Optional 类型，避免 Pydantic 自动创建
    database: Optional[DatabaseSettings] = None
    providers: Optional[ProviderSettings] = None
    server: Optional[ServerSettings] = None

    def __init__(self, **kwargs):
        """初始化，确保嵌套类能正确读取环境变量"""
        # 先调用父类初始化，但不传递嵌套类的数据
        super().__init__(
            **{k: v for k, v in kwargs.items() if k not in ["database", "providers", "server"]}
        )
        # 手动创建嵌套类实例，确保它们从环境变量读取（不传递任何 kwargs）
        if self.database is None:
            # 在创建前验证必需的环境变量
            if ENV_FILE.exists():
                load_dotenv(ENV_FILE, override=True)
            required_db_vars = ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"]
            missing_vars = [var for var in required_db_vars if not os.getenv(var)]
            if missing_vars:
                raise ValueError(
                    f"缺少必需的数据库环境变量: {', '.join(missing_vars)}\n"
                    f"请检查 .env 文件（路径: {ENV_FILE}）是否包含这些变量。"
                )
            self.database = DatabaseSettings()
        if self.providers is None:
            self.providers = ProviderSettings()
        if self.server is None:
            self.server = ServerSettings()

    # 请求配置
    request_timeout: int = Field(60, env="REQUEST_TIMEOUT", description="请求超时时间（秒）")
    max_retries: int = Field(3, env="MAX_RETRIES", description="最大重试次数")


# 全局配置实例
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    global _settings
    if _settings is None:
        # 确保 .env 文件已加载（防止模块导入顺序问题）
        if ENV_FILE.exists():
            load_dotenv(ENV_FILE, override=True)
        _settings = Settings()
    return _settings


def load_config_from_file(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    从配置文件加载配置

    Args:
      config_path: 配置文件路径，默认为 config.yaml

    Returns:
      配置字典
    """
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent.parent / "config.yaml"
    else:
        config_path = Path(config_path)

    if not config_path.exists():
        return {}

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
