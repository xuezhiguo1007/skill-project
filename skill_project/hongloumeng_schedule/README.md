# 廊坊红楼梦景区行程编排系统

## 项目简介

这个系统负责廊坊红楼梦景区的行程编排和排队项目管理，为用户提供个性化的游览体验。

## 核心功能

### 1. 剧目管理
- 管理每天的多场剧目演出
- 包含剧目的开始时间、结束时间、内容标签、位置信息
- 支持座位容量和预订管理

### 2. 排队时间预测
- 根据客流量预测排队时间
- 提供高峰时段分析
- 推荐最佳观演时间

### 3. 用户偏好管理
- 管理用户购票信息（身份信息）
- 存储用户偏好数据（剧目类型、区域偏好等）
- 支持个人对话偏好设置

### 4. 行程编排
- 根据用户偏好智能编排行程
- 考虑排队时间和步行距离
- 优化行程顺序和时间安排
- 生成个性化建议

## 系统架构

### 数据模型 (`models.py`)
- `Show`: 剧目信息
- `ShowSchedule`: 剧目时间安排
- `Location`: 位置信息
- `QueueInfo`: 排队信息
- `User`: 用户信息
- `UserPreferences`: 用户偏好
- `Itinerary`: 行程安排

### 服务层
- `DataService` (`data_service.py`): 管理剧目、位置、排队数据
- `UserService` (`user_service.py`): 管理用户信息和偏好
- `ScheduleService` (`schedule_service.py`): 行程编排核心算法

### Skills
系统提供4个独立的 Skills，可被 DeepAgent 调用：

1. **Schedule Planning Skill** (`skills/schedule_planning.py`)
   - 负责行程编排和规划
   - 触发关键词: 行程、规划、安排、游览、排队、时间表、路线

2. **User Preference Skill** (`skills/user_preference.py`)
   - 管理和分析用户偏好
   - 触发关键词: 偏好、喜欢、设置、更新、我喜欢

3. **Queue Prediction Skill** (`skills/queue_prediction.py`)
   - 预测排队时间和客流分析
   - 触发关键词: 排队、等待、多久、人多、高峰

4. **Show Recommendation Skill** (`skills/show_recommendation.py`)
   - 提供剧目推荐
   - 触发关键词: 推荐、好看、热门、经典、选择

## API 接口

### 行程相关
- `POST /hongloumeng/schedule`: 创建行程安排
- `GET /hongloumeng/schedule/{user_id}`: 获取用户行程推荐

### 用户相关
- `POST /hongloumeng/user`: 创建用户
- `GET /hongloumeng/user/{user_id}`: 获取用户信息
- `POST /hongloumeng/user/{user_id}/preference`: 更新用户偏好

### 剧目相关
- `GET /hongloumeng/shows`: 获取所有剧目
- `GET /hongloumeng/shows/{show_id}`: 获取指定剧目

### 排队预测
- `POST /hongloumeng/queue-prediction`: 预测排队时间

### 其他
- `GET /hongloumeng/locations`: 获取所有位置
- `GET /hongloumeng/recommendations/{user_id}`: 获取实时推荐

## 使用示例

### 1. 创建行程
```python
from datetime import date
from skill_project.hongloumeng_schedule.schedule_service import ScheduleService

schedule_service = ScheduleService()
itinerary = schedule_service.create_itinerary(
    user_id="user_001",
    target_date=date.today(),
)
```

### 2. 更新用户偏好
```python
from skill_project.hongloumeng_schedule.user_service import UserService
from skill_project.hongloumeng_schedule.models import UserPreferences

user_service = UserService()
preferences = UserPreferences(
    preferred_show_types=["爱情", "经典"],
    preferred_areas=["大观园"],
    group_size=2,
    priority="experience",
)
user = user_service.update_user_preferences("user_001", preferences)
```

### 3. 预测排队时间
```python
from datetime import datetime
from skill_project.hongloumeng_schedule.data_service import DataService

data_service = DataService()
wait_time = data_service.predict_wait_time(
    show_id="show_001",
    target_time=datetime.now(),
)
```

### 4. 使用 Skills
```python
from skill_project.hongloumeng_schedule.skills import (
    create_schedule_planning_skill,
    SchedulePlanningSkillHandler,
)

skill = create_schedule_planning_skill()
handler = SchedulePlanningSkillHandler()

result = handler.execute(
    user_request="帮我安排一天的游览行程",
    context={"user_id": "user_001", "target_date": date.today()},
)
```

## 与 DeepAgent 集成

每个 Skill 都提供 `SkillSpec` 对象，可以被 DeepAgent 加载和使用：

```python
from skill_project.langgraph_skill.registry import SkillRegistry
from skill_project.hongloumeng_schedule.skills import (
    create_schedule_planning_skill,
    create_user_preference_skill,
    create_queue_prediction_skill,
    create_show_recommendation_skill,
)

registry = SkillRegistry()
registry.register(create_schedule_planning_skill())
registry.register(create_user_preference_skill())
registry.register(create_queue_prediction_skill())
registry.register(create_show_recommendation_skill())
```

## 数据结构示例

### 剧目数据
- **黛玉葬花**: 45分钟，大观园-潇湘馆，爱情/经典/诗词
- **宝黛初见**: 50分钟，荣国府-正厅，爱情/经典/相遇
- **探春理家**: 40分钟，荣国府-正厅，家族/管理/智慧
- **黛玉焚稿**: 60分钟，大观园-潇湘馆，爱情/悲剧/经典

### 区域划分
- **大观园**: 潇湘馆、蘅芜苑等
- **荣国府**: 正厅等

## 扩展说明

系统采用模块化设计，易于扩展：
- 新增剧目类型只需更新 `data_service.py` 的模拟数据
- 新增推荐算法只需修改 `schedule_service.py` 的排序逻辑
- 新增 Skill 只需在 `skills/` 目录下添加新文件

## 注意事项

- 当前使用模拟数据，实际部署时需要连接真实数据库
- 排队时间预测基于简化模型，可根据实际数据优化算法
- 位置距离计算使用简化的欧几里得距离，实际应使用路径规划API