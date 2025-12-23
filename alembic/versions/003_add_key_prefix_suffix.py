"""change key_hash to key in api_keys

Revision ID: 003
Revises: 002
Create Date: 2025-12-23 17:18:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 直接按当前 schema 执行列变更（新库可以假定 002 已正确创建表结构）
    # 删除旧的 key_hash 列（如果存在）并新增 key 列
    with op.batch_alter_table("api_keys") as batch_op:
        try:
            batch_op.drop_column("key_hash")
        except Exception:
            # 如果列不存在，忽略错误，避免对已有环境造成影响
            pass

        try:
            batch_op.add_column(
                sa.Column(
                    "key",
                    sa.String(length=255),
                    nullable=True,
                    comment="API Key原始值（明文存储）",
                )
            )
        except Exception:
            # 如果列已存在，同样忽略
            pass

        try:
            batch_op.create_unique_constraint("uq_api_keys_key", ["key"])
        except Exception:
            # 约束已存在时忽略
            pass


def downgrade() -> None:
    # 恢复为key_hash字段
    op.drop_column("api_keys", "key")
    op.add_column(
        "api_keys",
        sa.Column(
            "key_hash",
            sa.String(length=255),
            nullable=False,
            unique=True,
            comment="API Key哈希值（加密存储）",
        ),
    )
