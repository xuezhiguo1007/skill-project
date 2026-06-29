#!/usr/bin/env python3
"""
世界杯预测结果对比与Skill优化脚本

功能：
1. 对比预测结果与真实比赛结果
2. 计算预测准确率
3. 分析失败案例，提取优化信号
4. 自动生成skill优化建议
5. 更新SKILL.md或reference-guide.md
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from skill_project.llm import create_chat_model


class WorldCupPredictionEvaluator:
    """世界杯预测评估器"""

    def __init__(
        self,
        prediction_dir: str = "generated_skills/worldcup/predictions",
        result_dir: str = "generated_skills/worldcup/results",
        evolution_dir: str = "generated_skills/worldcup/evolution",
    ):
        self.prediction_dir = Path(prediction_dir)
        self.result_dir = Path(result_dir)
        self.evolution_dir = Path(evolution_dir)

        # 创建目录
        for dir_path in [self.prediction_dir, self.result_dir, self.evolution_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

    def record_actual_result(
        self,
        matchup: str,
        actual_score: str,
        match_date: str | None = None,
        notes: str | None = None,
    ) -> dict[str, Any]:
        """
        记录真实比赛结果

        Args:
            matchup: 对阵名称，如 "巴西 vs 阿根廷"
            actual_score: 实际比分，如 "2-1"
            match_date: 比赛日期（可选）
            notes: 备注（可选）

        Returns:
            结果记录字典
        """
        # 查找对应的预测记录
        prediction_record = self._find_prediction_for_matchup(matchup)

        result_data = {
            "timestamp": datetime.now().isoformat(),
            "matchup": matchup,
            "actual_score": actual_score,
            "match_date": match_date,
            "notes": notes,
            "prediction_record": prediction_record,
        }

        # 计算预测准确性
        if prediction_record:
            predicted_score = prediction_record["predictions"].get(matchup, {}).get(
                "predicted_score"
            )
            if predicted_score:
                result_data["prediction_score"] = predicted_score
                result_data["accuracy"] = self._calculate_accuracy(
                    predicted_score, actual_score
                )

        # 保存结果
        result_file = self._save_result(result_data)

        # 更新预测记录状态
        if prediction_record:
            self._update_prediction_status(prediction_record, "verified")

        print(f"\n✅ 真实结果已记录！")
        print(f"对阵: {matchup}")
        print(f"实际比分: {actual_score}")
        print(f"预测比分: {result_data.get('prediction_score', '未预测')}")
        print(f"准确度: {result_data.get('accuracy', '无法计算')}")
        print(f"结果文件: {result_file}")

        return result_data

    def _find_prediction_for_matchup(self, matchup: str) -> dict[str, Any] | None:
        """
        查找包含指定对阵的最新预测记录

        Args:
            matchup: 对阵名称

        Returns:
            预测记录字典或None
        """
        pending_predictions = []
        for filepath in sorted(
            self.prediction_dir.glob("prediction_*.json"), reverse=True
        ):
            with open(filepath, encoding="utf-8") as f:
                record = json.load(f)
                if matchup in record.get("matchups", []) and record.get("status") == "pending":
                    pending_predictions.append(record)

        return pending_predictions[0] if pending_predictions else None

    def _calculate_accuracy(self, predicted_score: str, actual_score: str) -> str:
        """
        计算预测准确度

        Args:
            predicted_score: 预测比分
            actual_score: 实际比分

        Returns:
            准确度评级
        """
        # 清理比分字符串
        predicted_score = predicted_score.strip()
        actual_score = actual_score.strip()

        # 处理多比分预测（如 "2-1 或 1-1")
        predicted_scores = predicted_score.split("或")
        predicted_scores = [s.strip() for s in predicted_scores]

        # 完全匹配
        if actual_score in predicted_scores:
            return "exact_match"

        # 解析比分数字
        try:
            actual_parts = actual_score.split("-")
            actual_home, actual_away = int(actual_parts[0]), int(actual_parts[1])

            for pred in predicted_scores:
                pred_parts = pred.split("-")
                pred_home, pred_away = int(pred_parts[0]), int(pred_parts[1])

                # 胜负方向正确
                actual_result = (
                    "win" if actual_home > actual_away
                    else "loss" if actual_home < actual_away
                    else "draw"
                )
                pred_result = (
                    "win" if pred_home > pred_away
                    else "loss" if pred_home < pred_away
                    else "draw"
                )

                if actual_result == pred_result:
                    # 进球数差距
                    goal_diff = abs((actual_home + actual_away) - (pred_home + pred_away))
                    if goal_diff <= 1:
                        return "tendency_match"
                    elif goal_diff <= 2:
                        return "rough_match"

            return "wrong_prediction"

        except (ValueError, IndexError):
            return "parse_error"

    def _save_result(self, result_data: dict[str, Any]) -> Path:
        """
        保存结果记录

        Args:
            result_data: 结果数据

        Returns:
            文件路径
        """
        timestamp = datetime.fromisoformat(result_data["timestamp"])
        filename = f"result_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.result_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)

        return filepath

    def _update_prediction_status(self, prediction_record: dict[str, Any], status: str):
        """
        更新预测记录状态

        Args:
            prediction_record: 预测记录
            status: 新状态
        """
        timestamp = prediction_record["timestamp"]
        prediction_file = self.prediction_dir / f"prediction_{timestamp.replace(':', '').replace('.', '')[:15]}.json"

        if prediction_file.exists():
            with open(prediction_file, encoding="utf-8") as f:
                record = json.load(f)
            record["status"] = status
            with open(prediction_file, "w", encoding="utf-8") as f:
                json.dump(record, f, ensure_ascii=False, indent=2)

    def analyze_performance(self) -> dict[str, Any]:
        """
        分析整体预测性能

        Returns:
            性能分析结果
        """
        all_results = []
        for filepath in sorted(self.result_dir.glob("result_*.json"), reverse=True):
            with open(filepath, encoding="utf-8") as f:
                all_results.append(json.load(f))

        if not all_results:
            print("\n⚠️  暂无结果记录")
            return {}

        # 统计准确度
        accuracy_stats = {
            "exact_match": 0,
            "tendency_match": 0,
            "rough_match": 0,
            "wrong_prediction": 0,
            "parse_error": 0,
        }

        failed_cases = []

        for result in all_results:
            accuracy = result.get("accuracy", "parse_error")
            accuracy_stats[accuracy] += 1

            if accuracy in ["wrong_prediction", "parse_error"]:
                failed_cases.append(
                    {
                        "matchup": result["matchup"],
                        "predicted": result.get("prediction_score", "未预测"),
                        "actual": result["actual_score"],
                        "notes": result.get("notes", ""),
                    }
                )

        total = len(all_results)
        exact_match_rate = accuracy_stats["exact_match"] / total * 100 if total > 0 else 0
        tendency_match_rate = (accuracy_stats["exact_match"] + accuracy_stats["tendency_match"]) / total * 100 if total > 0 else 0

        performance_data = {
            "timestamp": datetime.now().isoformat(),
            "total_predictions": total,
            "accuracy_stats": accuracy_stats,
            "exact_match_rate": round(exact_match_rate, 2),
            "tendency_match_rate": round(tendency_match_rate, 2),
            "failed_cases": failed_cases,
        }

        # 保存性能分析
        analysis_file = self.evolution_dir / f"performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(analysis_file, "w", encoding="utf-8") as f:
            json.dump(performance_data, f, ensure_ascii=False, indent=2)

        print(f"\n📊 预测性能分析报告")
        print(f"总预测数: {total}")
        print(f"完全准确: {accuracy_stats['exact_match']} ({exact_match_rate:.1f}%)")
        print(f"胜负方向正确: {accuracy_stats['tendency_match']} ({tendency_match_rate:.1f}%)")
        print(f"粗略正确: {accuracy_stats['rough_match']}")
        print(f"预测错误: {accuracy_stats['wrong_prediction']}")
        print(f"解析错误: {accuracy_stats['parse_error']}")

        if failed_cases:
            print(f"\n❌ 失败案例:")
            for case in failed_cases:
                print(f"  - {case['matchup']}: 预测{case['predicted']}, 实际{case['actual']}")

        return performance_data

    def generate_optimization_suggestions(self, performance_data: dict[str, Any]) -> str:
        """
        基于性能分析生成优化建议

        Args:
            performance_data: 性能分析数据

        Returns:
            优化建议文本
        """
        if not performance_data:
            return ""

        model = create_chat_model()

        failed_cases = performance_data.get("failed_cases", [])
        accuracy_stats = performance_data.get("accuracy_stats", {})
        exact_match_rate = performance_data.get("exact_match_rate", 0)
        tendency_match_rate = performance_data.get("tendency_match_rate", 0)

        optimization_prompt = (
            "你是一个世界杯足球预测系统优化专家。\n"
            "请基于以下预测失败案例和性能数据，生成具体的skill优化建议。\n\n"
            f"当前预测准确率：\n"
            f"- 完全准确率: {exact_match_rate}%\n"
            f"- 胜负方向准确率: {tendency_match_rate}%\n\n"
            f"失败案例：\n"
            f"{json.dumps(failed_cases, ensure_ascii=False, indent=2)}\n\n"
            f"准确度统计：\n"
            f"{json.dumps(accuracy_stats, ensure_ascii=False, indent=2)}\n\n"
            "请从以下维度生成优化建议：\n"
            "1. 预测逻辑调整（如是否过度依赖排名、是否忽视某些变量）\n"
            "2. 数据源补充（如需要添加哪些新的参考数据）\n"
            "3. 输出格式优化（如是否需要调整输出结构以提高解析准确性）\n"
            "4. 核心变量权重调整（如FIFA排名、历史交锋、球员状态等的权重）\n"
            "5. 新规则补充（如针对特定场景的预测规则）\n\n"
            "输出格式：使用Markdown，包含以下章节：\n"
            "- # 性能问题诊断\n"
            "- # 核心优化建议\n"
            "- # 具体改进措施\n"
            "- # SKILL.md更新建议\n"
            "- # reference-guide.md更新建议\n"
        )

        print("\n🔄 正在生成优化建议...")
        response = model.invoke([{"role": "user", "content": optimization_prompt}])

        suggestions = response.content
        suggestions_file = self.evolution_dir / f"suggestions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        with open(suggestions_file, "w", encoding="utf-8") as f:
            f.write(suggestions)

        print(f"\n✅ 优化建议已生成！")
        print(f"建议文件: {suggestions_file}")
        print(f"\n{suggestions}")

        return suggestions

    def apply_skill_evolution(self, suggestions: str) -> bool:
        """
        应用skill进化（自动或半自动更新SKILL.md）

        Args:
            suggestions: 优化建议文本

        Returns:
            是否成功应用
        """
        print("\n🤖 是否要自动应用这些优化建议？")
        print("请选择：")
        print("1. 自动更新SKILL.md")
        print("2. 自动更新reference-guide.md")
        print("3. 同时更新两个文件")
        print("4. 手动查看建议，暂不更新")
        print("5. 退出")

        choice = input("\n请输入选择 (1-5): ").strip()

        skill_file = Path("skills/worldcup-prediction/SKILL.md")
        reference_file = Path("data/worldcup/reference-guide.md")

        if choice == "1":
            return self._update_skill_file(skill_file, suggestions)
        elif choice == "2":
            return self._update_skill_file(reference_file, suggestions)
        elif choice == "3":
            success1 = self._update_skill_file(skill_file, suggestions)
            success2 = self._update_skill_file(reference_file, suggestions)
            return success1 and success2
        elif choice == "4":
            print("\n请手动查看优化建议文件并决定如何更新skill。")
            return False
        else:
            print("\n已退出。")
            return False

    def _update_skill_file(self, filepath: Path, suggestions: str) -> bool:
        """
        更新skill文件

        Args:
            filepath: 文件路径
            suggestions: 优化建议

        Returns:
            是否成功
        """
        if not filepath.exists():
            print(f"\n⚠️  文件不存在: {filepath}")
            return False

        # 读取当前内容
        with open(filepath, encoding="utf-8") as f:
            current_content = f.read()

        # 使用模型生成更新内容
        model = create_chat_model()

        update_prompt = (
            f"请基于以下优化建议，更新skill文件内容。\n\n"
            f"当前文件内容：\n{current_content}\n\n"
            f"优化建议：\n{suggestions}\n\n"
            "请输出更新后的完整文件内容（保持原有frontmatter和基本结构，只修改需要优化的部分）。"
        )

        print(f"\n🔄 正在更新文件: {filepath}")
        response = model.invoke([{"role": "user", "content": update_prompt}])

        new_content = response.content

        # 保存更新
        backup_file = filepath.parent / f"{filepath.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(backup_file, "w", encoding="utf-8") as f:
            f.write(current_content)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)

        print(f"\n✅ 文件已更新！")
        print(f"备份文件: {backup_file}")
        print(f"更新文件: {filepath}")

        return True


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="世界杯预测结果对比与优化脚本")
    parser.add_argument(
        "--record-result",
        nargs=2,
        metavar=("MATCHUP", "SCORE"),
        help="记录真实比赛结果，如：'巴西 vs 阿根廷' '2-1'",
    )
    parser.add_argument(
        "--match-date",
        default=None,
        help="比赛日期（可选）",
    )
    parser.add_argument(
        "--notes",
        default=None,
        help="备注（可选）",
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="分析预测性能",
    )
    parser.add_argument(
        "--optimize",
        action="store_true",
        help="生成优化建议",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="应用优化建议（需要先执行--optimize）",
    )

    args = parser.parse_args()

    evaluator = WorldCupPredictionEvaluator()

    if args.record_result:
        matchup, actual_score = args.record_result
        evaluator.record_actual_result(
            matchup=matchup,
            actual_score=actual_score,
            match_date=args.match_date,
            notes=args.notes,
        )
        return

    if args.analyze:
        performance_data = evaluator.analyze_performance()

        if args.optimize and performance_data:
            suggestions = evaluator.generate_optimization_suggestions(performance_data)

            if args.apply:
                evaluator.apply_skill_evolution(suggestions)
        return

    # 默认：分析 + 优化
    performance_data = evaluator.analyze_performance()
    if performance_data:
        suggestions = evaluator.generate_optimization_suggestions(performance_data)
        evaluator.apply_skill_evolution(suggestions)


if __name__ == "__main__":
    main()