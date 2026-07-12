"""排队时间预测 Skill"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from skill_project.langgraph_skill.models import SkillSpec
from skill_project.hongloumeng_schedule.data_service import DataService
from skill_project.hongloumeng_schedule.models import CrowdData, QueueInfo


def create_queue_prediction_skill() -> SkillSpec:
    """创建排队时间预测的 Skill"""
    content = """
# 排队时间预测

## Description
这个 Skill 负责预测各个剧目的排队时间，基于客流量数据、历史数据和时间段分析，为用户提供最佳的观演时间建议。

## When to Use
当用户需要：
- 了解当前排队时间
- 预测特定时间的排队时长
- 选择排队时间最少的时间段
- 了解客流高峰时段

## Trigger Keywords
- 排队
- 等待
- 多久
- 人多
- 时间
- 高峰
- 拥挤

## Procedure
1. 获取当前客流数据
2. 分析历史排队模式
3. 计算预测排队时间
4. 推荐最佳观演时间段

## Example Queries
- "现在排队要多长时间？"
- "什么时候人最少？"
- "帮我看看哪个时间段排队时间短"
- "高峰期是什么时候？"

## Context
客流级别：
- low: 低峰期（<30%容量）
- medium: 平峰期（30-50%容量）
- high: 高峰期（50-70%容量）
- peak: 极高峰期（>70%容量）

输出信息：
- wait_time_minutes: 预估等待时间
- queue_length: 排队人数
- crowd_level: 客流级别
- recommended_time: 推荐观演时间
"""

    skill = SkillSpec(
        name="hongloumeng_queue_prediction",
        description="预测各个剧目的排队时间，为用户提供最佳观演时间建议",
        when_to_use="当用户需要了解排队时间、选择最佳观演时间段时使用",
        handler_type="context",
        trigger_keywords=(
            "排队",
            "等待",
            "多久",
            "人多",
            "时间",
            "高峰",
            "拥挤",
        ),
        content=content,
        context_text="排队时间预测服务，基于客流数据分析预测排队时长",
    )
    return skill


class QueuePredictionSkillHandler:
    """排队预测 Skill 处理器"""

    def __init__(self):
        self.data_service = DataService()

    def execute(self, user_request: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        执行排队时间预测

        Args:
            user_request: 用户请求文本
            context: 上下文信息

        Returns:
            排队时间预测结果
        """
        show_id = context.get("show_id") if context else None
        target_time = context.get("target_time") if context else None

        # 如果没有指定剧目，返回所有剧目的排队信息
        if not show_id:
            all_shows = self.data_service.get_all_shows()
            queue_predictions = []

            for show in all_shows:
                if target_time:
                    wait_time = self.data_service.predict_wait_time(
                        show.show_id,
                        datetime.fromisoformat(target_time) if isinstance(target_time, str) else target_time,
                    )
                else:
                    wait_time = self.data_service.predict_wait_time(show.show_id, datetime.now())

                queue_predictions.append({
                    "show_id": show.show_id,
                    "show_name": show.name,
                    "predicted_wait_time": wait_time,
                })

            return {
                "success": True,
                "queue_predictions": queue_predictions,
                "message": f"已预测 {len(queue_predictions)} 个剧目的排队时间",
            }

        # 指定剧目的排队预测
        if target_time:
            target_datetime = datetime.fromisoformat(target_time) if isinstance(target_time, str) else target_time
            wait_time = self.data_service.predict_wait_time(show_id, target_datetime)
        else:
            wait_time = self.data_service.predict_wait_time(show_id, datetime.now())

        show = self.data_service.get_show(show_id)

        return {
            "success": True,
            "show_id": show_id,
            "show_name": show.name if show else "未知剧目",
            "predicted_wait_time": wait_time,
            "message": f"预计排队时间约 {wait_time} 分钟",
        }

    def get_peak_times(self, date_str: str | None = None) -> dict[str, Any]:
        """获取高峰时段分析"""
        # 模拟高峰时段数据
        peak_times = {
            "morning_peak": {
                "time_range": "10:00-11:00",
                "crowd_level": "high",
                "suggestion": "建议避开此时段或提前到达",
            },
            "afternoon_peak": {
                "time_range": "14:00-15:00",
                "crowd_level": "peak",
                "suggestion": "人流高峰，建议选择其他时段",
            },
            "best_times": {
                "morning": "09:00-10:00",
                "noon": "12:00-13:00",
                "late_afternoon": "16:00-17:00",
                "suggestion": "这些时段人流较少，排队时间短",
            },
        }

        return {
            "success": True,
            "peak_times": peak_times,
            "message": "已获取高峰时段分析",
        }

    def update_crowd_data(self, crowd_data_dict: dict[str, Any]) -> dict[str, Any]:
        """更新客流数据"""
        queue_data = {}
        for show_id, queue_info_dict in crowd_data_dict.get("queue_data", {}).items():
            queue_info = QueueInfo(
                show_id=show_id,
                wait_time_minutes=queue_info_dict["wait_time_minutes"],
                queue_length=queue_info_dict["queue_length"],
                timestamp=datetime.fromisoformat(queue_info_dict["timestamp"]),
                crowd_level=queue_info_dict.get("crowd_level", "medium"),
            )
            queue_data[show_id] = queue_info

        crowd_data = CrowdData(
            timestamp=datetime.fromisoformat(crowd_data_dict["timestamp"]),
            total_visitors=crowd_data_dict["total_visitors"],
            area_distribution=crowd_data_dict["area_distribution"],
            queue_data=queue_data,
        )

        self.data_service.update_crowd_data(crowd_data)

        return {
            "success": True,
            "message": "已更新客流数据",
        }

    def compare_wait_times(self, show_ids: list[str], target_time: datetime) -> dict[str, Any]:
        """比较多个剧目的排队时间"""
        comparisons = []

        for show_id in show_ids:
            show = self.data_service.get_show(show_id)
            wait_time = self.data_service.predict_wait_time(show_id, target_time)

            if show:
                comparisons.append({
                    "show_id": show_id,
                    "show_name": show.name,
                    "wait_time": wait_time,
                    "rating": show.rating,
                })

        # 按排队时间排序
        comparisons.sort(key=lambda x: x["wait_time"])

        return {
            "success": True,
            "comparisons": comparisons,
            "recommended": comparisons[0] if comparisons else None,
            "message": f"已比较 {len(comparisons)} 个剧目的排队时间",
        }