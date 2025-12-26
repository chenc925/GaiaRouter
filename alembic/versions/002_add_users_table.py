"""add users table

Revision ID: 002_add_users
Revises: 001_initial
Create Date: 2024-01-02 00:00:00.000000

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "002"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建用户表
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=64), nullable=False, comment="用户ID"),
        sa.Column("username", sa.String(length=255), nullable=False, comment="用户名"),
        sa.Column("password_hash", sa.String(length=255), nullable=False, comment="密码哈希值"),
        sa.Column("email", sa.String(length=255), nullable=True, comment="邮箱"),
        sa.Column("full_name", sa.String(length=255), nullable=True, comment="全名"),
        sa.Column(
            "role",
            sa.String(length=20),
            server_default="admin",
            nullable=True,
            comment="角色：admin/user",
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default="active",
            nullable=True,
            comment="状态：active/inactive",
        ),
        sa.Column("created_at", sa.DateTime(), nullable=True, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(), nullable=True, comment="更新时间"),
        sa.Column("last_login_at", sa.DateTime(), nullable=True, comment="最后登录时间"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
        comment="用户表",
    )


def downgrade() -> None:
    op.drop_table("users")
