from __future__ import annotations

from importlib import import_module
from typing import Any

__all__ = [
    "SkillRegistry",
    "SkillSpec",
    "SkillMiddleware",
    "build_demo_skill_graph",
    "build_load_skill_tool",
    "create_skill_agent",
    "create_demo_registry",
]


def __getattr__(name: str) -> Any:
    if name == "create_skill_agent":
        return import_module("skill_project.langgraph_skill.agent").create_skill_agent
    if name == "build_demo_skill_graph":
        return import_module(
            "skill_project.langgraph_skill.graph"
        ).build_demo_skill_graph
    if name == "SkillMiddleware":
        return import_module("skill_project.langgraph_skill.middleware").SkillMiddleware
    if name == "SkillSpec":
        return import_module("skill_project.langgraph_skill.models").SkillSpec
    if name in {"SkillRegistry", "create_demo_registry"}:
        module = import_module("skill_project.langgraph_skill.registry")
        return getattr(module, name)
    if name == "build_load_skill_tool":
        return import_module(
            "skill_project.langgraph_skill.tools"
        ).build_load_skill_tool
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
