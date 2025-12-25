"""
手动迁移脚本：将 key_hash 改为 key
"""

import os
import sqlite3


def migrate_key_hash_to_key():
    """将key_hash字段改为key字段"""
    # 连接数据库
    db_path = "openrouter.db"
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 检查表结构
        cursor.execute("PRAGMA table_info(api_keys)")
        columns = [row[1] for row in cursor.fetchall()]

        print(f"Current columns: {columns}")

        # 如果有key_hash字段，需要迁移
        if "key_hash" in columns:
            print("Found key_hash column, migrating to key...")

            # SQLite不支持直接重命名列，需要重建表
            # 1. 创建新表
            cursor.execute(
                """
                CREATE TABLE api_keys_new (
                    id VARCHAR(64) PRIMARY KEY,
                    organization_id VARCHAR(64) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    key VARCHAR(255) UNIQUE,
                    permissions JSON,
                    status VARCHAR(20) DEFAULT 'active',
                    expires_at DATETIME,
                    created_at DATETIME,
                    updated_at DATETIME,
                    last_used_at DATETIME,
                    FOREIGN KEY (organization_id) REFERENCES organizations(id)
                )
            """
            )

            # 2. 复制数据（key_hash字段不复制，因为已经是哈希值）
            cursor.execute(
                """
                INSERT INTO api_keys_new 
                (id, organization_id, name, description, permissions, status, 
                 expires_at, created_at, updated_at, last_used_at)
                SELECT id, organization_id, name, description, permissions, status,
                       expires_at, created_at, updated_at, last_used_at
                FROM api_keys
            """
            )

            # 3. 删除旧表
            cursor.execute("DROP TABLE api_keys")

            # 4. 重命名新表
            cursor.execute("ALTER TABLE api_keys_new RENAME TO api_keys")

            conn.commit()
            print("Migration completed successfully!")
            print("Note: All existing API keys have been removed (only hashes were stored).")
            print("You need to create new API keys.")

        elif "key" in columns:
            print("Already migrated, key column exists.")
        else:
            print("ERROR: Neither key_hash nor key column found!")
            return False

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

    return True


if __name__ == "__main__":
    try:
        success = migrate_key_hash_to_key()
        if success:
            print("\n✅ Database migration successful!")
            print("Now you can restart the backend server and create new API keys.")
        else:
            print("\n❌ Database migration failed!")
            exit(1)
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
