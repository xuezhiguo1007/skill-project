"""数据模型定义"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time
from typing import Any


@dataclass(slots=True)
class Location:
    """位置信息"""
    location_id: str
    name: str
    area: str  # 区域名称，如"大观园"、"荣国府"等
    coordinates: tuple[float, float]  # (latitude, longitude)
    description: str = ""


@dataclass(slots=True)
class ShowSchedule:
    """剧目时间安排"""
    schedule_id: str
    start_time: datetime
    end_time: datetime
    capacity: int  # 容量
    current_bookings: int = 0  # 当前预订数量
    available_seats: int = 0

    def __post_init__(self):
        self.available_seats = self.capacity - self.current_bookings

    def is_available(self) -> bool:
        """判断是否还有可用座位"""
        return self.available_seats > 0


@dataclass(slots=True)
class Show:
    """剧目信息"""
    show_id: str
    name: str
    location: Location
    content_tags: list[str]  # 内容标签，如"爱情"、"家族"、"经典"等
    schedule: list[ShowSchedule]
    duration_minutes: int
    description: str = ""
    rating: float = 0.0  # 评分（0-5）

    def get_available_schedules(self) -> list[ShowSchedule]:
        """获取所有可用的时间安排"""
        return [s for s in self.schedule if s.is_available()]


@dataclass(slots=True)
class QueueInfo:
    """排队信息"""
    show_id: str
    wait_time_minutes: int  # 预估等待时间（分钟）
    queue_length: int  # 排队人数
    timestamp: datetime
    crowd_level: str = "medium"  # 客流级别: low, medium, high, peak

    def to_dict(self) -> dict[str, Any]:
        return {
            "show_id": self.show_id,
            "wait_time_minutes": self.wait_time_minutes,
            "queue_length": self.queue_length,
            "timestamp": self.timestamp.isoformat(),
            "crowd_level": self.crowd_level,
        }


@dataclass(slots=True)
class TicketInfo:
    """购票信息"""
    ticket_id: str
    user_id: str
    ticket_type: str  # 票种：普通票、VIP票等
    purchase_date: datetime
    valid_date: date
    price: float
    status: str = "active"  # active, used, expired


@dataclass(slots=True)
class TimeConstraints:
    """时间约束"""
    start_time: time  # 开始时间
    end_time: time  # 结束时间
    preferred_duration_hours: float = 4.0  # 希望游玩时长
    break_intervals: list[tuple[time, time]] = field(default_factory=list)  # 休息时间段


@dataclass(slots=True)
class UserPreferences:
    """用户偏好"""
    preferred_show_types: list[str] = field(default_factory=list)  # 喜欢的剧目类型
    preferred_areas: list[str] = field(default_factory=list)  # 喜欢的区域
    time_constraints: TimeConstraints | None = None
    group_size: int = 1  # 团队人数
    budget_level: str = "medium"  # 预算级别: low, medium, high
    mobility_level: str = "normal"  # 行动能力: fast, normal, slow
    priority: str = "balanced"  # 优先级: time-saving, experience, balanced


@dataclass(slots=True)
class ConversationStyle:
    """对话偏好"""
    language: str = "zh-CN"  # 语言
    tone: str = "friendly"  # 语气风格
    detail_level: str = "medium"  # 详细程度: brief, medium, detailed
    emoji_usage: bool = False  # 是否使用表情符号
    formal_level: str = "casual"  # 正式程度: casual, semi-formal, formal


@dataclass(slots=True)
class User:
    """用户信息"""
    user_id: str
    name: str
    ticket_info: TicketInfo | None = None
    preferences: UserPreferences = field(default_factory=UserPreferences)
    conversation_style: ConversationStyle = field(default_factory=ConversationStyle)
    history: list[str] = field(default_factory=list)  # 历史行程ID列表

    def to_dict(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "name": self.name,
            "ticket_info": self.ticket_info,
            "preferences": self.preferences,
            "conversation_style": self.conversation_style,
            "history": self.history,
        }


@dataclass(slots=True)
class ItineraryItem:
    """行程项目"""
    show: Show
    schedule: ShowSchedule
    estimated_arrival_time: datetime
    estimated_wait_time: int  # 预估排队时间（分钟）
    actual_start_time: datetime | None = None
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "show": {
                "show_id": self.show.show_id,
                "name": self.show.name,
                "location": self.show.location.name,
                "content_tags": self.show.content_tags,
                "duration_minutes": self.show.duration_minutes,
            },
            "schedule": {
                "start_time": self.schedule.start_time.isoformat(),
                "end_time": self.schedule.end_time.isoformat(),
            },
            "estimated_arrival_time": self.estimated_arrival_time.isoformat(),
            "estimated_wait_time": self.estimated_wait_time,
            "notes": self.notes,
        }


@dataclass(slots=True)
class Itinerary:
    """行程安排"""
    itinerary_id: str
    user_id: str
    date: date
    items: list[ItineraryItem] = field(default_factory=list)
    total_wait_time: int = 0  # 总排队时间（分钟）
    total_show_time: int = 0  # 总观演时间（分钟）
    optimization_score: float = 0.0  # 优化评分
    suggestions: list[str] = field(default_factory=list)  # 建议

    def calculate_totals(self):
        """计算总时间"""
        self.total_wait_time = sum(item.estimated_wait_time for item in self.items)
        self.total_show_time = sum(item.show.duration_minutes for item in self.items)

    def to_dict(self) -> dict[str, Any]:
        self.calculate_totals()
        return {
            "itinerary_id": self.itinerary_id,
            "user_id": self.user_id,
            "date": self.date.isoformat(),
            "items": [item.to_dict() for item in self.items],
            "total_wait_time": self.total_wait_time,
            "total_show_time": self.total_show_time,
            "optimization_score": self.optimization_score,
            "suggestions": self.suggestions,
        }


@dataclass(slots=True)
class CrowdData:
    """客流数据"""
    timestamp: datetime
    total_visitors: int  # 总游客数
    area_distribution: dict[str, int]  # 各区域人数分布
    queue_data: dict[str, QueueInfo]  # 各剧目排队情况

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "total_visitors": self.total_visitors,
            "area_distribution": self.area_distribution,
            "queue_data": {
                k: v.to_dict() for k, v in self.queue_data.items()
            },
        }