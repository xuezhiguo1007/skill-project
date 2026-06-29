#!/usr/bin/env python3
"""
世界杯比分预测记录脚本

功能：
1. 执行世界杯比分预测
2. 记录预测结果到JSON文件
3. 生成预测报告
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from skill_project.services.skill_service import run_validation
from skill_project.core.config import SETTINGS


class WorldCupPredictionRecorder:
    """世界杯预测记录器"""

    def __init__(self, record_dir: str = "generated_skills/worldcup/predictions"):
        self.record_dir = Path(record_dir)
        self.record_dir.mkdir(parents=True, exist_ok=True)

    def predict_and_record(
        self,
        matchups: list[str],
        model_name: str | None = None,
        prompt: str | None = None,
    ) -> dict[str, Any]:
        """
        执行预测并记录结果

        Args:
            matchups: 对阵列表，如 ["巴西 vs 阿根廷", "法国 vs 德国"]
            model_name: 使用的模型名称
            prompt: 自定义prompt（可选）

        Returns:
            预测结果字典
        """
        # 构建prompt
        if prompt is None:
            matchup_str = "\n".join(matchups)
            prompt = (
                f"请预测以下世界杯对阵的比分：\n{matchup_str}\n"
                "请读取 data/worldcup/reference-guide.md，"
                "基于FIFA排名、历史战绩、球员状态等核心变量进行分层概率分析。"
                "每场对阵输出明确的预测比分，并给出胜负平倾向和概率区间。"
                "输出必须使用中文 Markdown，并严格遵循对应 skill 中要求的结构。"
            )

        # 执行预测
        print(f"正在执行预测，使用模型: {model_name or SETTINGS.default_model}")
        print(f"对阵列表: {matchups}")

        result = run_validation(
            prompt=prompt,
            model_name=model_name,
        )

        # 解析预测结果
        predictions = self._parse_predictions(result["response"], matchups)

        # 构建记录数据
        record_data = {
            "timestamp": datetime.now().isoformat(),
            "model": model_name or SETTINGS.default_model,
            "matchups": matchups,
            "prompt": prompt,
            "response": result["response"],
            "predictions": predictions,
            "status": "pending",  # pending -> verified
        }

        # 保存记录
        record_file = self._save_record(record_data)

        print(f"\n✅ 预测完成！")
        print(f"记录文件: {record_file}")
        print(f"\n预测结果摘要:")
        for matchup, pred in predictions.items():
            print(f"  {matchup}: {pred['predicted_score']} ({pred['tendency']})")

        return record_data

    def _parse_predictions(
        self, response: str, matchups: list[str]
    ) -> dict[str, dict[str, Any]]:
        """
        解析预测结果

        Args:
            response: 模型响应文本
            matchups: 对阵列表

        Returns:
            解析后的预测字典
        """
        predictions = {}

        for matchup in matchups:
            # 提取该对阵的预测信息
            # 简化解析：通过正则或字符串匹配提取比分
            pred_info = {
                "matchup": matchup,
                "predicted_score": None,
                "tendency": None,
                "probability_range": None,
                "confidence": None,
                "raw_response": response,
            }

            # 尝试从响应中提取比分
            # 格式可能是: "预测比分：2-1" 或 "| 巴西 vs 阿根廷 | 2-1 |"
            import re

            # 匹配比分模式 (如 2-1, 1-1, 0-0等)
            score_pattern = r"预测比分[：:]\s*(\d+-\d+|\d+-\d+\s*或\s*\d+-\d+)"
            score_match = re.search(score_pattern, response)
            if score_match:
                pred_info["predicted_score"] = score_match.group(1).strip()

            # 匹配胜负倾向
            tendency_pattern = r"胜负平倾向[：:]\s*(主胜|客胜|平局|巴西胜|阿根廷胜)"
            tendency_match = re.search(tendency_pattern, response)
            if tendency_match:
                pred_info["tendency"] = tendency_match.group(1).strip()

            # 匹配概率区间
            prob_pattern = r"概率区间[：:]\s*(\d+%-?\d+%)"
            prob_match = re.search(prob_pattern, response)
            if prob_match:
                pred_info["probability_range"] = prob_match.group(1).strip()

            predictions[matchup] = pred_info

        return predictions

    def _save_record(self, record_data: dict[str, Any]) -> Path:
        """
        保存预测记录到JSON文件

        Args:
            record_data: 预测记录数据

        Returns:
            保存的文件路径
        """
        timestamp = datetime.fromisoformat(record_data["timestamp"])
        filename = f"prediction_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.record_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(record_data, f, ensure_ascii=False, indent=2)

        return filepath

    def list_predictions(self) -> list[dict[str, Any]]:
        """
        列出所有预测记录

        Returns:
            预测记录列表
        """
        records = []
        for filepath in sorted(self.record_dir.glob("prediction_*.json"), reverse=True):
            with open(filepath, encoding="utf-8") as f:
                records.append(json.load(f))
        return records

    def get_pending_predictions(self) -> list[dict[str, Any]]:
        """
        获取待验证的预测记录

        Returns:
            待验证的预测记录列表
        """
        return [r for r in self.list_predictions() if r["status"] == "pending"]


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="世界杯比分预测记录脚本")
    parser.add_argument(
        "--matchups",
        nargs="+",
        required=True,
        help="对阵列表，如：'巴西 vs 阿根廷' '法国 vs 德国'",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="使用的模型名称（默认使用配置文件中的模型）",
    )
    parser.add_argument(
        "--prompt",
        default=None,
        help="自定义预测prompt（可选）",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="列出所有预测记录",
    )
    parser.add_argument(
        "--pending",
        action="store_true",
        help="列出待验证的预测记录",
    )

    args = parser.parse_args()

    recorder = WorldCupPredictionRecorder()

    if args.list:
        records = recorder.list_predictions()
        print(f"\n历史预测记录（共 {len(records)} 条）：")
        for i, record in enumerate(records, 1):
            print(f"\n{i}. {record['timestamp']}")
            print(f"   模型: {record['model']}")
            print(f"   对阵: {', '.join(record['matchups'])}")
            print(f"   状态: {record['status']}")
        return

    if args.pending:
        records = recorder.get_pending_predictions()
        print(f"\n待验证预测记录（共 {len(records)} 条）：")
        for i, record in enumerate(records, 1):
            print(f"\n{i}. {record['timestamp']}")
            print(f"   对阵: {', '.join(record['matchups'])}")
            for matchup, pred in record["predictions"].items():
                print(f"   - {matchup}: {pred['predicted_score']}")
        return

    # 执行预测
    record = recorder.predict_and_record(
        matchups=args.matchups,
        model_name=args.model,
        prompt=args.prompt,
    )


if __name__ == "__main__":
    main()