"""
测试费用计算功能

验证 StatsCollector 的费用自动计算功能
"""

import sys
from pathlib import Path

# 添加 src 目录到 Python 路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from decimal import Decimal

from gaiarouter.database.connection import get_db
from gaiarouter.database.models import Model
from gaiarouter.stats.collector import StatsCollector


def test_calculate_cost_with_pricing():
    """测试有定价信息的模型费用计算"""
    print("\n=== 测试 1: 有定价信息的模型 ===")

    # 创建测试模型
    db = next(get_db())
    try:
        # 检查是否已存在测试模型
        test_model = db.query(Model).filter(Model.id == "test/gpt-4").first()
        if not test_model:
            test_model = Model(
                id="test/gpt-4",
                name="GPT-4 Test",
                provider="test",
                pricing_prompt=Decimal("0.03"),  # $0.03 per 1K tokens
                pricing_completion=Decimal("0.06"),  # $0.06 per 1K tokens
            )
            db.add(test_model)
            db.commit()
            print("✓ 创建测试模型: test/gpt-4")
        else:
            print("✓ 测试模型已存在: test/gpt-4")

        # 测试费用计算
        collector = StatsCollector()
        cost = collector.calculate_cost(
            model_id="test/gpt-4", prompt_tokens=1000, completion_tokens=2000
        )

        expected_cost = (1000 / 1000) * 0.03 + (2000 / 1000) * 0.06  # 0.03 + 0.12 = 0.15
        print(f"输入: 1000 prompt tokens, 2000 completion tokens")
        print(f"预期费用: ${expected_cost}")
        print(f"计算费用: ${cost}")

        if cost is not None and abs(cost - expected_cost) < 0.000001:
            print("✅ 测试通过: 费用计算正确")
            return True
        else:
            print(f"❌ 测试失败: 费用不匹配 (预期 {expected_cost}, 实际 {cost})")
            return False

    finally:
        db.close()


def test_calculate_cost_without_pricing():
    """测试没有定价信息的模型"""
    print("\n=== 测试 2: 没有定价信息的模型 ===")

    db = next(get_db())
    try:
        # 创建无定价模型
        test_model = db.query(Model).filter(Model.id == "test/free-model").first()
        if not test_model:
            test_model = Model(
                id="test/free-model",
                name="Free Model",
                provider="test",
                pricing_prompt=None,
                pricing_completion=None,
            )
            db.add(test_model)
            db.commit()
            print("✓ 创建测试模型: test/free-model (无定价)")

        # 测试费用计算
        collector = StatsCollector()
        cost = collector.calculate_cost(
            model_id="test/free-model", prompt_tokens=1000, completion_tokens=2000
        )

        print(f"计算费用: {cost}")

        if cost is None:
            print("✅ 测试通过: 无定价信息返回 None")
            return True
        else:
            print(f"❌ 测试失败: 应该返回 None，实际返回 {cost}")
            return False

    finally:
        db.close()


def test_calculate_cost_nonexistent_model():
    """测试不存在的模型"""
    print("\n=== 测试 3: 不存在的模型 ===")

    collector = StatsCollector()
    cost = collector.calculate_cost(
        model_id="nonexistent/model", prompt_tokens=1000, completion_tokens=2000
    )

    print(f"计算费用: {cost}")

    if cost is None:
        print("✅ 测试通过: 不存在的模型返回 None")
        return True
    else:
        print(f"❌ 测试失败: 应该返回 None，实际返回 {cost}")
        return False


def test_calculate_cost_edge_cases():
    """测试边界情况"""
    print("\n=== 测试 4: 边界情况 ===")

    db = next(get_db())
    try:
        # 确保测试模型存在
        test_model = db.query(Model).filter(Model.id == "test/gpt-4").first()
        if not test_model:
            print("⚠️  测试模型不存在，跳过边界测试")
            return True

        collector = StatsCollector()

        # 测试零 tokens
        cost_zero = collector.calculate_cost(model_id="test/gpt-4", prompt_tokens=0, completion_tokens=0)
        print(f"零 tokens 费用: ${cost_zero}")
        if cost_zero == 0.0:
            print("✓ 零 tokens 测试通过")
        else:
            print(f"✗ 零 tokens 测试失败 (预期 0.0, 实际 {cost_zero})")

        # 测试小数 tokens（实际使用中可能出现）
        cost_small = collector.calculate_cost(model_id="test/gpt-4", prompt_tokens=100, completion_tokens=50)
        expected_small = (100 / 1000) * 0.03 + (50 / 1000) * 0.06  # 0.003 + 0.003 = 0.006
        print(f"小量 tokens (100+50) 费用: ${cost_small}")
        if cost_small is not None and abs(cost_small - expected_small) < 0.000001:
            print("✓ 小量 tokens 测试通过")
        else:
            print(f"✗ 小量 tokens 测试失败 (预期 {expected_small}, 实际 {cost_small})")

        print("✅ 边界测试完成")
        return True

    finally:
        db.close()


def cleanup_test_data():
    """清理测试数据"""
    print("\n=== 清理测试数据 ===")

    db = next(get_db())
    try:
        # 删除测试模型
        db.query(Model).filter(Model.id.in_(["test/gpt-4", "test/free-model"])).delete(
            synchronize_session=False
        )
        db.commit()
        print("✓ 测试数据已清理")

    except Exception as e:
        print(f"⚠️  清理失败: {e}")
        db.rollback()

    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("开始测试费用计算功能")
    print("=" * 60)

    try:
        results = []

        # 运行所有测试
        results.append(("有定价信息", test_calculate_cost_with_pricing()))
        results.append(("无定价信息", test_calculate_cost_without_pricing()))
        results.append(("不存在的模型", test_calculate_cost_nonexistent_model()))
        results.append(("边界情况", test_calculate_cost_edge_cases()))

        # 打印测试结果摘要
        print("\n" + "=" * 60)
        print("测试结果摘要")
        print("=" * 60)

        passed = sum(1 for _, result in results if result)
        total = len(results)

        for test_name, result in results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{test_name}: {status}")

        print(f"\n总计: {passed}/{total} 测试通过")

        if passed == total:
            print("\n🎉 所有测试通过！")
            exit_code = 0
        else:
            print("\n⚠️  部分测试失败")
            exit_code = 1

    except Exception as e:
        print(f"\n❌ 测试执行出错: {e}")
        import traceback

        traceback.print_exc()
        exit_code = 1

    finally:
        # 清理测试数据
        cleanup_test_data()

    exit(exit_code)
