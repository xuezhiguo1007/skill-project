"""测试红楼梦景区行程编排系统"""
from __future__ import annotations

from datetime import date, datetime

from skill_project.hongloumeng_schedule.data_service import DataService
from skill_project.hongloumeng_schedule.user_service import UserService
from skill_project.hongloumeng_schedule.schedule_service import ScheduleService
from skill_project.hongloumeng_schedule.models import UserPreferences
from skill_project.hongloumeng_schedule.skills import (
    SchedulePlanningSkillHandler,
    UserPreferenceSkillHandler,
    QueuePredictionSkillHandler,
    ShowRecommendationSkillHandler,
)


def test_data_service():
    """测试数据服务"""
    print("=== 测试数据服务 ===")
    data_service = DataService()

    # 获取所有剧目
    shows = data_service.get_all_shows()
    print(f"共有 {len(shows)} 个剧目:")
    for show in shows:
        print(f"  - {show.name} ({show.location.name}, {show.duration_minutes}分钟, 评分{show.rating})")

    # 获取所有位置
    locations = data_service.get_all_locations()
    print(f"\n共有 {len(locations)} 个位置:")
    for loc in locations:
        print(f"  - {loc.name} ({loc.area})")

    # 预测排队时间
    wait_time = data_service.predict_wait_time("show_001", datetime.now())
    print(f"\n剧目 '黛玉葬花' 预估排队时间: {wait_time} 分钟")


def test_user_service():
    """测试用户服务"""
    print("\n=== 测试用户服务 ===")
    user_service = UserService()

    # 获取用户信息
    user = user_service.get_user("user_001")
    if user:
        print(f"用户: {user.name}")
        print(f"偏好: {user.preferences.preferred_show_types}")
        print(f"团队人数: {user.preferences.group_size}")

    # 从文本提取偏好
    preferences = user_service.extract_preferences_from_text(
        "我喜欢爱情类的剧目，我们一行4个人"
    )
    print(f"\n从文本提取的偏好:")
    print(f"  - 剧目类型: {preferences.preferred_show_types}")
    print(f"  - 团队人数: {preferences.group_size}")


def test_schedule_service():
    """测试行程编排服务"""
    print("\n=== 测试行程编排服务 ===")
    schedule_service = ScheduleService()

    # 创建行程
    itinerary = schedule_service.create_itinerary(
        user_id="user_001",
        target_date=date.today(),
    )

    if itinerary:
        print(f"行程ID: {itinerary.itinerary_id}")
        print(f"包含剧目数量: {len(itinerary.items)}")
        print(f"总排队时间: {itinerary.total_wait_time} 分钟")
        print(f"总观演时间: {itinerary.total_show_time} 分钟")
        print(f"优化评分: {itinerary.optimization_score:.2f}")

        print("\n行程详情:")
        for item in itinerary.items:
            print(f"  - {item.show.name}: {item.schedule.start_time.strftime('%H:%M')}-{item.schedule.end_time.strftime('%H:%M')}, 排队{item.estimated_wait_time}分钟")

        print("\n建议:")
        for suggestion in itinerary.suggestions:
            print(f"  - {suggestion}")


def test_skills():
    """测试Skills"""
    print("\n=== 测试Skills ===")

    # 测试行程编排Skill
    print("\n1. 行程编排Skill:")
    schedule_handler = SchedulePlanningSkillHandler()
    result = schedule_handler.execute(
        user_request="帮我安排一天的游览行程",
        context={"user_id": "user_001", "target_date": date.today()},
    )
    print(f"  - 结果: {result['success']}")
    print(f"  - 消息: {result['message']}")

    # 测试用户偏好Skill
    print("\n2. 用户偏好Skill:")
    preference_handler = UserPreferenceSkillHandler()
    result = preference_handler.execute(
        user_request="我喜欢爱情类的剧目，我们4个人",
        context={"user_id": "user_001"},
    )
    print(f"  - 结果: {result['success']}")
    print(f"  - 提取的偏好: {result['extracted_preferences']}")

    # 测试排队预测Skill
    print("\n3. 排队预测Skill:")
    queue_handler = QueuePredictionSkillHandler()
    result = queue_handler.execute(
        user_request="现在排队要多长时间",
        context={"show_id": "show_001"},
    )
    print(f"  - 结果: {result['success']}")
    print(f"  - 消息: {result['message']}")

    # 测试剧目推荐Skill
    print("\n4. 剧目推荐Skill:")
    recommendation_handler = ShowRecommendationSkillHandler()
    result = recommendation_handler.execute(
        user_request="推荐几个好看的剧目",
        context={"user_id": "user_001", "limit": 3},
    )
    print(f"  - 结果: {result['success']}")
    print(f"  - 推荐数量: {len(result['recommendations'])}")
    for rec in result['recommendations']:
        print(f"    - {rec['show_name']} (评分{rec['rating']}, 推荐理由: {rec['recommendation_reason']})")


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("廊坊红楼梦景区行程编排系统测试")
    print("=" * 60)

    test_data_service()
    test_user_service()
    test_schedule_service()
    test_skills()

    print("\n" + "=" * 60)
    print("所有测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()