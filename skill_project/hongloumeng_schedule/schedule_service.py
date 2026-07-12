"""行程编排核心服务"""
from __future__ import annotations

from datetime import datetime, timedelta, date
from typing import Any
from uuid import uuid4

from skill_project.hongloumeng_schedule.data_service import DataService
from skill_project.hongloumeng_schedule.models import (
    Itinerary,
    ItineraryItem,
    Show,
    ShowSchedule,
    User,
    UserPreferences,
)
from skill_project.hongloumeng_schedule.user_service import UserService


class ScheduleService:
    """行程编排核心服务"""

    def __init__(
        self,
        data_service: DataService | None = None,
        user_service: UserService | None = None,
    ):
        self.data_service = data_service or DataService()
        self.user_service = user_service or UserService()

    def create_itinerary(
        self,
        user_id: str,
        target_date: date,
        preferences: UserPreferences | None = None,
    ) -> Itinerary | None:
        """为用户创建行程安排"""
        user = self.user_service.get_user(user_id)
        if not user:
            return None

        # 使用用户偏好或传入的偏好
        user_prefs = preferences or user.preferences

        # 获取可用剧目
        available_shows = self._filter_shows_by_preferences(
            self.data_service.get_all_shows(),
            user_prefs,
        )

        if not available_shows:
            return None

        # 编排行程
        itinerary = self._optimize_schedule(
            user=user,
            target_date=target_date,
            shows=available_shows,
            preferences=user_prefs,
        )

        return itinerary

    def _filter_shows_by_preferences(
        self,
        shows: list[Show],
        preferences: UserPreferences,
    ) -> list[Show]:
        """根据用户偏好过滤剧目"""
        filtered = shows

        # 按类型过滤
        if preferences.preferred_show_types:
            filtered = [
                show for show in filtered
                if any(
                    tag in preferences.preferred_show_types
                    for tag in show.content_tags
                )
            ]

        # 按区域过滤
        if preferences.preferred_areas:
            filtered = [
                show for show in filtered
                if show.location.area in preferences.preferred_areas
            ]

        # 如果过滤结果为空，返回所有剧目
        return filtered if filtered else shows

    def _optimize_schedule(
        self,
        user: User,
        target_date: date,
        shows: list[Show],
        preferences: UserPreferences,
    ) -> Itinerary:
        """优化行程安排"""
        itinerary_id = f"itin_{uuid4().hex[:8]}"

        # 确定时间范围
        start_time = datetime.combine(
            target_date,
            preferences.time_constraints.start_time if preferences.time_constraints
            else datetime.min.time()
        )
        end_time = datetime.combine(
            target_date,
            preferences.time_constraints.end_time if preferences.time_constraints
            else datetime.max.time()
        )

        # 按评分和时间排序剧目
        shows_sorted = self._rank_shows(shows, preferences)

        # 选择剧目并编排时间
        selected_items = []
        current_time = start_time

        for show in shows_sorted:
            # 检查是否有合适的时间安排
            best_schedule = self._find_best_schedule(
                show=show,
                current_time=current_time,
                end_time=end_time,
            )

            if best_schedule:
                # 计算排队时间和到达时间
                wait_time = self.data_service.predict_wait_time(
                    show.show_id,
                    best_schedule.start_time,
                )

                # 计算步行时间（如果有上一个剧目）
                walking_time = 0
                if selected_items:
                    last_item = selected_items[-1]
                    walking_time = self.data_service.calculate_walking_time(
                        last_item.show.location,
                        show.location,
                    )

                # 计算到达时间
                arrival_time = current_time + timedelta(minutes=walking_time)

                # 检查是否能按时到达
                if arrival_time + timedelta(minutes=wait_time) <= best_schedule.start_time:
                    item = ItineraryItem(
                        show=show,
                        schedule=best_schedule,
                        estimated_arrival_time=arrival_time,
                        estimated_wait_time=wait_time,
                    )
                    selected_items.append(item)

                    # 更新当前时间为剧结束时间
                    current_time = best_schedule.end_time

                    # 添加休息时间
                    current_time += timedelta(minutes=15)

                    # 检查是否已达到时间限制
                    if current_time >= end_time:
                        break

        # 创建行程
        itinerary = Itinerary(
            itinerary_id=itinerary_id,
            user_id=user.user_id,
            date=target_date,
            items=selected_items,
        )

        # 计算优化评分和建议
        itinerary.optimization_score = self._calculate_optimization_score(
            itinerary,
            preferences,
        )
        itinerary.suggestions = self._generate_suggestions(itinerary, preferences)

        # 保存到用户历史
        self.user_service.add_to_history(user.user_id, itinerary_id)

        return itinerary

    def _rank_shows(
        self,
        shows: list[Show],
        preferences: UserPreferences,
    ) -> list[Show]:
        """根据偏好对剧目排序"""
        scored_shows = []

        for show in shows:
            score = show.rating * 10  # 基础分数来自评分

            # 根据偏好加分
            if preferences.preferred_show_types:
                matching_tags = sum(
                    1 for tag in show.content_tags
                    if tag in preferences.preferred_show_types
                )
                score += matching_tags * 15

            if preferences.preferred_areas:
                if show.location.area in preferences.preferred_areas:
                    score += 20

            # 根据优先级调整
            if preferences.priority == "time-saving":
                # 短时长剧目优先
                score -= show.duration_minutes * 0.5
            elif preferences.priority == "experience":
                # 高评分剧目优先
                score += show.rating * 5

            scored_shows.append((show, score))

        # 按分数排序
        scored_shows.sort(key=lambda x: x[1], reverse=True)
        return [show for show, _ in scored_shows]

    def _find_best_schedule(
        self,
        show: Show,
        current_time: datetime,
        end_time: datetime,
    ) -> ShowSchedule | None:
        """找到最佳的时间安排"""
        available_schedules = [
            schedule for schedule in show.schedule
            if schedule.start_time >= current_time
            and schedule.end_time <= end_time
            and schedule.is_available()
        ]

        if not available_schedules:
            return None

        # 选择最接近当前时间且有足够座位的安排
        best_schedule = None
        best_score = -1

        for schedule in available_schedules:
            # 时间接近度分数（越接近越好，但有缓冲时间）
            time_score = 100 - abs(
                (schedule.start_time - current_time).total_seconds() / 60
            )

            # 座位可用性分数
            availability_score = schedule.available_seats / schedule.capacity * 50

            score = time_score + availability_score

            if score > best_score:
                best_score = score
                best_schedule = schedule

        return best_schedule

    def _calculate_optimization_score(
        self,
        itinerary: Itinerary,
        preferences: UserPreferences,
    ) -> float:
        """计算行程优化评分"""
        if not itinerary.items:
            return 0.0

        score = 100.0

        # 排队时间惩罚
        total_wait = itinerary.total_wait_time
        score -= total_wait * 0.5

        # 观演数量奖励
        score += len(itinerary.items) * 10

        # 剧目评分奖励
        avg_rating = sum(item.show.rating for item in itinerary.items) / len(itinerary.items)
        score += avg_rating * 10

        # 偏好匹配度奖励
        if preferences.preferred_show_types:
            matching_count = sum(
                1 for item in itinerary.items
                if any(
                    tag in preferences.preferred_show_types
                    for tag in item.show.content_tags
                )
            )
            score += matching_count * 15

        # 时间利用率
        if preferences.time_constraints:
            total_time = itinerary.total_wait_time + itinerary.total_show_time
            preferred_duration = preferences.time_constraints.preferred_duration_hours * 60
            utilization = min(total_time / preferred_duration, 1.0)
            score += utilization * 20

        return max(min(score, 100.0), 0.0)

    def _generate_suggestions(
        self,
        itinerary: Itinerary,
        preferences: UserPreferences,
    ) -> list[str]:
        """生成行程建议"""
        suggestions = []

        if not itinerary.items:
            suggestions.append("当前时间段没有合适的剧目安排，建议调整时间范围。")
            return suggestions

        # 排队时间建议
        if itinerary.total_wait_time > 60:
            suggestions.append(
                f"总排队时间约{itinerary.total_wait_time}分钟，建议提前到达或选择较少人的时间段。"
            )

        # 区域集中度建议
        areas = [item.show.location.area for item in itinerary.items]
        if len(set(areas)) > 2:
            suggestions.append(
                "行程跨越多个区域，建议考虑区域集中安排以减少步行时间。"
            )

        # 时间紧凑度建议
        total_duration = itinerary.total_show_time + itinerary.total_wait_time
        if total_duration > preferences.time_constraints.preferred_duration_hours * 60 * 1.5:
            suggestions.append("行程安排较为紧凑，建议适当减少剧目数量以提升体验质量。")

        # 高评分剧目推荐
        high_rated = [item.show.name for item in itinerary.items if item.show.rating >= 4.8]
        if high_rated:
            suggestions.append(f"推荐重点关注高评分剧目：{', '.join(high_rated)}。")

        return suggestions

    def update_itinerary(
        self,
        itinerary: Itinerary,
        add_show_id: str | None = None,
        remove_show_id: str | None = None,
    ) -> Itinerary:
        """更新行程安排"""
        if add_show_id:
            show = self.data_service.get_show(add_show_id)
            if show:
                # 找到合适的插入位置
                # 这里简化处理，实际应该重新优化整个行程
                pass

        if remove_show_id:
            itinerary.items = [
                item for item in itinerary.items
                if item.show.show_id != remove_show_id
            ]

        itinerary.calculate_totals()
        return itinerary

    def get_real_time_recommendations(
        self,
        user_id: str,
        current_time: datetime,
    ) -> list[dict[str, Any]]:
        """获取实时推荐"""
        user = self.user_service.get_user(user_id)
        if not user:
            return []

        # 获取当前可观看的剧目
        available_shows = self.data_service.get_available_shows_at_time(current_time)

        # 根据用户偏好过滤和排序
        filtered_shows = self._filter_shows_by_preferences(
            available_shows,
            user.preferences,
        )
        ranked_shows = self._rank_shows(filtered_shows, user.preferences)

        # 生成推荐
        recommendations = []
        for show in ranked_shows[:5]:  # 只推荐前5个
            wait_time = self.data_service.predict_wait_time(show.show_id, current_time)
            recommendations.append({
                "show_id": show.show_id,
                "show_name": show.name,
                "location": show.location.name,
                "rating": show.rating,
                "estimated_wait_time": wait_time,
                "next_schedule": show.get_available_schedules()[0] if show.get_available_schedules() else None,
            })

        return recommendations

    def optimize_for_minimal_wait_time(
        self,
        user_id: str,
        target_date: date,
    ) -> Itinerary | None:
        """为最小排队时间优化行程"""
        user = self.user_service.get_user(user_id)
        if not user:
            return None

        # 创建偏好副本，设置为时间优先
        preferences = UserPreferences(
            preferred_show_types=user.preferences.preferred_show_types,
            preferred_areas=user.preferences.preferred_areas,
            priority="time-saving",
        )

        return self.create_itinerary(user_id, target_date, preferences)