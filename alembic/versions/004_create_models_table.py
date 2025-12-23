"""create models table

Revision ID: 004
Revises: 003
Create Date: 2025-12-23

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建models表
    op.create_table(
        "models",
        sa.Column(
            "id",
            sa.String(length=255),
            nullable=False,
            comment="模型ID（完整路径，如openai/gpt-4）",
        ),
        sa.Column("name", sa.String(length=255), nullable=False, comment="模型名称"),
        sa.Column("description", sa.Text(), nullable=True, comment="模型描述"),
        sa.Column(
            "provider",
            sa.String(length=50),
            nullable=True,
            comment="提供商（openrouter, openai, anthropic等）",
        ),
        sa.Column("context_length", sa.Integer(), nullable=True, comment="上下文长度"),
        sa.Column("max_completion_tokens", sa.Integer(), nullable=True, comment="最大输出Token数"),
        sa.Column(
            "pricing_prompt",
            sa.Numeric(precision=10, scale=6),
            nullable=True,
            comment="输入价格（每1K tokens，美元）",
        ),
        sa.Column(
            "pricing_completion",
            sa.Numeric(precision=10, scale=6),
            nullable=True,
            comment="输出价格（每1K tokens，美元）",
        ),
        sa.Column(
            "supports_vision", sa.Boolean(), nullable=True, default=False, comment="是否支持视觉"
        ),
        sa.Column(
            "supports_function_calling",
            sa.Boolean(),
            nullable=True,
            default=False,
            comment="是否支持函数调用",
        ),
        sa.Column(
            "supports_streaming",
            sa.Boolean(),
            nullable=True,
            default=True,
            comment="是否支持流式输出",
        ),
        sa.Column("is_enabled", sa.Boolean(), nullable=True, default=False, comment="是否启用"),
        sa.Column("is_free", sa.Boolean(), nullable=True, default=False, comment="是否免费"),
        sa.Column(
            "openrouter_id", sa.String(length=255), nullable=True, comment="OpenRouter 模型ID"
        ),
        sa.Column("created_at", sa.DateTime(), nullable=True, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(), nullable=True, comment="更新时间"),
        sa.Column("synced_at", sa.DateTime(), nullable=True, comment="最后同步时间"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("models")
