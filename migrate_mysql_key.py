"""
MySQL数据库迁移脚本：将 key_hash 改为 key
"""

import os
import sys

sys.path.insert(0, ".")

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# 加载环境变量
load_dotenv(".env")


def migrate_key_hash_to_key():
    """将key_hash字段改为key字段"""
    # 构建数据库URL
    db_url = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

    print(f"Connecting to database: {os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}")
    engine = create_engine(db_url)

    try:
        with engine.connect() as conn:
            # 开始事务
            trans = conn.begin()

            try:
                # 1. 删除旧的 key_hash 列
                print("Dropping key_hash column...")
                conn.execute(text("ALTER TABLE api_keys DROP COLUMN key_hash"))

                # 2. 添加新的 key 列
                print("Adding key column...")
                conn.execute(
                    text(
                        """
                    ALTER TABLE api_keys 
                    ADD COLUMN `key` VARCHAR(255) NULL 
                    COMMENT 'API Key原始值（明文存储）'
                """
                    )
                )

                # 3. 添加唯一索引
                print("Adding unique index...")
                conn.execute(
                    text(
                        """
                    ALTER TABLE api_keys 
                    ADD UNIQUE INDEX `uq_api_keys_key` (`key`)
                """
                    )
                )

                # 提交事务
                trans.commit()
                print("\n✅ Migration completed successfully!")
                print("Note: All existing API keys have been removed (only hashes were stored).")
                print("You need to create new API keys.")
                return True

            except Exception as e:
                # 回滚事务
                trans.rollback()
                print(f"\n❌ Migration failed: {e}")
                raise

    except Exception as e:
        print(f"\n❌ Database connection failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        success = migrate_key_hash_to_key()
        if success:
            print("\n✅ Database migration successful!")
            print("Now restart the backend server and create new API keys.")
        else:
            print("\n❌ Database migration failed!")
            exit(1)
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
