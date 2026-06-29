#!/usr/bin/env python3

"""
世界杯预测自进化系统 - 一键运行脚本

功能：
1. 执行预测
2. 记录结果
3. 分析性能
4. 生成优化建议
5. 自动应用优化

支持交互式和自动化两种模式。
"""

import json
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from predict_and_record import WorldCupPredictionRecorder
from compare_and_evolve import WorldCupPredictionEvaluator


def interactive_mode():
    """交互式模式"""
    print("\n" + "=" * 50)
    print("世界杯预测自进化系统 - 交互式模式")
    print("=" * 50 + "\n")

    recorder = WorldCupPredictionRecorder()
    evaluator = WorldCupPredictionEvaluator()

    # 步骤1：输入对阵
    print("步骤1：输入对阵信息")
    print("示例：巴西 vs 阿根廷")
    matchups_input = input("\n请输入对阵（多场用逗号分隔）：").strip()

    if not matchups_input:
        print("未输入对阵，退出。")
        return

    matchups = [m.strip() for m in matchups_input.split(",")]

    # 步骤2：执行预测
    print("\n步骤2：执行预测...")
    prediction_data = recorder.predict_and_record(matchups)

    # 步骤3：等待比赛结束
    print("\n步骤3：记录真实结果")
    print("（模拟场景：假设比赛已结束）")

    for matchup in matchups:
        actual_score = input(f"\n{matchup} 的实际比分（如 2-1）：").strip()
        if actual_score:
            notes = input("备注（可选）：").strip()
            evaluator.record_actual_result(
                matchup=matchup,
                actual_score=actual_score,
                notes=notes,
            )

    # 步骤4：分析性能
    print("\n步骤4：分析预测性能...")
    performance_data = evaluator.analyze_performance()

    if not performance_data:
        print("暂无性能数据。")
        return

    # 步骤5：生成优化建议
    print("\n步骤5：生成优化建议...")
    suggestions = evaluator.generate_optimization_suggestions(performance_data)

    # 步骤6：应用优化
    print("\n步骤6：应用优化建议...")
    evaluator.apply_skill_evolution(suggestions)

    print("\n" + "=" * 50)
    print("✅ 自进化流程完成！")
    print("=" * 50)


def auto_mode(matchups: list[str], actual_scores: dict[str, str] | None = None):
    """
    自动化模式

    Args:
        matchups: 对阵列表
        actual_scores: 实际比分字典（可选）
    """
    print("\n" + "=" * 50)
    print("世界杯预测自进化系统 - 自动化模式")
    print("=" * 50 + "\n")

    recorder = WorldCupPredictionRecorder()
    evaluator = WorldCupPredictionEvaluator()

    # 步骤1：执行预测
    print("步骤1：执行预测...")
    prediction_data = recorder.predict_and_record(matchups)

    # 步骤2：记录真实结果
    if actual_scores:
        print("\n步骤2：记录真实结果...")
        for matchup, actual_score in actual_scores.items():
            evaluator.record_actual_result(
                matchup=matchup,
                actual_score=actual_score,
            )

        # 步骤3：分析性能
        print("\n步骤3：分析预测性能...")
        performance_data = evaluator.analyze_performance()

        # 步骤4：生成优化建议
        print("\n步骤4：生成优化建议...")
        suggestions = evaluator.generate_optimization_suggestions(performance_data)

        # 步骤5：自动应用优化（默认更新两个文件）
        print("\n步骤5：自动应用优化...")
        skill_file = Path("skills/worldcup-prediction/SKILL.md")
        reference_file = Path("data/worldcup/reference-guide.md")

        evaluator._update_skill_file(skill_file, suggestions)
        evaluator._update_skill_file(reference_file, suggestions)

    print("\n" + "=" * 50)
    print("✅ 自动化流程完成！")
    print("=" * 50)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="世界杯预测自进化系统一键运行脚本")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="交互式模式（逐步输入）",
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="自动化模式（需要提供对阵和比分）",
    )
    parser.add_argument(
        "--matchups",
        nargs="+",
        help="对阵列表（自动化模式）",
    )
    parser.add_argument(
        "--scores",
        nargs="+",
        help="实际比分列表（自动化模式，格式：对阵:比分）",
    )

    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
    elif args.auto and args.matchups:
        # 解析比分
        actual_scores = {}
        if args.scores:
            for score_item in args.scores:
                matchup, score = score_item.split(":")
                actual_scores[matchup] = score

        auto_mode(args.matchups, actual_scores)
    else:
        # 默认：交互式模式
        interactive_mode()


if __name__ == "__main__":
    main()