from __future__ import annotations

import re
from collections import Counter

from skill_project.skill_evolution.models import SkillCandidate, TaskTrajectory

COMMON_STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "from",
    "into",
    "your",
    "have",
    "请",
    "帮我",
    "一个",
    "需要",
    "可以",
    "如何",
    "什么",
}


class SkillGenerator:
    """Distill repeated successful trajectories into a reusable skill draft."""

    def generate(
        self,
        trajectories: list[TaskTrajectory],
        *,
        skill_name: str | None = None,
        description: str | None = None,
    ) -> SkillCandidate:
        successful = [item for item in trajectories if item.succeeded]
        if not successful:
            raise ValueError("At least one successful trajectory is required.")

        inferred_name = skill_name or self._infer_skill_name(successful)
        inferred_description = description or self._infer_description(successful)
        when_to_use = self._build_when_to_use(successful)
        trigger_keywords = self._extract_keywords(successful)
        tool_hints = self._extract_tool_hints(successful)
        tags = self._extract_tags(successful)
        markdown = self._build_markdown(
            skill_name=inferred_name,
            description=inferred_description,
            when_to_use=when_to_use,
            trajectories=successful,
            trigger_keywords=trigger_keywords,
            tool_hints=tool_hints,
        )
        return SkillCandidate(
            skill_name=inferred_name,
            description=inferred_description,
            when_to_use=when_to_use,
            markdown=markdown,
            source_count=len(successful),
            trigger_keywords=trigger_keywords,
            tags=tags,
            tool_hints=tool_hints,
        )

    def _infer_skill_name(self, trajectories: list[TaskTrajectory]) -> str:
        keywords = self._extract_keywords(trajectories)
        base = "_".join(keywords[:3]) or "generated_skill"
        normalized = re.sub(r"[^a-z0-9_]+", "_", base.lower()).strip("_")
        return normalized or "generated_skill"

    def _infer_description(self, trajectories: list[TaskTrajectory]) -> str:
        tools = self._extract_tool_hints(trajectories)
        if tools:
            return f"为重复任务沉淀可复用流程，常配合 {', '.join(tools[:3])} 使用。"
        return "为重复成功任务沉淀步骤、风险和验收方式。"

    def _build_when_to_use(self, trajectories: list[TaskTrajectory]) -> str:
        requests = [item.request.strip() for item in trajectories[:3]]
        fragments = [f"类似“{text[:36]}”的问题" for text in requests if text]
        if not fragments:
            return "当任务多次重复出现，且需要稳定执行步骤和验收标准时使用。"
        return "当用户请求属于 " + "、".join(fragments) + " 这类场景时使用。"

    def _extract_keywords(self, trajectories: list[TaskTrajectory]) -> list[str]:
        counter: Counter[str] = Counter()
        for item in trajectories:
            for token in re.findall(
                r"[A-Za-z][A-Za-z0-9_]{2,}|[\u4e00-\u9fff]{2,8}", item.request
            ):
                lowered = token.lower()
                if lowered in COMMON_STOPWORDS:
                    continue
                counter[lowered] += 1
            for tag in item.tags:
                counter[tag.lower()] += 2
        return [word for word, _ in counter.most_common(8)]

    def _extract_tool_hints(self, trajectories: list[TaskTrajectory]) -> list[str]:
        counter: Counter[str] = Counter()
        for item in trajectories:
            for tool_name in item.tools_used:
                counter[tool_name] += 1
        return [tool_name for tool_name, _ in counter.most_common(6)]

    def _extract_tags(self, trajectories: list[TaskTrajectory]) -> list[str]:
        counter: Counter[str] = Counter()
        for item in trajectories:
            for tag in item.tags:
                counter[tag] += 1
        return [tag for tag, _ in counter.most_common(6)]

    def _build_markdown(
        self,
        *,
        skill_name: str,
        description: str,
        when_to_use: str,
        trajectories: list[TaskTrajectory],
        trigger_keywords: list[str],
        tool_hints: list[str],
    ) -> str:
        procedure_lines = [
            "1. 先复述目标、输入约束和输出格式，避免范围漂移。",
            "2. 提取关键实体、时间范围、过滤条件和验收标准。",
            "3. 优先复用已验证过的步骤，不要临场发明新流程。",
            "4. 如果上下文不足，先列出假设，再继续执行。",
            "5. 在最终输出前执行一次自检，确认覆盖关键字段和边界情况。",
        ]
        if tool_hints:
            procedure_lines.insert(
                3,
                f"4. 优先使用这些已证明有效的工具或能力：{', '.join(tool_hints)}。",
            )
        pitfalls = [
            "不要把一次性的用户细节固化为通用规则。",
            "不要跳过验证步骤，只凭表面相似就套模板。",
            "如果用户补充了纠正信息，应优先遵循纠正后的做法。",
        ]
        correction_lines = []
        for item in trajectories:
            correction_lines.extend(item.correction_notes)
        if correction_lines:
            unique_corrections = list(dict.fromkeys(correction_lines))
            pitfalls.extend(f"历史纠正：{note}" for note in unique_corrections[:3])

        example_requests = "\n".join(
            f"- {item.request.strip()}"
            for item in trajectories[:3]
            if item.request.strip()
        )
        verification = [
            "确认输出是否覆盖用户目标、关键约束和最终交付格式。",
            "确认没有引入与历史纠正相冲突的步骤。",
            "确认关键术语、字段名或实体名称前后一致。",
        ]
        keywords_text = ", ".join(trigger_keywords[:8]) or "无"
        return (
            f"# {skill_name}\n\n"
            f"## Description\n{description}\n\n"
            f"## When to Use\n{when_to_use}\n\n"
            f"## Trigger Keywords\n{keywords_text}\n\n"
            "## Procedure\n"
            + "\n".join(procedure_lines)
            + "\n\n## Pitfalls\n"
            + "\n".join(f"- {line}" for line in pitfalls)
            + "\n\n## Verification\n"
            + "\n".join(f"- {line}" for line in verification)
            + "\n\n## Example Requests\n"
            + (example_requests or "- 无")
            + "\n"
        )
