#!/usr/bin/env python3
"""
GaiaRouter 统一初始化脚本

使用方法:
    # 使用默认配置初始化
    python scripts/init.py

    # 自定义管理员账号
    python scripts/init.py --admin-username myadmin --admin-password mypassword

    # 同时同步 OpenRouter 模型
    python scripts/init.py --sync-models

    # 跳过某些步骤
    python scripts/init.py --skip-migrations --skip-admin
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def print_header(title):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_step(step_num, step_name):
    """打印步骤"""
    print(f"\n[{step_num}/4] {step_name}")
    print("-" * 60)


def check_env_file():
    """检查 .env 文件是否存在"""
    env_file = project_root / ".env"
    if not env_file.exists():
        print("❌ 错误: .env 文件不存在")
        print("\n请执行以下步骤:")
        print("  1. 复制模板: cp env.example .env")
        print("  2. 编辑 .env 文件，配置数据库连接信息")
        print("  3. 重新运行此脚本")
        return False

    # 检查必需的环境变量
    from dotenv import load_dotenv

    load_dotenv(env_file)

    required_vars = ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"❌ 错误: .env 文件缺少必需的变量: {', '.join(missing_vars)}")
        print("\n请在 .env 文件中配置:")
        for var in missing_vars:
            print(f"  {var}=...")
        return False

    print("✓ .env 文件配置正确")
    return True


def run_migrations():
    """运行数据库迁移"""
    print("🔄 执行数据库迁移...")
    try:
        # 使用 python -m alembic 确保使用正确的 Python 环境
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=project_root,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print("❌ 数据库迁移失败")
            print("\n错误信息:")
            print(result.stderr)
            return False

        print("✓ 数据库迁移完成")
        # 显示迁移输出
        if result.stdout:
            for line in result.stdout.strip().split("\n"):
                if "Running upgrade" in line or "INFO" in line:
                    print(f"  {line}")
        return True

    except Exception as e:
        print(f"❌ 执行迁移时出错: {e}")
        return False


def create_admin_user(username, password):
    """创建管理员用户"""
    print(f"👤 创建管理员用户: {username}...")

    try:
        from src.gaiarouter.auth.user_manager import get_user_manager
        from src.gaiarouter.database import init_db

        init_db()
        user_manager = get_user_manager()

        try:
            user = user_manager.create_user(
                username=username, password=password, full_name=username, role="admin"
            )
            print(f"✓ 管理员用户创建成功")
            print(f"  用户ID: {user.id}")
            print(f"  用户名: {user.username}")
            print(f"  角色: {user.role}")
            return True

        except ValueError as e:
            # 用户已存在
            if "already exists" in str(e) or "已存在" in str(e):
                print(f"⚠️  管理员用户已存在: {username}")
                print("  如需使用新密码，请先删除现有用户或使用不同的用户名")
                return True  # 不算作失败
            else:
                raise

    except Exception as e:
        print(f"❌ 创建管理员用户失败: {e}")
        import traceback

        traceback.print_exc()
        return False


async def sync_openrouter_models():
    """同步 OpenRouter 模型"""
    print("🔄 同步 OpenRouter 模型...")

    try:
        from src.gaiarouter.config import get_settings
        from src.gaiarouter.models.sync import sync_models_from_openrouter

        settings = get_settings()

        # 检查是否配置了 OpenRouter API Key
        if not settings.providers.openrouter_api_key:
            print("⚠️  未配置 OPENROUTER_API_KEY，跳过模型同步")
            print("  如需同步模型，请在 .env 文件中添加:")
            print("    OPENROUTER_API_KEY=sk-or-your-api-key")
            return True  # 跳过不算失败

        stats = await sync_models_from_openrouter()

        print("✓ OpenRouter 模型同步完成")
        print(f"  总计: {stats['total']} 个模型")
        print(f"  新增: {stats['created']} 个")
        print(f"  更新: {stats['updated']} 个")
        if stats["failed"] > 0:
            print(f"  失败: {stats['failed']} 个")
        return True

    except Exception as e:
        print(f"❌ 模型同步失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description="GaiaRouter 统一初始化脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用默认配置初始化
  python scripts/init.py

  # 自定义管理员账号
  python scripts/init.py --admin-username myadmin --admin-password mypass123

  # 同时同步模型
  python scripts/init.py --sync-models

  # 仅创建管理员（跳过迁移）
  python scripts/init.py --skip-migrations
        """,
    )

    parser.add_argument("--admin-username", default="admin", help="管理员用户名 (默认: admin)")
    parser.add_argument("--admin-password", default="admin123", help="管理员密码 (默认: admin123)")
    parser.add_argument("--skip-migrations", action="store_true", help="跳过数据库迁移")
    parser.add_argument("--skip-admin", action="store_true", help="跳过创建管理员用户")
    parser.add_argument("--sync-models", action="store_true", help="同步 OpenRouter 模型列表")

    args = parser.parse_args()

    # 打印标题
    print_header("GaiaRouter 初始化")
    print("\n此脚本将帮助你完成以下初始化步骤:")
    print("  1. 检查环境配置")
    print("  2. 运行数据库迁移")
    print("  3. 创建管理员用户")
    if args.sync_models:
        print("  4. 同步 OpenRouter 模型")

    # Step 1: 检查环境
    print_step(1, "检查环境配置")
    if not check_env_file():
        sys.exit(1)

    # Step 2: 运行迁移
    if not args.skip_migrations:
        print_step(2, "运行数据库迁移")
        if not run_migrations():
            print("\n⚠️  数据库迁移失败，请检查:")
            print("  - 数据库服务是否运行")
            print("  - .env 中的数据库配置是否正确")
            print("  - 数据库用户是否有足够的权限")
            sys.exit(1)
    else:
        print_step(2, "跳过数据库迁移")
        print("⚠️  已跳过")

    # Step 3: 创建管理员
    if not args.skip_admin:
        print_step(3, "创建管理员用户")
        if not create_admin_user(args.admin_username, args.admin_password):
            sys.exit(1)
    else:
        print_step(3, "跳过创建管理员")
        print("⚠️  已跳过")

    # Step 4: 同步模型（可选）
    if args.sync_models:
        print_step(4, "同步 OpenRouter 模型")
        import asyncio

        if not asyncio.run(sync_openrouter_models()):
            print("\n⚠️  模型同步失败，但初始化已完成")
            print("  你可以稍后在管理后台手动同步模型")

    # 完成
    print_header("✓ 初始化完成！")

    print("\n📝 初始化摘要:")
    print(f"  - 数据库: {'✓ 已迁移' if not args.skip_migrations else '⊘ 已跳过'}")
    print(f"  - 管理员: {'✓ ' + args.admin_username if not args.skip_admin else '⊘ 已跳过'}")
    print(f"  - 模型同步: {'✓ 已完成' if args.sync_models else '⊘ 未执行'}")

    print("\n🚀 下一步:")
    print("  1. 启动后端服务:")
    print("     python -m uvicorn src.gaiarouter.main:app --reload")
    print("\n  2. 启动前端服务:")
    print("     cd frontend && npm run dev")
    print("\n  3. 访问管理后台:")
    print("     http://localhost:3000")

    if not args.skip_admin:
        print("\n  4. 使用管理员账号登录:")
        print(f"     用户名: {args.admin_username}")
        print(f"     密码: {args.admin_password}")
        if args.admin_password == "admin123":
            print("\n     ⚠️  安全提示: 请在登录后修改默认密码！")

    print("\n📚 查看文档:")
    print("  - 初始化指南: INITIALIZATION_GUIDE.md")
    print("  - API 文档: http://localhost:8000/docs")
    print()


if __name__ == "__main__":
    main()
