"""廊坊红楼梦景区行程编排系统 API"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from skill_project.hongloumeng_schedule.schedule_service import ScheduleService
from skill_project.hongloumeng_schedule.user_service import UserService
from skill_project.hongloumeng_schedule.data_service import DataService


router = APIRouter(prefix="/hongloumeng", tags=["hongloumeng"])

# 初始化服务
schedule_service = ScheduleService()
user_service = UserService()
data_service = DataService()


# Request Models
class CreateItineraryRequest(BaseModel):
    """创建行程请求"""
    user_id: str = Field(..., description="用户ID")
    target_date: str = Field(..., description="目标日期 (YYYY-MM-DD)")
    preferred_show_types: list[str] | None = Field(default=None, description="喜欢的剧目类型")
    preferred_areas: list[str] | None = Field(default=None, description="喜欢的区域")
    group_size: int | None = Field(default=1, description="团队人数")
    priority: str | None = Field(default="balanced", description="优先级")


class UpdatePreferenceRequest(BaseModel):
    """更新偏好请求"""
    user_id: str = Field(..., description="用户ID")
    preferred_show_types: list[str] | None = None
    preferred_areas: list[str] | None = None
    group_size: int | None = None
    priority: str | None = None


class CreateUserRequest(BaseModel):
    """创建用户请求"""
    name: str = Field(..., description="用户姓名")


class QueuePredictionRequest(BaseModel):
    """排队预测请求"""
    show_id: str | None = Field(default=None, description="剧目ID")
    target_time: str | None = Field(default=None, description="目标时间")


# API Endpoints
@router.post("/schedule", response_model=dict[str, Any])
async def create_itinerary(request: CreateItineraryRequest):
    """创建行程安排"""
    try:
        target_date_obj = date.fromisoformat(request.target_date)

        # 如果有偏好信息，创建偏好对象
        preferences = None
        if request.preferred_show_types or request.preferred_areas:
            from skill_project.hongloumeng_schedule.models import UserPreferences
            preferences = UserPreferences(
                preferred_show_types=request.preferred_show_types or [],
                preferred_areas=request.preferred_areas or [],
                group_size=request.group_size or 1,
                priority=request.priority or "balanced",
            )

        itinerary = schedule_service.create_itinerary(
            user_id=request.user_id,
            target_date=target_date_obj,
            preferences=preferences,
        )

        if not itinerary:
            raise HTTPException(status_code=404, detail="无法创建行程")

        return {
            "success": True,
            "itinerary": itinerary.to_dict(),
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/schedule/{user_id}", response_model=dict[str, Any])
async def get_user_schedule(user_id: str, target_date: str = None):
    """获取用户行程"""
    try:
        target_date_obj = date.fromisoformat(target_date) if target_date else date.today()

        recommendations = schedule_service.get_real_time_recommendations(
            user_id=user_id,
            current_time=datetime.now(),
        )

        return {
            "success": True,
            "recommendations": recommendations,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/user", response_model=dict[str, Any])
async def create_user(request: CreateUserRequest):
    """创建用户"""
    user = user_service.create_user(name=request.name)

    return {
        "success": True,
        "user": user.to_dict(),
    }


@router.get("/user/{user_id}", response_model=dict[str, Any])
async def get_user(user_id: str):
    """获取用户信息"""
    user = user_service.get_user(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return {
        "success": True,
        "user": user.to_dict(),
    }


@router.post("/user/{user_id}/preference", response_model=dict[str, Any])
async def update_preference(user_id: str, request: UpdatePreferenceRequest):
    """更新用户偏好"""
    from skill_project.hongloumeng_schedule.models import UserPreferences

    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 更新偏好
    preferences = UserPreferences(
        preferred_show_types=request.preferred_show_types or user.preferences.preferred_show_types,
        preferred_areas=request.preferred_areas or user.preferences.preferred_areas,
        group_size=request.group_size or user.preferences.group_size,
        priority=request.priority or user.preferences.priority,
    )

    updated_user = user_service.update_user_preferences(user_id, preferences)

    return {
        "success": True,
        "user": updated_user.to_dict(),
    }


@router.get("/shows", response_model=dict[str, Any])
async def get_all_shows():
    """获取所有剧目"""
    shows = data_service.get_all_shows()

    return {
        "success": True,
        "shows": [
            {
                "show_id": show.show_id,
                "name": show.name,
                "location": show.location.name,
                "content_tags": show.content_tags,
                "duration_minutes": show.duration_minutes,
                "rating": show.rating,
                "description": show.description,
            }
            for show in shows
        ],
    }


@router.get("/shows/{show_id}", response_model=dict[str, Any])
async def get_show(show_id: str):
    """获取指定剧目"""
    show = data_service.get_show(show_id)

    if not show:
        raise HTTPException(status_code=404, detail="剧目不存在")

    return {
        "success": True,
        "show": {
            "show_id": show.show_id,
            "name": show.name,
            "location": show.location.name,
            "content_tags": show.content_tags,
            "duration_minutes": show.duration_minutes,
            "rating": show.rating,
            "description": show.description,
            "schedules": [
                {
                    "schedule_id": schedule.schedule_id,
                    "start_time": schedule.start_time.isoformat(),
                    "end_time": schedule.end_time.isoformat(),
                    "capacity": schedule.capacity,
                    "available_seats": schedule.available_seats,
                }
                for schedule in show.schedule
            ],
        },
    }


@router.post("/queue-prediction", response_model=dict[str, Any])
async def predict_queue(request: QueuePredictionRequest):
    """预测排队时间"""
    if request.target_time:
        target_time = datetime.fromisoformat(request.target_time)
    else:
        target_time = datetime.now()

    if request.show_id:
        show = data_service.get_show(request.show_id)
        if not show:
            raise HTTPException(status_code=404, detail="剧目不存在")

        wait_time = data_service.predict_wait_time(request.show_id, target_time)

        return {
            "success": True,
            "show_id": request.show_id,
            "show_name": show.name,
            "predicted_wait_time": wait_time,
            "target_time": target_time.isoformat(),
        }

    # 获取所有剧目的排队预测
    shows = data_service.get_all_shows()
    predictions = []

    for show in shows:
        wait_time = data_service.predict_wait_time(show.show_id, target_time)
        predictions.append({
            "show_id": show.show_id,
            "show_name": show.name,
            "predicted_wait_time": wait_time,
        })

    return {
        "success": True,
        "predictions": predictions,
        "target_time": target_time.isoformat(),
    }


@router.get("/locations", response_model=dict[str, Any])
async def get_all_locations():
    """获取所有位置"""
    locations = data_service.get_all_locations()

    return {
        "success": True,
        "locations": [
            {
                "location_id": loc.location_id,
                "name": loc.name,
                "area": loc.area,
                "coordinates": loc.coordinates,
                "description": loc.description,
            }
            for loc in locations
        ],
    }


@router.get("/recommendations/{user_id}", response_model=dict[str, Any])
async def get_recommendations(user_id: str):
    """获取实时推荐"""
    recommendations = schedule_service.get_real_time_recommendations(
        user_id=user_id,
        current_time=datetime.now(),
    )

    return {
        "success": True,
        "recommendations": recommendations,
    }