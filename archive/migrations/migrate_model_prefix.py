#!/usr/bin/env python3
"""
给现有模型 ID 添加 openrouter/ 前缀的迁移脚本
"""

import sys
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# 加载环境变量
load_dotenv(".env")

# 数据库连接信息
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME")

db_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print(f"Connecting to database: {DB_HOST}/{DB_NAME}")

try:
    engine = create_engine(db_url, echo=False)

    with engine.connect() as conn:
        # 开始事务
        trans = conn.begin()

        try:
            # 1. 检查是否有需要迁移的模型（没有 openrouter/ 前缀的）
            result = conn.execute(
                text(
                    """
                SELECT COUNT(*) as count 
                FROM models 
                WHERE id NOT LIKE 'openrouter/%' AND provider = 'openrouter'
            """
                )
            )
            count = result.fetchone()[0]

            if count == 0:
                print("✅ No models need migration (all models already have openrouter/ prefix)")
                trans.commit()
                sys.exit(0)

            print(f"Found {count} models to migrate")

            # 2. 创建临时表来存储旧 ID 和新 ID 的映射
            print("Creating temporary mapping...")

            # 3. 更新模型 ID（添加 openrouter/ 前缀）
            print("Updating model IDs...")

            # 由于 id 是主键，我们需要：
            # a) 先获取所有需要更新的模型
            result = conn.execute(
                text(
                    """
                SELECT id, name, openrouter_id 
                FROM models 
                WHERE id NOT LIKE 'openrouter/%' AND provider = 'openrouter'
            """
                )
            )

            models_to_update = result.fetchall()

            # b) 为每个模型创建新记录并删除旧记录
            updated_count = 0
            for old_id, name, openrouter_id in models_to_update:
                new_id = f"openrouter/{old_id}"

                # 复制记录到新 ID
                conn.execute(
                    text(
                        """
                    INSERT INTO models (
                        id, name, description, provider, context_length, 
                        max_completion_tokens, pricing_prompt, pricing_completion,
                        supports_vision, supports_function_calling, supports_streaming,
                        is_enabled, is_free, openrouter_id, synced_at, created_at, updated_at
                    )
                    SELECT 
                        :new_id, name, description, provider, context_length,
                        max_completion_tokens, pricing_prompt, pricing_completion,
                        supports_vision, supports_function_calling, supports_streaming,
                        is_enabled, is_free, openrouter_id, synced_at, created_at, NOW()
                    FROM models
                    WHERE id = :old_id
                """
                    ),
                    {"new_id": new_id, "old_id": old_id},
                )

                # 删除旧记录
                conn.execute(text("DELETE FROM models WHERE id = :old_id"), {"old_id": old_id})

                updated_count += 1
                if updated_count % 50 == 0:
                    print(f"  Migrated {updated_count}/{count} models...")

            print(f"✅ Successfully migrated {updated_count} models")

            # 提交事务
            trans.commit()

            # 4. 验证迁移结果
            result = conn.execute(
                text(
                    """
                SELECT COUNT(*) as count 
                FROM models 
                WHERE id LIKE 'openrouter/%'
            """
                )
            )
            new_count = result.fetchone()[0]

            print(f"\n✅ Migration completed successfully!")
            print(f"   Total models with openrouter/ prefix: {new_count}")

        except Exception as e:
            # 回滚事务
            trans.rollback()
            print(f"\n❌ Migration failed: {e}")
            import traceback

            traceback.print_exc()
            sys.exit(1)

except Exception as e:
    print(f"\n❌ Database connection failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

print("\n✅ All migrations completed successfully!")
