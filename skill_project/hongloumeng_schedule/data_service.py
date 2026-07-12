"""数据服务：管理剧目、排队时间、位置信息等"""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from uuid import uuid4

from skill_project.hongloumeng_schedule.models import (
    CrowdData,
    Location,
    QueueInfo,
    Show,
    ShowSchedule,
)


class DataService:
    """数据服务，负责管理景区的所有数据"""

    def __init__(self, data_dir: Path | None = None):
        self.data_dir = data_dir or Path("data/hongloumeng")
        self.shows: dict[str, Show] = {}
        self.locations: dict[str, Location] = {}
        self.current_crowd_data: CrowdData | None = None
        self._load_data()

    def _load_data(self):
        """加载基础数据"""
        self._load_locations()
        self._load_shows()

    def _load_locations(self):
        """加载位置信息"""
        # 模拟数据，实际应该从数据库或文件加载
        locations_data = [
            {
                "location_id": "loc_001",
                "name": "大观园正门",
                "area": "大观园",
                "coordinates": (39.9042, 116.4074),
                "description": "大观园主入口",
            },
            {
                "location_id": "loc_002",
                "name": "荣国府正厅",
                "area": "荣国府",
                "coordinates": (39.9050, 116.4080),
                "description": "荣国府主要建筑",
            },
            {
                "location_id": "loc_003",
                "name": "潇湘馆",
                "area": "大观园",
                "coordinates": (39.9045, 116.4075),
                "description": "林黛玉居所",
            },
            {
                "location_id": "loc_004",
                "name": "蘅芜苑",
                "area": "大观园",
                "coordinates": (39.9046, 116.4076),
                "description": "薛宝钗居所",
            },
        ]

        for loc_data in locations_data:
            location = Location(
                location_id=loc_data["location_id"],
                name=loc_data["name"],
                area=loc_data["area"],
                coordinates=loc_data["coordinates"],
                description=loc_data.get("description", ""),
            )
            self.locations[location.location_id] = location

    def _load_shows(self):
        """加载剧目信息"""
        # 模拟数据，实际应该从数据库或文件加载
        shows_data = [
            {
                "show_id": "show_001",
                "name": "黛玉葬花",
                "location_id": "loc_003",
                "content_tags": ["爱情", "经典", "诗词"],
                "duration_minutes": 45,
                "description": "林黛玉葬花的经典场景再现",
                "rating": 4.8,
                "schedules": [
                    {
                        "start_time": "2024-07-15T09:00:00",
                        "end_time": "2024-07-15T09:45:00",
                        "capacity": 100,
                        "current_bookings": 30,
                    },
                    {
                        "start_time": "2024-07-15T11:00:00",
                        "end_time": "2024-07-15T11:45:00",
                        "capacity": 100,
                        "current_bookings": 50,
                    },
                    {
                        "start_time": "2024-07-15T14:00:00",
                        "end_time": "2024-07-15T14:45:00",
                        "capacity": 100,
                        "current_bookings": 20,
                    },
                ],
            },
            {
                "show_id": "show_002",
                "name": "宝黛初见",
                "location_id": "loc_002",
                "content_tags": ["爱情", "经典", "相遇"],
                "duration_minutes": 50,
                "description": "宝玉与黛玉初次相见的经典片段",
                "rating": 4.9,
                "schedules": [
                    {
                        "start_time": "2024-07-15T10:00:00",
                        "end_time": "2024-07-15T10:50:00",
                        "capacity": 150,
                        "current_bookings": 60,
                    },
                    {
                        "start_time": "2024-07-15T13:00:00",
                        "end_time": "2024-07-15T13:50:00",
                        "capacity": 150,
                        "current_bookings": 40,
                    },
                    {
                        "start_time": "2024-07-15T15:00:00",
                        "end_time": "2024-07-15T15:50:00",
                        "capacity": 150,
                        "current_bookings": 70,
                    },
                ],
            },
            {
                "show_id": "show_003",
                "name": "探春理家",
                "location_id": "loc_002",
                "content_tags": ["家族", "管理", "智慧"],
                "duration_minutes": 40,
                "description": "探春管理家务的精彩片段",
                "rating": 4.5,
                "schedules": [
                    {
                        "start_time": "2024-07-15T09:30:00",
                        "end_time": "2024-07-15T10:10:00",
                        "capacity": 80,
                        "current_bookings": 25,
                    },
                    {
                        "start_time": "2024-07-15T12:30:00",
                        "end_time": "2024-07-15T13:10:00",
                        "capacity": 80,
                        "current_bookings": 15,
                    },
                ],
            },
            {
                "show_id": "show_004",
                "name": "黛玉焚稿",
                "location_id": "loc_003",
                "content_tags": ["爱情", "悲剧", "经典"],
                "duration_minutes": 60,
                "description": "黛玉焚稿断痴情的悲壮场景",
                "rating": 4.7,
                "schedules": [
                    {
                        "start_time": "2024-07-15T16:00:00",
                        "end_time": "2024-07-15T17:00:00",
                        "capacity": 120,
                        "current_bookings": 80,
                    },
                    {
                        "start_time": "2024-07-15T18:00:00",
                        "end_time": "2024-07-15T19:00:00",
                        "capacity": 120,
                        "current_bookings": 90,
                    },
                ],
            },
        ]

        for show_data in shows_data:
            location = self.locations[show_data["location_id"]]
            schedules = []
            for schedule_data in show_data["schedules"]:
                schedule = ShowSchedule(
                    schedule_id=f"sch_{uuid4().hex[:8]}",
                    start_time=datetime.fromisoformat(schedule_data["start_time"]),
                    end_time=datetime.fromisoformat(schedule_data["end_time"]),
                    capacity=schedule_data["capacity"],
                    current_bookings=schedule_data["current_bookings"],
                )
                schedules.append(schedule)

            show = Show(
                show_id=show_data["show_id"],
                name=show_data["name"],
                location=location,
                content_tags=show_data["content_tags"],
                schedule=schedules,
                duration_minutes=show_data["duration_minutes"],
                description=show_data.get("description", ""),
                rating=show_data.get("rating", 0.0),
            )
            self.shows[show.show_id] = show

    def get_all_shows(self) -> list[Show]:
        """获取所有剧目"""
        return list(self.shows.values())

    def get_show(self, show_id: str) -> Show | None:
        """获取指定剧目"""
        return self.shows.get(show_id)

    def get_shows_by_area(self, area: str) -> list[Show]:
        """获取指定区域的剧目"""
        return [
            show for show in self.shows.values()
            if show.location.area == area
        ]

    def get_shows_by_tags(self, tags: list[str]) -> list[Show]:
        """获取包含指定标签的剧目"""
        return [
            show for show in self.shows.values()
            if any(tag in show.content_tags for tag in tags)
        ]

    def get_location(self, location_id: str) -> Location | None:
        """获取指定位置"""
        return self.locations.get(location_id)

    def get_all_locations(self) -> list[Location]:
        """获取所有位置"""
        return list(self.locations.values())

    def get_locations_by_area(self, area: str) -> list[Location]:
        """获取指定区域的所有位置"""
        return [
            loc for loc in self.locations.values()
            if loc.area == area
        ]

    def update_crowd_data(self, crowd_data: CrowdData):
        """更新客流数据"""
        self.current_crowd_data = crowd_data

    def get_queue_info(self, show_id: str) -> QueueInfo | None:
        """获取指定剧目的排队信息"""
        if self.current_crowd_data:
            return self.current_crowd_data.queue_data.get(show_id)
        return None

    def predict_wait_time(self, show_id: str, target_time: datetime) -> int:
        """
        预测指定时间的排队时长
        基于历史数据和当前客流情况
        """
        # 简化模型：基于时间段和座位占用率估算
        show = self.get_show(show_id)
        if not show:
            return 0

        # 找到最接近的时间安排
        closest_schedule = None
        for schedule in show.schedule:
            if schedule.start_time <= target_time <= schedule.end_time:
                closest_schedule = schedule
                break
            if schedule.start_time > target_time:
                closest_schedule = schedule
                break

        if not closest_schedule:
            return 0

        # 基于座位占用率估算排队时间
        occupancy_rate = closest_schedule.current_bookings / closest_schedule.capacity
        base_wait_time = 10  # 基础排队时间10分钟

        # 根据占用率调整
        if occupancy_rate > 0.9:
            return int(base_wait_time * 3)
        elif occupancy_rate > 0.7:
            return int(base_wait_time * 2)
        elif occupancy_rate > 0.5:
            return int(base_wait_time * 1.5)
        else:
            return base_wait_time

    def calculate_distance(self, loc1: Location, loc2: Location) -> float:
        """
        计算两个位置之间的距离（简化模型）
        实际应该使用真实的路径规划算法
        """
        # 使用简单的欧几里得距离作为示例
        lat1, lon1 = loc1.coordinates
        lat2, lon2 = loc2.coordinates
        distance = ((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2) ** 0.5
        # 转换为米（粗略估算）
        return distance * 111000  # 1度约等于111公里

    def calculate_walking_time(self, loc1: Location, loc2: Location) -> int:
        """计算步行时间（分钟）"""
        distance = self.calculate_distance(loc1, loc2)
        # 平均步行速度约5km/h，即83.3m/min
        walking_speed = 83.3
        return int(distance / walking_speed) + 2  # 加2分钟缓冲时间

    def get_available_shows_at_time(self, target_time: datetime) -> list[Show]:
        """获取指定时间可观看的剧目"""
        available_shows = []
        for show in self.shows.values():
            for schedule in show.schedule:
                # 检查是否在合适的时间范围内（提前30分钟可到达）
                arrival_window = timedelta(minutes=30)
                if (
                    schedule.start_time - arrival_window <= target_time
                    and schedule.end_time >= target_time
                    and schedule.is_available()
                ):
                    available_shows.append(show)
                    break
        return available_shows

    def export_data(self) -> dict[str, Any]:
        """导出所有数据"""
        return {
            "shows": {
                show_id: {
                    "show_id": show.show_id,
                    "name": show.name,
                    "location": show.location.name,
                    "content_tags": show.content_tags,
                    "duration_minutes": show.duration_minutes,
                    "description": show.description,
                    "rating": show.rating,
                }
                for show_id, show in self.shows.items()
            },
            "locations": {
                loc_id: {
                    "location_id": loc.location_id,
                    "name": loc.name,
                    "area": loc.area,
                    "coordinates": loc.coordinates,
                    "description": loc.description,
                }
                for loc_id, loc in self.locations.items()
            },
        }