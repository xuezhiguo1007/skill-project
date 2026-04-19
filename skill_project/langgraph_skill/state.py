from __future__ import annotations

from typing import TypedDict

from langchain.agents import AgentState


class SkillGraphState(TypedDict, total=False):
    user_request: str
    normalized_request: str
    available_skills: list[str]
    selected_skill: str | None
    loaded_skills: list[str]
    route_reason: str | None
    skill_context: str | None
    skill_result: str | None
    final_response: str | None


class SkillAgentState(AgentState, total=False):
    loaded_skills: list[str]
    selected_skill: str | None
    skill_context: str | None
