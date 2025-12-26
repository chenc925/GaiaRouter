"""initial schema

Revision ID: 001_initial
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""

import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from alembic import op

# revision identifiers, used by Alembic.
revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建组织表
    op.create_table(
        "organizations",
        sa.Column("id", sa.String(length=64), nullable=False, comment="组织ID"),
        sa.Column("name", sa.String(length=255), nullable=False, comment="组织名称"),
        sa.Column("description", sa.Text(), nullable=True, comment="组织描述"),
        sa.Column("admin_user_id", sa.String(length=64), nullable=True, comment="管理员用户ID"),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default="active",
            nullable=True,
            comment="状态：active/inactive",
        ),
        sa.Column(
            "monthly_requests_limit", sa.Integer(), nullable=True, comment="月度请求次数限制"
        ),
        sa.Column("monthly_tokens_limit", sa.Integer(), nullable=True, comment="月度Token限制"),
        sa.Column(
            "monthly_cost_limit",
            sa.Numeric(precision=10, scale=2),
            nullable=True,
            comment="月度费用限制",
        ),
        sa.Column("created_at", sa.DateTime(), nullable=True, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(), nullable=True, comment="更新时间"),
        sa.PrimaryKeyConstraint("id"),
        comment="组织表",
    )

    # 创建API Key表
    op.create_table(
        "api_keys",
        sa.Column("id", sa.String(length=64), nullable=False, comment="API Key ID"),
        sa.Column("organization_id", sa.String(length=64), nullable=False, comment="组织ID"),
        sa.Column("name", sa.String(length=255), nullable=False, comment="API Key名称"),
        sa.Column("description", sa.Text(), nullable=True, comment="描述"),
        sa.Column(
            "key_hash", sa.String(length=255), nullable=False, comment="API Key哈希值（加密存储）"
        ),
        sa.Column("permissions", sa.JSON(), nullable=True, comment="权限列表"),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default="active",
            nullable=True,
            comment="状态：active/inactive/expired",
        ),
        sa.Column("expires_at", sa.DateTime(), nullable=True, comment="过期时间"),
        sa.Column("created_at", sa.DateTime(), nullable=True, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(), nullable=True, comment="更新时间"),
        sa.Column("last_used_at", sa.DateTime(), nullable=True, comment="最后使用时间"),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key_hash"),
        comment="API Key表",
    )
    op.create_index(
        op.f("ix_api_keys_organization_id"), "api_keys", ["organization_id"], unique=False
    )

    # 创建请求统计表
    op.create_table(
        "request_stats",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="统计ID"),
        sa.Column("api_key_id", sa.String(length=64), nullable=False, comment="API Key ID"),
        sa.Column("organization_id", sa.String(length=64), nullable=True, comment="组织ID"),
        sa.Column("model", sa.String(length=255), nullable=False, comment="模型标识"),
        sa.Column("provider", sa.String(length=50), nullable=False, comment="提供商"),
        sa.Column(
            "prompt_tokens", sa.Integer(), server_default="0", nullable=True, comment="输入Token数"
        ),
        sa.Column(
            "completion_tokens",
            sa.Integer(),
            server_default="0",
            nullable=True,
            comment="输出Token数",
        ),
        sa.Column(
            "total_tokens", sa.Integer(), server_default="0", nullable=True, comment="总Token数"
        ),
        sa.Column("cost", sa.Numeric(precision=10, scale=4), nullable=True, comment="费用"),
        sa.Column("timestamp", sa.DateTime(), nullable=True, comment="请求时间"),
        sa.ForeignKeyConstraint(
            ["api_key_id"],
            ["api_keys.id"],
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        comment="请求统计表",
    )
    op.create_index(
        op.f("ix_request_stats_timestamp"), "request_stats", ["timestamp"], unique=False
    )
    op.create_index(
        op.f("ix_request_stats_api_key_id"), "request_stats", ["api_key_id"], unique=False
    )
    op.create_index(
        op.f("ix_request_stats_organization_id"), "request_stats", ["organization_id"], unique=False
    )


def downgrade() -> None:
    # 删除索引
    op.drop_index(op.f("ix_request_stats_organization_id"), table_name="request_stats")
    op.drop_index(op.f("ix_request_stats_api_key_id"), table_name="request_stats")
    op.drop_index(op.f("ix_request_stats_timestamp"), table_name="request_stats")
    op.drop_index(op.f("ix_api_keys_organization_id"), table_name="api_keys")

    # 删除表
    op.drop_table("request_stats")
    op.drop_table("api_keys")
    op.drop_table("organizations")
