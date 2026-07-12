"""Skills for Hongloumeng schedule system"""
from __future__ import annotations

from skill_project.hongloumeng_schedule.skills.schedule_planning import (
    create_schedule_planning_skill,
    SchedulePlanningSkillHandler,
)
from skill_project.hongloumeng_schedule.skills.user_preference import (
    create_user_preference_skill,
    UserPreferenceSkillHandler,
)
from skill_project.hongloumeng_schedule.skills.queue_prediction import (
    create_queue_prediction_skill,
    QueuePredictionSkillHandler,
)
from skill_project.hongloumeng_schedule.skills.show_recommendation import (
    create_show_recommendation_skill,
    ShowRecommendationSkillHandler,
)

__all__ = [
    "create_schedule_planning_skill",
    "SchedulePlanningSkillHandler",
    "create_user_preference_skill",
    "UserPreferenceSkillHandler",
    "create_queue_prediction_skill",
    "QueuePredictionSkillHandler",
    "create_show_recommendation_skill",
    "ShowRecommendationSkillHandler",
]