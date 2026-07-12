"""用户偏好管理 Skill"""
from __future__ import annotations

from typing import Any

from skill_project.langgraph_skill.models import SkillSpec
from skill_project.hongloumeng_schedule.user_service import UserService
from skill_project.hongloumeng_schedule.models import UserPreferences, ConversationStyle


def create_user_preference_skill() -> SkillSpec:
    """创建用户偏好管理的 Skill"""
    content = """
# 用户偏好管理

## Description
这个 Skill 负责管理和分析用户的偏好信息，包括剧目类型偏好、区域偏好、时间约束、团队规模等，并根据用户对话自动提取偏好信息。

## When to Use
当用户需要：
- 设置或更新个人偏好
- 从对话中提取偏好信息
- 查看当前偏好设置
- 了解适合自己偏好的推荐

## Trigger Keywords
- 偏好
- 喜欢
- 设置
- 更新
- 我喜欢
- 我们几个人
- 老人
- 小孩

## Procedure
1. 分析用户对话内容
2. 提取偏好信息关键词
3. 更新用户偏好设置
4. 根据新偏好推荐相关剧目

## Example Queries
- "我喜欢爱情类的剧目"
- "我们一行4个人，有老人和小孩"
- "帮我设置偏好，喜欢经典剧目"
- "我想在大观园区域游览"

## Context
偏好字段：
- preferred_show_types: 喜欢的剧目类型列表
- preferred_areas: 喜欢的区域列表
- group_size: 团队人数
- budget_level: 预算级别（low, medium, high）
- mobility_level: 行动能力（fast, normal, slow）
- priority: 优先级（time-saving, experience, balanced）

对话风格：
- language: 语言
- tone: 语气风格
- detail_level: 详细程度
- emoji_usage: 是否使用表情符号
"""

    skill = SkillSpec(
        name="hongloumeng_user_preference",
        description="管理和分析用户的偏好信息，根据对话自动提取偏好",
        when_to_use="当用户需要设置偏好、更新偏好或从对话中提取偏好信息时使用",
        handler_type="context",
        trigger_keywords=(
            "偏好",
            "喜欢",
            "设置",
            "更新",
            "我喜欢",
            "我们几个人",
            "老人",
            "小孩",
        ),
        content=content,
        context_text="用户偏好管理服务，负责分析和更新用户偏好设置",
    )
    return skill


class UserPreferenceSkillHandler:
    """用户偏好 Skill 处理器"""

    def __init__(self):
        self.user_service = UserService()

    def execute(self, user_request: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        执行偏好提取和更新

        Args:
            user_request: 用户请求文本
            context: 上下文信息

        Returns:
            偏好提取和更新结果
        """
        user_id = context.get("user_id") if context else "user_001"

        # 从用户文本中提取偏好
        extracted_preferences = self.user_service.extract_preferences_from_text(user_request)

        # 更新用户偏好
        user = self.user_service.update_user_preferences(user_id, extracted_preferences)

        if not user:
            return {
                "success": False,
                "message": "用户不存在，无法更新偏好",
            }

        return {
            "success": True,
            "extracted_preferences": {
                "preferred_show_types": extracted_preferences.preferred_show_types,
                "preferred_areas": extracted_preferences.preferred_areas,
                "group_size": extracted_preferences.group_size,
                "priority": extracted_preferences.priority,
            },
            "message": f"已从对话中提取并更新用户偏好：喜欢的类型={extracted_preferences.preferred_show_types}, 区域={extracted_preferences.preferred_areas}",
        }

    def get_user_preferences(self, user_id: str) -> dict[str, Any]:
        """获取用户当前偏好"""
        user = self.user_service.get_user(user_id)

        if not user:
            return {
                "success": False,
                "message": "用户不存在",
            }

        return {
            "success": True,
            "preferences": {
                "preferred_show_types": user.preferences.preferred_show_types,
                "preferred_areas": user.preferences.preferred_areas,
                "group_size": user.preferences.group_size,
                "budget_level": user.preferences.budget_level,
                "mobility_level": user.preferences.mobility_level,
                "priority": user.preferences.priority,
            },
            "conversation_style": {
                "language": user.conversation_style.language,
                "tone": user.conversation_style.tone,
                "detail_level": user.conversation_style.detail_level,
                "emoji_usage": user.conversation_style.emoji_usage,
            },
        }

    def update_conversation_style(
        self,
        user_id: str,
        language: str = "zh-CN",
        tone: str = "friendly",
        detail_level: str = "medium",
        emoji_usage: bool = False,
    ) -> dict[str, Any]:
        """更新对话风格"""
        style = ConversationStyle(
            language=language,
            tone=tone,
            detail_level=detail_level,
            emoji_usage=emoji_usage,
        )

        user = self.user_service.update_conversation_style(user_id, style)

        if not user:
            return {
                "success": False,
                "message": "用户不存在",
            }

        return {
            "success": True,
            "message": f"已更新对话风格：语言={language}, 语气={tone}",
        }