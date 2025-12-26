#!/usr/bin/env python3
"""检查环境变量配置"""

import os
from pathlib import Path

from dotenv import load_dotenv

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent
ENV_FILE = PROJECT_ROOT / ".env"

print(f"检查 .env 文件: {ENV_FILE}")
print(f".env 文件存在: {ENV_FILE.exists()}\n")

if ENV_FILE.exists():
    # 加载 .env 文件
    load_dotenv(ENV_FILE, override=True)
    print("已加载 .env 文件\n")

    # 检查数据库相关环境变量
    db_vars = {
        "DB_HOST": os.getenv("DB_HOST"),
        "DB_PORT": os.getenv("DB_PORT"),
        "DB_USER": os.getenv("DB_USER"),
        "DB_PASSWORD": os.getenv("DB_PASSWORD"),
        "DB_NAME": os.getenv("DB_NAME"),
    }

    print("数据库环境变量:")
    for key, value in db_vars.items():
        if value:
            # 密码只显示前3个字符
            if key == "DB_PASSWORD":
                display_value = value[:3] + "***" if len(value) > 3 else "***"
            else:
                display_value = value
            print(f"  {key} = {display_value}")
        else:
            print(f"  {key} = (未设置)")

    # 检查是否有缺失的必需变量
    required_vars = ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"]
    missing = [var for var in required_vars if not db_vars.get(var)]

    if missing:
        print(f"\n❌ 缺少必需的环境变量: {', '.join(missing)}")
    else:
        print("\n✅ 所有必需的数据库环境变量都已设置")
else:
    print("❌ .env 文件不存在！")
    print(f"请从 env.example 创建 .env 文件:")
    print(f"  cp env.example .env")
    print("然后编辑 .env 文件，填入实际的配置值。")
