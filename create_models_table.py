#!/usr/bin/env python3
"""
创建 models 表的独立脚本
"""

import sys
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect

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
        # 检查表是否已存在
        inspector = inspect(engine)
        if "models" in inspector.get_table_names():
            print("✅ Table 'models' already exists")
            sys.exit(0)

        print("Creating models table...")

        # 创建 models 表
        create_table_sql = """
        CREATE TABLE models (
            id VARCHAR(255) NOT NULL COMMENT '模型ID（完整路径，如openai/gpt-4）',
            name VARCHAR(255) NOT NULL COMMENT '模型名称',
            description TEXT COMMENT '模型描述',
            provider VARCHAR(50) COMMENT '提供商（openrouter, openai, anthropic等）',
            context_length INT COMMENT '上下文长度',
            max_completion_tokens INT COMMENT '最大输出长度',
            pricing_prompt DECIMAL(10, 6) COMMENT '输入价格（每1K tokens，美元）',
            pricing_completion DECIMAL(10, 6) COMMENT '输出价格（每1K tokens，美元）',
            supports_vision TINYINT(1) DEFAULT 0 COMMENT '是否支持视觉',
            supports_function_calling TINYINT(1) DEFAULT 0 COMMENT '是否支持函数调用',
            supports_streaming TINYINT(1) DEFAULT 1 COMMENT '是否支持流式输出',
            is_enabled TINYINT(1) DEFAULT 0 COMMENT '是否启用',
            is_free TINYINT(1) DEFAULT 0 COMMENT '是否免费',
            openrouter_id VARCHAR(255) COMMENT 'OpenRouter 模型ID',
            synced_at DATETIME COMMENT '最后同步时间',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            PRIMARY KEY (id),
            INDEX idx_provider (provider),
            INDEX idx_is_enabled (is_enabled),
            INDEX idx_is_free (is_free)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """

        conn.execute(text(create_table_sql))
        conn.commit()

        print("✅ Table 'models' created successfully!")

        # 验证表结构
        inspector = inspect(engine)
        columns = inspector.get_columns("models")
        print(f"\n✅ Verified {len(columns)} columns in 'models' table:")
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

print("\n✅ Migration completed successfully!")
