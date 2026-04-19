from __future__ import annotations

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from skill_project.langgraph_skill.middleware import SkillMiddleware
from skill_project.langgraph_skill.registry import SkillRegistry, create_demo_registry


def create_skill_agent(model, registry: SkillRegistry | None = None):
    skill_registry = registry or create_demo_registry()
    middleware = SkillMiddleware(skill_registry)
    return create_agent(
        model=model,
        system_prompt=(
            "You are a helpful assistant. "
            "Use available skills when the request needs domain-specific guidance."
        ),
        middleware=[middleware],
        checkpointer=InMemorySaver(),
    )
