from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from skill_project import PROJECT_ROOT, SKILLS_DIR
from skill_project.core.config import SETTINGS

SCENARIOS = {
    "itinerary": {
        "title": "模拟调用旅游行程规划 skill",
        "prompt": (
            "请读取 data/travel/destination-guide.md，"
            "为一对第一次去北海和涠洲岛的情侣规划四天三晚行程。"
            "要求节奏轻松，包含看海、拍照、海鲜和日落安排。"
            "输出必须使用中文 Markdown，并严格遵循对应 skill 中要求的结构。"
        ),
    },
    "shopping": {
        "title": "模拟调用旅游商品推荐 skill",
        "prompt": (
            "请读取 data/travel/shopping-guide.md，"
            "为准备去北海和涠洲岛玩四天三晚的女生朋友二人组推荐旅游商品。"
            "预算中等，重点考虑防晒、防水、拍照和少量伴手礼。"
            "输出必须使用中文 Markdown，并严格遵循对应 skill 中要求的结构。"
        ),
    },
    "dual-skills": {
        "title": "模拟调用两个 skills：行程规划 + 商品推荐",
        "prompt": (
            "请完成两个独立任务，并使用中文 Markdown 输出。"
            "最终结果必须包含两个一级标题：`# 旅游行程规划` 和 `# 旅游商品推荐`。\n\n"
            "任务一：读取 data/travel/destination-guide.md，"
            "为带一位长辈同行的家庭设计北海加涠洲岛四日行程，要求节奏不要太赶。\n\n"
            "任务二：读取 data/travel/shopping-guide.md，"
            "为这次出行推荐需要提前准备和适合在当地购买的商品。"
            "这部分如果更适合专业旅行购物顾问处理，请直接委托。"
        ),
    },
}


def extract_frontmatter(skill_file: Path) -> dict[str, str]:
    text = skill_file.read_text(encoding="utf-8")
    lines = text.splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        return {"name": skill_file.parent.name, "description": ""}

    metadata: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"')
    metadata.setdefault("name", skill_file.parent.name)
    metadata.setdefault("description", "")
    return metadata


def list_skills() -> list[dict[str, str]]:
    payload = []
    for skill_file in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        metadata = extract_frontmatter(skill_file)
        payload.append(
            {
                "name": metadata["name"],
                "description": metadata["description"],
                "path": str(skill_file.parent.relative_to(PROJECT_ROOT)),
            }
        )
    return payload


def require_openai_api_key() -> None:
    if os.getenv("OPENAI_API_KEY"):
        return
    raise RuntimeError("OPENAI_API_KEY is not set.")


def extract_text(message: object) -> str:
    content = getattr(message, "content", message)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
                continue
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(str(item.get("text", "")))
                continue
            text = getattr(item, "text", None)
            if text:
                parts.append(str(text))
        return "\n".join(part for part in parts if part)
    return str(content)


def build_agent(model_name: str | None = None) -> Any:
    from deepagents import create_deep_agent
    from deepagents.backends.filesystem import FilesystemBackend
    from langchain_openai import ChatOpenAI

    model = ChatOpenAI(model=model_name or SETTINGS.default_model, temperature=0)
    backend = FilesystemBackend(root_dir=PROJECT_ROOT, virtual_mode=True)

    return create_deep_agent(
        model=model,
        system_prompt=(
            "你是一个用于演示 deepagents 本地技能选择能力的中文智能代理。"
            "当任务涉及旅行天数安排、每日路线、景点串联、餐饮节奏或出行提醒时，"
            "优先使用本地的旅游行程规划 skill。"
            "当任务涉及旅行装备、伴手礼、预算内采购或商品准备清单时，"
            "优先委托旅游商品推荐子代理处理。"
            "如果用户一次要求多个交付物，请分节完成，并为每一部分使用最合适的 skill。"
        ),
        backend=backend,
        skills=["/skills"],
        subagents=[
            {
                "name": "travel_shopping_specialist",
                "description": (
                    "处理旅行商品推荐、出行装备建议、伴手礼清单和预算内采购建议。"
                ),
                "system_prompt": (
                    "你是一名中文旅行购物顾问。"
                    "请严格依据提供的旅行商品资料推荐，不要编造未提供的品牌和价格。"
                    "输出必须清晰说明推荐理由、预算取舍和购买提醒。"
                ),
                "skills": ["/skills"],
            }
        ],
    )


def run_validation(
    prompt: str,
    model_name: str | None = None,
    scenario: str | None = None,
) -> dict[str, Any]:
    require_openai_api_key()
    agent = build_agent(model_name)
    result = agent.invoke({"messages": [{"role": "user", "content": prompt}]})
    messages = result.get("messages", [])
    final_text = extract_text(messages[-1]) if messages else ""
    return {
        "scenario": scenario,
        "model": model_name or SETTINGS.default_model,
        "prompt": prompt,
        "response": final_text,
    }


def run_scenario(scenario: str, model_name: str | None = None) -> dict[str, Any]:
    scenario_config = SCENARIOS[scenario]
    validation_result = run_validation(
        prompt=scenario_config["prompt"],
        model_name=model_name,
        scenario=scenario,
    )
    validation_result["title"] = scenario_config["title"]
    return validation_result


def run_scenario_with_prompt(
    scenario: str,
    prompt: str,
    model_name: str | None = None,
) -> dict[str, Any]:
    scenario_config = SCENARIOS[scenario]
    validation_result = run_validation(
        prompt=prompt,
        model_name=model_name,
        scenario=scenario,
    )
    validation_result["title"] = scenario_config["title"]
    return validation_result
