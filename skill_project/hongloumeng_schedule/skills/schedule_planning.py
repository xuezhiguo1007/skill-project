"""行程编排规划 Skill"""
from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any

from skill_project.langgraph_skill.models import SkillSpec
from skill_project.hongloumeng_schedule.schedule_service import ScheduleService


def create_schedule_planning_skill() -> SkillSpec:
    """创建行程编排规划的 Skill"""
    content = """
# 廊坊红楼梦景区行程编排规划

## Description
这个 Skill 负责为用户编排廊坊红楼梦景区的游览行程，考虑排队时间、剧目时间表、用户偏好和位置信息，生成最优化的行程安排。

## When to Use
当用户需要：
- 制定完整的游览行程计划
- 优化游览路线和时间安排
- 了解排队时间和最佳观演时间
- 获得个性化的行程建议

## Trigger Keywords
- 行程
- 规划
- 安排
- 游览
- 排队
- 时间表
- 路线
- 一日游

## Procedure
1. 获取用户信息和偏好
2. 查询可用的剧目和时间安排
3. 计算排队时间和步行时间
4. 根据偏好优化行程顺序
5. 生成详细的行程安排和建议

## Example Queries
- "帮我安排明天一天的游览行程"
- "我想看红楼梦的经典剧目，怎么安排时间？"
- "帮我规划一条排队时间最少的路线"
- "我们一行4人，想在大观园区域游览，帮我安排行程"

## Context
用户偏好：
- preferred_show_types: 喜欢的剧目类型（爱情、家族、经典、悲剧等）
- preferred_areas: 喜欢的区域（大观园、荣国府等）
- group_size: 团队人数
- priority: 优先级（time-saving, experience, balanced）

输出格式：
- itinerary_id: 行程ID
- items: 行程项目列表
  - show: 剧目信息
  - schedule: 时间安排
  - estimated_arrival_time: 预估到达时间
  - estimated_wait_time: 预估排队时间
- total_wait_time: 总排队时间
- total_show_time: 总观演时间
- optimization_score: 优化评分
- suggestions: 行程建议
"""

    skill = SkillSpec(
        name="hongloumeng_schedule_planning",
        description="为用户编排廊坊红楼梦景区的游览行程，生成最优化的行程安排",
        when_to_use="当用户需要制定游览行程计划、优化游览路线和时间安排时使用",
        handler_type="context",
        trigger_keywords=(
            "行程",
            "规划",
            "安排",
            "游览",
            "排队",
            "时间表",
            "路线",
            "一日游",
        ),
        content=content,
        context_text="行程编排规划服务，负责根据用户偏好和剧目时间表生成优化的游览行程",
    )
    return skill


class SchedulePlanningSkillHandler:
    """行程编排 Skill 处理器"""

    def __init__(self):
        self.schedule_service = ScheduleService()

    def execute(self, user_request: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        执行行程编排

        Args:
            user_request: 用户请求文本
            context: 上下文信息，包含 user_id, target_date 等

        Returns:
            行程编排结果
        """
        # 从上下文获取必要信息
        user_id = context.get("user_id") if context else None
        target_date = context.get("target_date") if context else None

        if not user_id:
            # 尝试从请求中提取用户ID
            user_id = "user_001"  # 默认用户

        if not target_date:
            # 默认使用今天
            target_date = date.today()

        # 创建行程
        itinerary = self.schedule_service.create_itinerary(
            user_id=user_id,
            target_date=target_date,
        )

        if not itinerary:
            return {
                "success": False,
                "message": "无法创建行程，请检查用户信息和剧目可用性",
            }

        return {
            "success": True,
            "itinerary": itinerary.to_dict(),
            "message": f"已为用户 {user_id} 创建行程安排，包含 {len(itinerary.items)} 个剧目",
        }

    def optimize_for_minimal_wait(self, user_id: str, target_date: date) -> dict[str, Any]:
        """为最小排队时间优化行程"""
        itinerary = self.schedule_service.optimize_for_minimal_wait_time(
            user_id=user_id,
            target_date=target_date,
        )

        if not itinerary:
            return {
                "success": False,
                "message": "无法创建优化行程",
            }

        return {
            "success": True,
            "itinerary": itinerary.to_dict(),
            "message": f"已创建最小排队时间的行程，总排队时间 {itinerary.total_wait_time} 分钟",
        }

    def get_real_time_recommendations(self, user_id: str) -> dict[str, Any]:
        """获取实时推荐"""
        recommendations = self.schedule_service.get_real_time_recommendations(
            user_id=user_id,
            current_time=datetime.now(),
        )

        return {
            "success": True,
            "recommendations": recommendations,
            "message": f"找到 {len(recommendations)} 个当前可观看的剧目推荐",
        }