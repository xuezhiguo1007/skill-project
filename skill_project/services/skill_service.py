from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from skill_project import PROJECT_ROOT, SKILLS_DIR
from skill_project.core.config import SETTINGS

SCENARIOS = {
    "release": {
        "title": "模拟调用发布说明 skill",
        "prompt": (
            "请读取 data/releases/change-log.md，"
            "生成一份面向客户的 2026 年 4 月版本发布说明。"
            "输出必须使用中文 Markdown，并严格遵循对应 skill 中要求的结构。"
        ),
    },
    "support": {
        "title": "模拟调用客服分诊 skill",
        "prompt": (
            "请根据 data/support/refund-policy.md 判断下面这封客户邮件是否应该退款，"
            "并起草一封中文客服回复。"
            "如果需要，你可以把这项工作委托给更专业的客服支持子代理。\n\n"
            "客户邮件：\n"
            "我昨天刚续费年度套餐，结果今天团队决定停用。"
            "我几乎没有使用产品，只创建了 1 个项目。"
            "请问可以退款吗？如果不行，至少帮我降成月付。"
        ),
    },
    "dual-skills": {
        "title": "模拟调用两个 skills：发布说明 + 客服分诊",
        "prompt": (
            "请完成两个独立任务，并使用中文 Markdown 输出。"
            "最终结果必须包含两个一级标题：`# 版本发布说明` 和 `# 客服回复方案`。\n\n"
            "任务一：读取 data/releases/change-log.md，"
            "为 2026 年 4 月版本写一份面对客户的发布说明。\n\n"
            "任务二：读取 data/support/refund-policy.md，"
            "判断下面这封客户邮件是否符合退款条件，并起草客服回复。"
            "这部分如果更适合专业支持子代理处理，请直接委托。\n\n"
            "客户邮件：\n"
            "我们上周刚续费企业版，现在公司决定把团队收缩到 3 个人。"
            "目前只创建了 2 个项目，还没正式上线。"
            "如果能退掉年费最好；如果不能，请给我一个尽量稳妥的替代方案。"
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
            "当任务涉及版本发布说明、变更摘要、面向客户的更新介绍时，"
            "优先使用本地的发布说明 skill。"
            "当任务涉及退款判断、客服回复、政策解释、售后安抚时，"
            "优先委托客服支持子代理处理。"
            "如果用户一次要求多个交付物，请分节完成，并为每一部分使用最合适的 skill。"
        ),
        backend=backend,
        skills=["/skills"],
        subagents=[
            {
                "name": "support_triage_specialist",
                "description": (
                    "处理退款判断、售后咨询、政策解释、客服回复草拟等工作。"
                ),
                "system_prompt": (
                    "你是一名中文客服支持专家。"
                    "请严格依据退款政策判断，不要承诺政策之外的补偿。"
                    "输出必须清晰说明结论、依据和建议回复。"
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
