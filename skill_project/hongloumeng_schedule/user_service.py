"""用户服务：管理用户信息、偏好、购票信息等"""
from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from skill_project.hongloumeng_schedule.models import (
    ConversationStyle,
    TicketInfo,
    TimeConstraints,
    User,
    UserPreferences,
)


class UserService:
    """用户服务，负责管理用户信息和偏好"""

    def __init__(self, data_dir: Path | None = None):
        self.data_dir = data_dir or Path("data/hongloumeng/users")
        self.users: dict[str, User] = {}
        self._load_users()

    def _load_users(self):
        """加载用户数据"""
        # 模拟数据，实际应该从数据库或文件加载
        self._create_mock_users()

    def _create_mock_users(self):
        """创建模拟用户数据"""
        # 创建几个示例用户
        users_data = [
            {
                "user_id": "user_001",
                "name": "张三",
                "preferences": {
                    "preferred_show_types": ["爱情", "经典"],
                    "preferred_areas": ["大观园"],
                    "group_size": 2,
                    "budget_level": "medium",
                    "mobility_level": "normal",
                    "priority": "experience",
                },
                "conversation_style": {
                    "language": "zh-CN",
                    "tone": "friendly",
                    "detail_level": "medium",
                    "emoji_usage": True,
                    "formal_level": "casual",
                },
            },
            {
                "user_id": "user_002",
                "name": "李四",
                "preferences": {
                    "preferred_show_types": ["家族", "管理"],
                    "preferred_areas": ["荣国府"],
                    "group_size": 4,
                    "budget_level": "high",
                    "mobility_level": "fast",
                    "priority": "time-saving",
                },
                "conversation_style": {
                    "language": "zh-CN",
                    "tone": "professional",
                    "detail_level": "brief",
                    "emoji_usage": False,
                    "formal_level": "semi-formal",
                },
            },
        ]

        for user_data in users_data:
            user = User(
                user_id=user_data["user_id"],
                name=user_data["name"],
                preferences=UserPreferences(
                    preferred_show_types=user_data["preferences"]["preferred_show_types"],
                    preferred_areas=user_data["preferences"]["preferred_areas"],
                    group_size=user_data["preferences"]["group_size"],
                    budget_level=user_data["preferences"]["budget_level"],
                    mobility_level=user_data["preferences"]["mobility_level"],
                    priority=user_data["preferences"]["priority"],
                ),
                conversation_style=ConversationStyle(
                    language=user_data["conversation_style"]["language"],
                    tone=user_data["conversation_style"]["tone"],
                    detail_level=user_data["conversation_style"]["detail_level"],
                    emoji_usage=user_data["conversation_style"]["emoji_usage"],
                    formal_level=user_data["conversation_style"]["formal_level"],
                ),
            )
            self.users[user.user_id] = user

    def get_user(self, user_id: str) -> User | None:
        """获取用户信息"""
        return self.users.get(user_id)

    def create_user(
        self,
        name: str,
        preferences: UserPreferences | None = None,
        conversation_style: ConversationStyle | None = None,
    ) -> User:
        """创建新用户"""
        user_id = f"user_{uuid4().hex[:8]}"
        user = User(
            user_id=user_id,
            name=name,
            preferences=preferences or UserPreferences(),
            conversation_style=conversation_style or ConversationStyle(),
        )
        self.users[user.user_id] = user
        self._save_user(user)
        return user

    def update_user_preferences(
        self,
        user_id: str,
        preferences: UserPreferences,
    ) -> User | None:
        """更新用户偏好"""
        user = self.get_user(user_id)
        if user:
            user.preferences = preferences
            self._save_user(user)
            return user
        return None

    def update_conversation_style(
        self,
        user_id: str,
        style: ConversationStyle,
    ) -> User | None:
        """更新对话偏好"""
        user = self.get_user(user_id)
        if user:
            user.conversation_style = style
            self._save_user(user)
            return user
        return None

    def add_ticket_info(
        self,
        user_id: str,
        ticket_type: str,
        valid_date: date,
        price: float,
    ) -> TicketInfo | None:
        """添加购票信息"""
        user = self.get_user(user_id)
        if user:
            ticket = TicketInfo(
                ticket_id=f"ticket_{uuid4().hex[:8]}",
                user_id=user_id,
                ticket_type=ticket_type,
                purchase_date=datetime.now(),
                valid_date=valid_date,
                price=price,
            )
            user.ticket_info = ticket
            self._save_user(user)
            return ticket
        return None

    def extract_preferences_from_text(self, text: str) -> UserPreferences:
        """
        从用户文本中提取偏好信息
        这是一个简化的实现，实际应该使用LLM进行提取
        """
        # 关键词匹配
        preferred_types = []
        preferred_areas = []
        priority = "balanced"

        # 检测剧目类型偏好
        type_keywords = {
            "爱情": ["爱情", "宝黛", "黛玉"],
            "家族": ["家族", "理家", "探春"],
            "经典": ["经典", "名著"],
            "悲剧": ["悲剧", "焚稿"],
        }

        for type_name, keywords in type_keywords.items():
            if any(keyword in text for keyword in keywords):
                preferred_types.append(type_name)

        # 检测区域偏好
        area_keywords = {
            "大观园": ["大观园", "潇湘馆", "蘅芜苑"],
            "荣国府": ["荣国府", "正厅"],
        }

        for area_name, keywords in area_keywords.items():
            if any(keyword in text for keyword in keywords):
                preferred_areas.append(area_name)

        # 检测优先级
        if any(word in text for word in ["时间", "快", "效率", "赶"]):
            priority = "time-saving"
        elif any(word in text for word in ["体验", "感受", "慢", "仔细"]):
            priority = "experience"

        # 检测人数
        group_size = 1
        import re
        numbers = re.findall(r"\d+人", text)
        if numbers:
            group_size = int(numbers[0].replace("人", ""))

        return UserPreferences(
            preferred_show_types=preferred_types,
            preferred_areas=preferred_areas,
            priority=priority,
            group_size=group_size,
        )

    def get_user_history(self, user_id: str) -> list[str]:
        """获取用户历史行程"""
        user = self.get_user(user_id)
        if user:
            return user.history
        return []

    def add_to_history(self, user_id: str, itinerary_id: str) -> bool:
        """添加行程到历史记录"""
        user = self.get_user(user_id)
        if user:
            user.history.append(itinerary_id)
            self._save_user(user)
            return True
        return False

    def _save_user(self, user: User):
        """保存用户数据"""
        # 实际应该保存到数据库或文件
        # 这里只是模拟
        pass

    def list_all_users(self) -> list[User]:
        """列出所有用户"""
        return list(self.users.values())

    def export_user_data(self, user_id: str) -> dict[str, Any] | None:
        """导出用户数据"""
        user = self.get_user(user_id)
        if user:
            return user.to_dict()
        return None