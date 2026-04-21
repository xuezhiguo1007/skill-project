from __future__ import annotations

from langchain.tools import ToolRuntime, tool
from langchain_core.messages import ToolMessage
from langgraph.types import Command

from skill_project.langgraph_skill.registry import SkillRegistry, create_demo_registry


def build_load_skill_tool(registry: SkillRegistry | None = None):
    skill_registry = registry or create_demo_registry()

    @tool
    def load_skill(skill_name: str, runtime: ToolRuntime) -> Command:
        """Load the full content of a skill into the current agent context."""
        tool_call_id = runtime.tool_call_id or "load_skill"
        skill = skill_registry.get(skill_name)
        if skill is None:
            available = ", ".join(skill_registry.list_names())
            message = f"Skill '{skill_name}' not found. Available skills: {available}"
            return Command(
                update={
                    "messages": [
                        ToolMessage(message, tool_call_id=tool_call_id),
                    ],
                    "loaded_skills": runtime.state.get("loaded_skills", []),
                },
                goto=(),
                resume=message,
            )

        loaded_skills = list(runtime.state.get("loaded_skills", []))
        if skill.name not in loaded_skills:
            loaded_skills.append(skill.name)

        message = (
            f"Loaded skill: {skill.name}\n\n"
            f"Description: {skill.description}\n"
            f"When to use: {skill.when_to_use}\n\n"
            f"{skill.content}"
        )
        return Command(
            update={
                "messages": [
                    ToolMessage(message, tool_call_id=tool_call_id),
                ],
                "loaded_skills": loaded_skills,
                "selected_skill": skill.name,
                "skill_context": skill.content,
            },
            goto=(),
            resume=message,
        )

    return load_skill
