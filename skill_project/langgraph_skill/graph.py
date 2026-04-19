from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from skill_project.langgraph_skill.example_skills import (
    build_travel_itinerary_skill_graph,
)
from skill_project.langgraph_skill.nodes import (
    build_available_skills_node,
    build_context_skill_node,
    build_default_response_node,
    build_finalize_node,
    build_preprocess_node,
    build_skill_context_node,
    build_skill_router_node,
)
from skill_project.langgraph_skill.registry import SkillRegistry, create_demo_registry
from skill_project.langgraph_skill.state import SkillGraphState


def _route_after_router(state: SkillGraphState) -> str:
    selected_skill = state.get("selected_skill")
    if selected_skill == "travel_itinerary":
        return "travel_itinerary"
    if selected_skill == "travel_shopping":
        return "travel_shopping"
    return "default"


def build_demo_skill_graph(registry: SkillRegistry | None = None):
    skill_registry = registry or create_demo_registry()
    itinerary_graph = build_travel_itinerary_skill_graph()

    graph = StateGraph(SkillGraphState)
    graph.add_node("preprocess", build_preprocess_node())
    graph.add_node("available_skills", build_available_skills_node(skill_registry))
    graph.add_node("skill_router", build_skill_router_node(skill_registry))
    graph.add_node("load_skill_context", build_skill_context_node(skill_registry))
    graph.add_node("context_skill_executor", build_context_skill_node(skill_registry))
    graph.add_node("default_response", build_default_response_node())
    graph.add_node("finalize", build_finalize_node())
    graph.add_node("travel_itinerary_skill", itinerary_graph)

    graph.add_edge(START, "preprocess")
    graph.add_edge("preprocess", "available_skills")
    graph.add_edge("available_skills", "skill_router")
    graph.add_conditional_edges(
        "skill_router",
        _route_after_router,
        {
            "travel_itinerary": "load_skill_context",
            "travel_shopping": "load_skill_context",
            "default": "default_response",
        },
    )
    graph.add_conditional_edges(
        "load_skill_context",
        _route_after_router,
        {
            "travel_itinerary": "travel_itinerary_skill",
            "travel_shopping": "context_skill_executor",
            "default": "default_response",
        },
    )
    graph.add_edge("travel_itinerary_skill", "finalize")
    graph.add_edge("context_skill_executor", "finalize")
    graph.add_edge("default_response", END)
    graph.add_edge("finalize", END)
    return graph.compile()


def build_context_demo_skill_graph(registry: SkillRegistry):
    graph = StateGraph(SkillGraphState)
    graph.add_node("preprocess", build_preprocess_node())
    graph.add_node("available_skills", build_available_skills_node(registry))
    graph.add_node("skill_router", build_skill_router_node(registry))
    graph.add_node("load_skill_context", build_skill_context_node(registry))
    graph.add_node("context_skill_executor", build_context_skill_node(registry))
    graph.add_node("default_response", build_default_response_node())
    graph.add_node("finalize", build_finalize_node())

    graph.add_edge(START, "preprocess")
    graph.add_edge("preprocess", "available_skills")
    graph.add_edge("available_skills", "skill_router")
    graph.add_conditional_edges(
        "skill_router",
        lambda state: "context" if state.get("selected_skill") else "default",
        {
            "context": "load_skill_context",
            "default": "default_response",
        },
    )
    graph.add_edge("load_skill_context", "context_skill_executor")
    graph.add_edge("context_skill_executor", "finalize")
    graph.add_edge("default_response", END)
    graph.add_edge("finalize", END)
    return graph.compile()
