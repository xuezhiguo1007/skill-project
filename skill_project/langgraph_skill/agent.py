from __future__ import annotations

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from skill_project.langgraph_skill.middleware import SkillMiddleware
from skill_project.langgraph_skill.registry import SkillRegistry, create_demo_registry
from skill_project.langgraph_skill.state import SkillAgentState
from skill_project.langgraph_skill.tools import build_load_skill_tool


def create_skill_agent(model, registry: SkillRegistry | None = None):
    skill_registry = registry or create_demo_registry()
    middleware = SkillMiddleware(skill_registry)
    return create_agent(
        model=model,
        tools=[build_load_skill_tool(skill_registry)],
        system_prompt=(
            "You are a helpful assistant. "
            "Use available skills when the request needs domain-specific guidance."
        ),
        middleware=[middleware],
        state_schema=SkillAgentState,
        checkpointer=InMemorySaver(),
    )


def create_sql_skill_agent(model, registry: SkillRegistry):
    middleware = SkillMiddleware(registry)
    return create_agent(
        model=model,
        tools=[build_load_skill_tool(registry)],
        system_prompt=(
            "You are a SQL assistant that uses on-demand skills. "
            "Do not assume a domain skill upfront. "
            "First inspect the available skill descriptions from the system prompt. "
            "If the request is about business analytics SQL, inventory SQL, or another "
            "domain-specific workflow, call `load_skill` before answering. "
            "After loading a skill, use it to produce a concise, practical response "
            "that includes SQL or a SQL drafting plan when appropriate. "
            "If the request is ambiguous, state the assumptions clearly."
        ),
        middleware=[middleware],
        state_schema=SkillAgentState,
        checkpointer=InMemorySaver(),
    )
