# 廊坊红楼梦景区行程编排系统 - 项目总结

## 项目完成情况

✅ **已完成所有功能模块**

### 1. 项目结构

```
skill_project/hongloumeng-schedule/
├── __init__.py                 # 包初始化文件
├── README.md                   # 项目文档
├── models.py                   # 数据模型定义（10个核心数据类）
├── data_service.py            # 数据服务（剧目、位置、排队管理）
├── user_service.py            # 用户服务（用户信息、偏好管理）
├── schedule_service.py        # 行程编排核心服务
├── api.py                     # REST API接口
├── utils.py                   # 工具函数
├── test_system.py             # 测试脚本
└── skills/                    # Skills目录
    ├── __init__.py
    ├── schedule_planning.py   # 行程编排Skill
    ├── user_preference.py     # 用户偏好Skill
    ├── queue_prediction.py    # 排队预测Skill
    └── show_recommendation.py # 剧目推荐Skill
```

### 2. 核心功能模块

#### 数据模型 (models.py)
- **Location**: 位置信息（区域、坐标）
- **ShowSchedule**: 剧目时间安排
- **Show**: 剧目信息（名称、位置、标签、评分）
- **QueueInfo**: 排队信息（等待时间、客流级别）
- **TicketInfo**: 购票信息
- **UserPreferences**: 用户偏好（类型、区域、人数、优先级）
- **ConversationStyle**: 对话偏好（语言、语气、详细度）
- **User**: 用户信息
- **ItineraryItem**: 行程项目
- **Itinerary**: 行程安排

#### 数据服务 (data_service.py)
- 管理剧目数据（4个示例剧目）
- 管理位置数据（大观园、荣国府等）
- 预测排队时间（基于占用率）
- 计算位置距离和步行时间
- 提供数据查询和过滤功能

#### 用户服务 (user_service.py)
- 用户信息管理
- 偏好提取（从对话文本）
- 偏好更新
- 对话风格管理
- 历史记录管理

#### 行程编排服务 (schedule_service.py)
- 核心编排算法
- 基于偏好的剧目排序
- 时间冲突检测
- 排队时间优化
- 步行距离优化
- 评分和建议生成
- 实时推荐

### 3. Skills实现

#### Schedule Planning Skill
- **触发关键词**: 行程、规划、安排、游览、排队、时间表、路线
- **功能**: 编排完整行程、优化时间安排、生成建议
- **Handler**: SchedulePlanningSkillHandler

#### User Preference Skill
- **触发关键词**: 偏好、喜欢、设置、更新、我喜欢
- **功能**: 提取偏好、更新设置、管理对话风格
- **Handler**: UserPreferenceSkillHandler

#### Queue Prediction Skill
- **触发关键词**: 排队、等待、多久、人多、高峰
- **功能**: 预测排队时间、分析高峰时段、比较剧目排队
- **Handler**: QueuePredictionSkillHandler

#### Show Recommendation Skill
- **触发关键词**: 推荐、好看、热门、经典、选择
- **功能**: 个性化推荐、评分排序、类型筛选
- **Handler**: ShowRecommendationSkillHandler

### 4. API接口 (api.py)

已集成到主系统 (`skill_project/api/main.py`)

提供以下REST API：

- `POST /hongloumeng/schedule` - 创建行程
- `GET /hongloumeng/schedule/{user_id}` - 获取行程推荐
- `POST /hongloumeng/user` - 创建用户
- `GET /hongloumeng/user/{user_id}` - 获取用户信息
- `POST /hongloumeng/user/{user_id}/preference` - 更新偏好
- `GET /hongloumeng/shows` - 获取所有剧目
- `GET /hongloumeng/shows/{show_id}` - 获取指定剧目
- `POST /hongloumeng/queue-prediction` - 预测排队时间
- `GET /hongloumeng/locations` - 获取所有位置
- `GET /hongloumeng/recommendations/{user_id}` - 实时推荐

### 5. 示例数据

#### 剧目
1. **黛玉葬花** - 45分钟, 潇湘馆, 爱情/经典/诗词, 评分4.8
2. **宝黛初见** - 50分钟, 荣国府正厅, 爱情/经典/相遇, 评分4.9
3. **探春理家** - 40分钟, 荑国府正厅, 家族/管理/智慧, 评分4.5
4. **黛玉焚稿** - 60分钟, 潇湘馆, 爱情/悲剧/经典, 评分4.7

#### 区域
- **大观园**: 潇湘馆、蘅芜苑、大观园正门
- **荣国府**: 正厅

### 6. 核心算法

#### 行程编排算法
1. 根据用户偏好过滤剧目
2. 多维度评分排序（评分+偏好匹配+区域+座位）
3. 时间窗口匹配
4. 步行时间计算
5. 排队时间预测
6. 冲突检测和优化
7. 生成建议和评分

#### 排队预测算法
基于座位占用率：
- <30%: 低峰期，基础时间
- 30-50%: 平峰期，1.5倍时间
- 50-70%: 高峰期，2倍时间
- >70%: 极高峰期，3倍时间

#### 推荐算法
评分维度：
- 基础评分（20分）
- 内容匹配（25分/标签）
- 区域匹配（30分）
- 座位充足度（10分）
- 高评分热度（10-15分）

### 7. 与DeepAgent集成方式

```python
# 在SkillRegistry中注册Skills
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

# 或者直接使用Handlers
from skill_project.hongloumeng_schedule.skills import SchedulePlanningSkillHandler

handler = SchedulePlanningSkillHandler()
result = handler.execute(
    user_request="帮我安排行程",
    context={"user_id": "user_001"}
)
```

### 8. 技术特点

- **模块化设计**: 每个服务独立，易于扩展和维护
- **数据驱动**: 基于模拟数据，可替换为真实数据源
- **Skill化**: 每个功能封装为Skill，可被Agent调用
- **RESTful API**: 提供标准HTTP接口
- **智能优化**: 多维度评分和优化算法
- **个性化**: 支持用户偏好和对话风格定制

### 9. 使用示例

```python
# 创建行程
from skill_project.hongloumeng_schedule import ScheduleService
from datetime import date

service = ScheduleService()
itinerary = service.create_itinerary("user_001", date.today())

# 使用API
import requests

# 创建行程
response = requests.post(
    "http://localhost:8000/hongloumeng/schedule",
    json={
        "user_id": "user_001",
        "target_date": "2024-07-15",
        "preferred_show_types": ["爱情"],
        "group_size": 2
    }
)

# 获取推荐
response = requests.get(
    "http://localhost:8000/hongloumeng/recommendations/user_001"
)
```

### 10. 扩展建议

1. **数据持久化**: 连接真实数据库（MySQL/PostgreSQL）
2. **实时数据**: 接入客流监控系统
3. **路径规划**: 使用地图API计算真实步行时间
4. **机器学习**: 基于历史数据训练排队预测模型
5. **用户反馈**: 收集用户评分反馈优化推荐
6. **多语言**: 支持英文等其他语言
7. **移动端**: 开发小程序或APP

## 项目价值

- ✅ 完整的业务逻辑实现
- ✅ 可扩展的架构设计
- ✅ 与DeepAgent无缝集成
- ✅ 提供REST API接口
- ✅ 模拟数据便于测试
- ✅ 详细文档和示例

这个系统为廊坊红楼梦景区提供了一个完整的智能化行程编排解决方案，可以通过DeepAgent或直接API调用为用户提供个性化服务！