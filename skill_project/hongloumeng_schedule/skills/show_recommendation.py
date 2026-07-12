"""剧目推荐 Skill"""
from __future__ import annotations

from typing import Any

from skill_project.langgraph_skill.models import SkillSpec
from skill_project.hongloumeng_schedule.data_service import DataService
from skill_project.hongloumeng_schedule.user_service import UserService


def create_show_recommendation_skill() -> SkillSpec:
    """创建剧目推荐的 Skill"""
    content = """
# 剧目推荐

## Description
这个 Skill 负责根据用户偏好、时间可用性、位置便利性和评分等维度推荐最适合的剧目，帮助用户做出最佳选择。

## When to Use
当用户需要：
- 获取个性化剧目推荐
- 了解热门剧目信息
- 根据时间段选择剧目
- 发现符合自己喜好的剧目

## Trigger Keywords
- 推荐
- 好看
- 热门
- 经典
- 哪个
- 选择
- 建议

## Procedure
1. 分析用户偏好和需求
2. 过滤可用剧目
3. 计算推荐评分
4. 生成推荐列表和说明

## Example Queries
- "推荐几个好看的剧目"
- "我喜欢爱情类的，有什么推荐？"
- "帮我推荐几个高评分的剧目"
- "有什么经典剧目值得看？"

## Context
推荐维度：
- content_tags: 内容标签匹配
- rating: 剧目评分
- location: 位置便利性
- available_seats: 座位可用性
- user_preference: 用户偏好匹配度

输出信息：
- show_id: 剧目ID
- show_name: 剧目名称
- rating: 评分
- content_tags: 内容标签
- location: 位置信息
- recommendation_reason: 推荐理由
"""

    skill = SkillSpec(
        name="hongloumeng_show_recommendation",
        description="根据用户偏好和剧目特征推荐最适合的剧目",
        when_to_use="当用户需要获取个性化剧目推荐、了解热门剧目信息时使用",
        handler_type="context",
        trigger_keywords=(
            "推荐",
            "好看",
            "热门",
            "经典",
            "哪个",
            "选择",
            "建议",
        ),
        content=content,
        context_text="剧目推荐服务，根据用户偏好和剧目特征生成个性化推荐",
    )
    return skill


class ShowRecommendationSkillHandler:
    """剧目推荐 Skill 处理器"""

    def __init__(self):
        self.data_service = DataService()
        self.user_service = UserService()

    def execute(self, user_request: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        执行剧目推荐

        Args:
            user_request: 用户请求文本
            context: 上下文信息

        Returns:
            剧目推荐结果
        """
        user_id = context.get("user_id") if context else "user_001"
        limit = context.get("limit", 5) if context else 5

        # 获取用户偏好
        user = self.user_service.get_user(user_id)

        # 获取所有剧目
        all_shows = self.data_service.get_all_shows()

        # 根据偏好过滤和排序
        recommendations = self._generate_recommendations(
            shows=all_shows,
            user_preferences=user.preferences if user else None,
            limit=limit,
        )

        return {
            "success": True,
            "recommendations": recommendations,
            "message": f"已为您推荐 {len(recommendations)} 个剧目",
        }

    def _generate_recommendations(
        self,
        shows: list[Any],
        user_preferences: Any | None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """生成推荐列表"""
        scored_shows = []

        for show in shows:
            score = self._calculate_recommendation_score(show, user_preferences)
            scored_shows.append((show, score))

        # 按分数排序
        scored_shows.sort(key=lambda x: x[1], reverse=True)

        # 生成推荐列表
        recommendations = []
        for show, score in scored_shows[:limit]:
            reason = self._generate_recommendation_reason(show, user_preferences, score)
            recommendations.append({
                "show_id": show.show_id,
                "show_name": show.name,
                "rating": show.rating,
                "content_tags": show.content_tags,
                "location": show.location.name,
                "duration_minutes": show.duration_minutes,
                "recommendation_score": round(score, 2),
                "recommendation_reason": reason,
                "description": show.description,
            })

        return recommendations

    def _calculate_recommendation_score(
        self,
        show: Any,
        user_preferences: Any | None,
    ) -> float:
        """计算推荐评分"""
        score = 0.0

        # 基础评分（剧目评分）
        score += show.rating * 20

        # 用户偏好匹配加分
        if user_preferences:
            # 内容标签匹配
            if user_preferences.preferred_show_types:
                matching_tags = sum(
                    1 for tag in show.content_tags
                    if tag in user_preferences.preferred_show_types
                )
                score += matching_tags * 25

            # 区域偏好匹配
            if user_preferences.preferred_areas:
                if show.location.area in user_preferences.preferred_areas:
                    score += 30

        # 座位可用性加分
        available_seats = sum(
            schedule.available_seats for schedule in show.schedule
        )
        if available_seats > 0:
            score += 10

        # 评分热度（高评分剧目更受欢迎）
        if show.rating >= 4.8:
            score += 15
        elif show.rating >= 4.5:
            score += 10

        return score

    def _generate_recommendation_reason(
        self,
        show: Any,
        user_preferences: Any | None,
        score: float,
    ) -> str:
        """生成推荐理由"""
        reasons = []

        # 高评分理由
        if show.rating >= 4.8:
            reasons.append(f"高评分剧目（{show.rating}分）")
        elif show.rating >= 4.5:
            reasons.append(f"优质剧目（{show.rating}分）")

        # 偏好匹配理由
        if user_preferences and user_preferences.preferred_show_types:
            matching_tags = [
                tag for tag in show.content_tags
                if tag in user_preferences.preferred_show_types
            ]
            if matching_tags:
                reasons.append(f"符合您喜欢的{', '.join(matching_tags)}类型")

        # 区域便利理由
        if user_preferences and user_preferences.preferred_areas:
            if show.location.area in user_preferences.preferred_areas:
                reasons.append(f"位于您偏好的{show.location.area}区域")

        # 座位充足理由
        available_seats = sum(
            schedule.available_seats for schedule in show.schedule
        )
        if available_seats > 50:
            reasons.append("座位充足，无需长时间排队")

        if not reasons:
            reasons.append("值得观看的精彩剧目")

        return "；".join(reasons)

    def get_top_rated_shows(self, limit: int = 5) -> dict[str, Any]:
        """获取评分最高的剧目"""
        all_shows = self.data_service.get_all_shows()
        sorted_shows = sorted(all_shows, key=lambda s: s.rating, reverse=True)

        recommendations = []
        for show in sorted_shows[:limit]:
            recommendations.append({
                "show_id": show.show_id,
                "show_name": show.name,
                "rating": show.rating,
                "content_tags": show.content_tags,
                "location": show.location.name,
                "duration_minutes": show.duration_minutes,
                "recommendation_reason": f"高评分热门剧目（{show.rating}分）",
            })

        return {
            "success": True,
            "recommendations": recommendations,
            "message": f"已推荐 {len(recommendations)} 个高评分剧目",
        }

    def get_shows_by_type(self, content_type: str, limit: int = 5) -> dict[str, Any]:
        """获取指定类型的剧目"""
        shows = self.data_service.get_shows_by_tags([content_type])
        sorted_shows = sorted(shows, key=lambda s: s.rating, reverse=True)

        recommendations = []
        for show in sorted_shows[:limit]:
            recommendations.append({
                "show_id": show.show_id,
                "show_name": show.name,
                "rating": show.rating,
                "content_tags": show.content_tags,
                "location": show.location.name,
                "duration_minutes": show.duration_minutes,
                "recommendation_reason": f"{content_type}类型推荐剧目",
            })

        return {
            "success": True,
            "content_type": content_type,
            "recommendations": recommendations,
            "message": f"已推荐 {len(recommendations)} 个{content_type}类型的剧目",
        }

    def get_area_shows(self, area: str) -> dict[str, Any]:
        """获取指定区域的剧目"""
        shows = self.data_service.get_shows_by_area(area)

        recommendations = []
        for show in shows:
            recommendations.append({
                "show_id": show.show_id,
                "show_name": show.name,
                "rating": show.rating,
                "content_tags": show.content_tags,
                "location": show.location.name,
                "duration_minutes": show.duration_minutes,
                "recommendation_reason": f"位于{area}区域",
            })

        return {
            "success": True,
            "area": area,
            "recommendations": recommendations,
            "message": f"{area}区域共有 {len(recommendations)} 个剧目",
        }