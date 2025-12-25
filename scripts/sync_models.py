#!/usr/bin/env python3
"""
同步 OpenRouter 模型到数据库

使用方法:
    python scripts/sync_models.py
"""

import sys
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.gaiarouter.models.sync import sync_models_from_openrouter
from src.gaiarouter.config import get_settings


async def main():
    """主函数"""
    print("="*60)
    print("OpenRouter 模型同步工具")
    print("="*60)

    # 检查配置
    settings = get_settings()
    if not settings.providers.openrouter_api_key:
        print("\n❌ 错误: 未配置 OPENROUTER_API_KEY")
        print("请在 .env 文件中添加:")
        print("  OPENROUTER_API_KEY=sk-or-your-api-key")
        sys.exit(1)

    print("\n✓ 检测到 OpenRouter API Key")
    print("\n🔄 开始同步模型...")

    try:
        stats = await sync_models_from_openrouter()

        print("\n" + "="*60)
        print("✓ 同步完成！")
        print("="*60)
        print(f"  总模型数: {stats['total']}")
        print(f"  新增: {stats['created']}")
        print(f"  更新: {stats['updated']}")
        print(f"  失败: {stats['failed']}")
        print("\n提示: 访问管理后台的模型管理页面启用需要的模型")

    except Exception as e:
        print(f"\n❌ 同步失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
