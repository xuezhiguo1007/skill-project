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
sys.path.insert(0, str(Path(__file__).parent.parent))

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
        # 构建prompt（优化版：明确要求输出完整报告）
        if prompt is None:
            matchup_str = "\n".join(matchups)
            prompt = (
                f"请预测以下世界杯对阵的比分：\n{matchup_str}\n\n"
                "**重要要求：**\n"
                "1. **必须输出完整的预测报告，不要只返回简短总结！**\n"
                "2. 必须包含「预测汇总表」章节，格式如下：\n"
                "| 对阵 | 推荐比分 | 胜负平倾向 | 主胜概率 | 平局概率 | 客胜概率 | 预测信心 |\n"
                "|------|----------|------------|----------|----------|----------|----------|\n"
                "| 科特迪瓦 vs 挪威 | **1-2** | 客胜 | 22-25% | 30-32% | 45-55% | ⭐⭐⭐ |\n\n"
                "3. 每场对阵必须给出明确比分（如 2-1、1-1、3-0），不要使用模糊表述\n"
                "4. 必须包含胜负平倾向（主胜/客胜/平局）和概率区间（如 主胜65-75%）\n"
                "5. 基于FIFA排名、历史战绩、球员状态等核心变量进行分析\n"
                "6. 如果无法搜索最新数据，请基于你的足球知识库进行分析，不要跳过\n"
                "7. 使用中文 Markdown 格式输出\n\n"
                "**输出结构示例：**\n"
                "# 🏆 世界杯足球比分预测报告\n\n"
                "## 对阵一：科特迪瓦 vs 挪威\n"
                "### 一、基础参考研判\n"
                "...（FIFA排名、历史战绩等）\n"
                "### 四、预测比分\n"
                "**📌 最终推荐比分：1-2（挪威胜）**\n\n"
                "---\n\n"
                "## 📊 预测汇总表\n"
                "| 对阵 | 推荐比分 | 胜负平倾向 | 主胜概率 | 平局概率 | 客胜概率 | 预测信心 |\n"
                "...（所有对阵）\n\n"
                "**再次强调：必须输出完整的预测报告和汇总表，不要只返回简短总结！**"
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
        解析预测结果（改进版）

        Args:
            response: 模型响应文本
            matchups: 对阵列表

        Returns:
            解析后的预测字典
        """
        import re

        predictions = {}

        # 策略1: 优先解析预测汇总表（结构化数据）
        table_data = self._parse_summary_table(response)

        # 策略2: 如果汇总表解析失败，按对阵章节解析
        if not table_data:
            table_data = self._parse_by_sections(response, matchups)

        # 组装最终结果
        for matchup in matchups:
            pred_info = {
                "matchup": matchup,
                "predicted_score": None,
                "tendency": None,
                "probability_range": None,
                "confidence": None,
                "raw_response": response,
            }

            # 从解析结果中提取
            if matchup in table_data:
                pred_info.update(table_data[matchup])

            predictions[matchup] = pred_info

        return predictions

    def _parse_summary_table(self, response: str) -> dict[str, dict[str, Any]]:
        """
        解析预测汇总表（优先策略）

        格式示例：
        | 对阵 | 推荐比分 | 胜负平倾向 | 主胜概率 | 平局概率 | 客胜概率 | 预测信心 |
        | 科特迪瓦 vs 挪威 | **1-2** | 客胜 | 22-25% | 30-32% | 45-55% | ⭐⭐⭐ |

        Args:
            response: 响应文本

        Returns:
            解析结果字典
        """
        import re

        table_data = {}

        # 匹配汇总表标题
        table_header_pattern = r"## 📊 预测汇总表"
        if not re.search(table_header_pattern, response):
            return {}

        # 匹配表格行（支持 **比分** 加粗格式）
        # 格式: | 对阵 | **比分** | 倾向 | 主胜% | 平局% | 客胜% | 信心 |
        row_pattern = r"\|\s*([^|]+?)\s*\|\s*\*{0,2}([^*|]+?)\*{0,2}\s*\|\s*(\w+)\s*\|\s*([\d-]+%)\s*\|\s*([\d-]+%)\s*\|\s*([\d-]+%)\s*\|\s*(⭐+)\s*\|"

        matches = re.findall(row_pattern, response)

        for match in matches:
            matchup, score, tendency, home_prob, draw_prob, away_prob, confidence = match

            # 清理对阵名称（去除多余空格）
            matchup = matchup.strip()

            # 组合概率区间
            probability_range = f"主胜{home_prob}|平局{draw_prob}|客胜{away_prob}"

            table_data[matchup] = {
                "predicted_score": score.strip(),
                "tendency": tendency.strip(),
                "probability_range": probability_range,
                "confidence": confidence.strip(),
            }

        return table_data

    def _parse_by_sections(self, response: str, matchups: list[str]) -> dict[str, dict[str, Any]]:
        """
        按对阵章节解析（备用策略）

        格式示例：
        ## 对阵一：科特迪瓦 vs 挪威
        ...
        **📌 最终推荐比分：1-2（挪威胜）**

        Args:
            response: 响应文本
            matchups: 对阵列表

        Returns:
            解析结果字典
        """
        import re

        section_data = {}

        for matchup in matchups:
            # 找到该对阵的章节（支持"对阵一："、"对阵二："等标题）
            # 使用模糊匹配：找到包含对阵名称的标题行到下一个 "---" 之间的内容
            section_pattern = rf"## 对阵[^:]*[：:]\s*{re.escape(matchup)}.*?---"
            section_match = re.search(section_pattern, response, re.DOTALL | re.IGNORECASE)

            if not section_match:
                continue

            section_text = section_match.group(0)

            # 在章节内解析比分
            # 格式1: **📌 最终推荐比分：1-2（挪威胜）**
            # 格式2: **📌 最终推荐比分：1-2**
            score_pattern = r"\*{0,2}📌\s*最终推荐比分[：:]([^*（\n]+)"
            score_match = re.search(score_pattern, section_text)

            if score_match:
                score = score_match.group(1).strip()
                # 清理括号内容（如 "(挪威胜)"）
                score = re.sub(r"\（[^）]+\）", "", score).strip()
                score = re.sub(r"\([^)]+\)", "", score).strip()

                section_data[matchup] = {
                    "predicted_score": score,
                }

            # 解析胜负倾向（从分层概率预测表格）
            # 格式: | **平衡型** | 客胜倾向 | 主胜25%-平局30%-客胜45% |
            tendency_pattern = r"\|\s*\*{0,2}平衡型\*{0,2}\s*\|\s*(\w+)\s*\|\s*主胜([\d-]+%)-平局([\d-]+%)-客胜([\d-]+%)\s*\|"
            tendency_match = re.search(tendency_pattern, section_text)

            if tendency_match:
                tendency = tendency_match.group(1)
                home_prob = tendency_match.group(2)
                draw_prob = tendency_match.group(3)
                away_prob = tendency_match.group(4)

                probability_range = f"主胜{home_prob}|平局{draw_prob}|客胜{away_prob}"

                if matchup in section_data:
                    section_data[matchup].update({
                        "tendency": tendency,
                        "probability_range": probability_range,
                    })
                else:
                    section_data[matchup] = {
                        "tendency": tendency,
                        "probability_range": probability_range,
                    }

        return section_data

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
        help="对阵列表，如：'巴西 vs 日本' '德国 vs 巴拉圭' '荷兰 vs 摩洛哥'",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="glm-5-no-think-fast",
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