#!/usr/bin/env python3
"""
创建默认管理员用户脚本

使用方法:
    python scripts/create_admin_user.py
    或
    python scripts/create_admin_user.py --username admin --password admin123
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import argparse

from src.gaiarouter.auth.user_manager import get_user_manager
from src.gaiarouter.database import init_db


def main():
    parser = argparse.ArgumentParser(description="创建默认管理员用户")
    parser.add_argument("--username", default="admin", help="用户名（默认：admin）")
    parser.add_argument("--password", default="admin123", help="密码（默认：admin123）")
    parser.add_argument("--email", help="邮箱（可选）")
    parser.add_argument("--full-name", help="全名（可选）")

    args = parser.parse_args()

    # 初始化数据库
    print("初始化数据库...")
    init_db()

    # 创建用户
    print(f"创建管理员用户: {args.username}")
    user_manager = get_user_manager()

    try:
        user = user_manager.create_user(
            username=args.username,
            password=args.password,
            email=args.email,
            full_name=args.full_name or args.username,
            role="admin",
        )
        print(f"✓ 用户创建成功！")
        print(f"  用户ID: {user.id}")
        print(f"  用户名: {user.username}")
        print(f"  角色: {user.role}")
    except ValueError as e:
        print(f"✗ 用户已存在: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ 创建用户失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
