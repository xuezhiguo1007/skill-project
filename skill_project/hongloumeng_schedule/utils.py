"""工具函数"""
from __future__ import annotations

import re
from datetime import datetime
from typing import Any


def parse_time_from_text(text: str) -> datetime | None:
    """从文本中解析时间"""
    # 匹配常见的中文时间格式
    patterns = [
        r"(\d{1,2})点(\d{1,2})分",
        r"(\d{1,2}):(\d{1,2})",
        r"(\d{1,2})点",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2)) if len(match.groups()) > 1 else 0
            # 使用今天的日期
            return datetime.now().replace(hour=hour, minute=minute, second=0)

    return None


def parse_date_from_text(text: str) -> datetime | None:
    """从文本中解析日期"""
    # 匹配常见的中文日期格式
    patterns = [
        r"(\d{4})年(\d{1,2})月(\d{1,2})日",
        r"(\d{4})-(\d{1,2})-(\d{1,2})",
        r"(\d{1,2})月(\d{1,2})日",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            if len(match.groups()) == 3:
                year = int(match.group(1)) if match.lastindex == 3 else datetime.now().year
                month = int(match.group(2))
                day = int(match.group(3))
                return datetime(year, month, day)

    # 检查关键词
    if "今天" in text:
        return datetime.now()
    elif "明天" in text:
        return datetime.now() + __import__('datetime').timedelta(days=1)
    elif "后天" in text:
        return datetime.now() + __import__('datetime').timedelta(days=2)

    return None


def extract_number_from_text(text: str) -> int:
    """从文本中提取数字"""
    patterns = [
        r"(\d+)人",
        r"(\d+)个",
        r"(\d+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))

    return 1


def format_time_range(start: datetime, end: datetime) -> str:
    """格式化时间范围"""
    start_str = start.strftime("%H:%M")
    end_str = end.strftime("%H:%M")
    return f"{start_str}-{end_str}"


def format_duration(minutes: int) -> str:
    """格式化时长"""
    if minutes < 60:
        return f"{minutes}分钟"
    hours = minutes // 60
    remaining_minutes = minutes % 60
    if remaining_minutes == 0:
        return f"{hours}小时"
    return f"{hours}小时{remaining_minutes}分钟"


def calculate_crowd_level(occupancy_rate: float) -> str:
    """计算客流级别"""
    if occupancy_rate < 0.3:
        return "low"
    elif occupancy_rate < 0.5:
        return "medium"
    elif occupancy_rate < 0.7:
        return "high"
    else:
        return "peak"


def generate_response_with_style(
    message: str,
    tone: str = "friendly",
    detail_level: str = "medium",
    emoji_usage: bool = False,
) -> str:
    """根据对话风格生成响应"""
    # 根据语气调整
    if tone == "professional":
        prefix = ""
    elif tone == "friendly":
        prefix = "您好，" if emoji_usage else "你好，"
    else:
        prefix = ""

    # 根据详细程度调整
    if detail_level == "brief":
        suffix = ""
    elif detail_level == "detailed":
        suffix = "如有其他需要，请随时告诉我。"
    else:
        suffix = ""

    # 添加表情符号
    if emoji_usage:
        emojis = {
            "friendly": "😊",
            "professional": "",
            "casual": "😄",
        }
        emoji = emojis.get(tone, "")
        if emoji:
            message = f"{message} {emoji}"

    return f"{prefix}{message}{suffix}"


def validate_user_input(input_data: dict[str, Any]) -> bool:
    """验证用户输入"""
    required_fields = ["user_id"]

    for field in required_fields:
        if field not in input_data:
            return False

    return True


def sanitize_text(text: str) -> str:
    """清理文本"""
    # 移除多余的空格
    text = " ".join(text.split())
    # 移除特殊字符（保留中文、英文、数字）
    text = re.sub(r"[^\w\s\u4e00-\u9fff]", "", text)
    return text.strip()