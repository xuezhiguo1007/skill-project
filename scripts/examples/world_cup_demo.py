#!/usr/bin/env python3
"""
世界杯预测系统 - 完整演示脚本

演示从预测到优化的完整流程
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from predict_and_record import WorldCupPredictionRecorder
from compare_and_evolve import WorldCupPredictionEvaluator


def demo_prediction():
    """演示预测功能"""
    print("=" * 60)
    print("1. 世界杯比分预测演示")
    print("=" * 60)

    recorder = WorldCupPredictionRecorder()

    # 执行预测
    matchups = ["科特迪瓦 vs 挪威", "法国 vs 瑞典", "墨西哥 vs 厄瓜多尔"]
    prediction_data = recorder.predict_and_record(
        matchups=matchups,
        model_name="glm-5-no-think-fast",
    )

    print("\n预测完成！")
    print(f"预测结果数: {len(prediction_data['predictions'])}")
    return prediction_data


def demo_evaluation():
    """演示评估功能"""
    print("\n" + "=" * 60)
    print("2. 预测评估演示")
    print("=" * 60)

    evaluator = WorldCupPredictionEvaluator()

    # 记录真实结果（示例）
    print("\n记录真实比赛结果...")
    print("（演示用，实际使用时请取消注释）")

    # evaluator.record_actual_result(
    #     matchup="科特迪瓦 vs 挪威",
    #     actual_score="2-1",
    #     match_date="2026-06-30",
    #     notes="科特迪瓦表现出色，进攻效率高"
    # )

    # 分析性能
    print("\n分析预测性能...")
    performance_data = evaluator.analyze_performance()

    if performance_data:
        print(f"总预测数: {performance_data.get('total_predictions', 0)}")
        print(f"已验证数: {performance_data.get('verified_predictions', 0)}")

        # 生成优化建议
        suggestions = evaluator.generate_optimization_suggestions(performance_data)
        if suggestions:
            print(f"\n生成了 {len(suggestions)} 条优化建议")
    else:
        print("\n暂无预测数据可供分析")


if __name__ == "__main__":
    # 运行演示
    demo_prediction()
    demo_evaluation()

    print("\n" + "=" * 60)
    print("演示完成！")
    print("查看 scripts/README.md 了解更多用法")
    print("=" * 60)