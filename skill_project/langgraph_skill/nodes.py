from __future__ import annotations

from collections.abc import Callable

from skill_project.langgraph_skill.registry import SkillRegistry
from skill_project.langgraph_skill.state import SkillGraphState


def build_preprocess_node() -> Callable[[SkillGraphState], SkillGraphState]:
    def preprocess(state: SkillGraphState) -> SkillGraphState:
        request = state.get("user_request", "")
        return {
            "normalized_request": " ".join(request.strip().split()).lower(),
        }

    return preprocess


def build_available_skills_node(
    registry: SkillRegistry,
) -> Callable[[SkillGraphState], SkillGraphState]:
    def available_skills(_: SkillGraphState) -> SkillGraphState:
        return {
            "available_skills": registry.list_names(),
        }

    return available_skills


def build_skill_router_node(
    registry: SkillRegistry,
) -> Callable[[SkillGraphState], SkillGraphState]:
    def route(state: SkillGraphState) -> SkillGraphState:
        request = state.get("normalized_request") or state.get("user_request", "")
        matched = registry.match(request)
        if matched is None:
            return {
                "selected_skill": None,
                "route_reason": "No registered skill matched the current request.",
            }
        return {
            "selected_skill": matched.name,
            "route_reason": f"Matched skill `{matched.name}` by trigger keywords.",
        }

    return route


def build_skill_context_node(
    registry: SkillRegistry,
) -> Callable[[SkillGraphState], SkillGraphState]:
    def load_context(state: SkillGraphState) -> SkillGraphState:
        skill_name = state.get("selected_skill")
        if not skill_name:
            return {
                "skill_context": None,
                "loaded_skills": state.get("loaded_skills", []),
            }

        skill = registry.get(skill_name)
        if skill is None:
            return {
                "skill_context": None,
                "loaded_skills": state.get("loaded_skills", []),
            }

        loaded_skills = list(state.get("loaded_skills", []))
        if skill.name not in loaded_skills:
            loaded_skills.append(skill.name)

        context = (
            f"Skill: {skill.name}\n"
            f"Description: {skill.description}\n"
            f"When to use: {skill.when_to_use}\n"
            f"Execution notes: {skill.context_text}"
        )
        return {"skill_context": context, "loaded_skills": loaded_skills}

    return load_context


def build_context_skill_node(
    registry: SkillRegistry,
) -> Callable[[SkillGraphState], SkillGraphState]:
    def execute(state: SkillGraphState) -> SkillGraphState:
        skill_name = state.get("selected_skill")
        skill = registry.get(skill_name) if skill_name else None
        request = state.get("user_request", "")
        if skill is None:
            return {"skill_result": "No context skill was selected."}

        return {
            "skill_result": (
                f"[{skill.name}] 已命中上下文型 skill。\n"
                f"请求: {request}\n"
                f"执行提示:\n{state.get('skill_context', '')}"
            )
        }

    return execute


def build_default_response_node() -> Callable[[SkillGraphState], SkillGraphState]:
    def default_response(state: SkillGraphState) -> SkillGraphState:
        return {
            "final_response": (
                "当前请求没有命中任何已注册 skill。"
                "建议回退到默认 LangGraph agent 或普通业务流程。"
            )
        }

    return default_response


def build_finalize_node() -> Callable[[SkillGraphState], SkillGraphState]:
    def finalize(state: SkillGraphState) -> SkillGraphState:
        if state.get("final_response"):
            return {}

        route_reason = state.get("route_reason", "No route reason.")
        skill_result = state.get("skill_result", "")
        return {
            "final_response": f"{route_reason}\n\n{skill_result}".strip(),
        }

    return finalize
