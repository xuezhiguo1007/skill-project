from __future__ import annotations

from functools import lru_cache

from skill_project.langgraph_skill.graph import build_demo_skill_graph


@lru_cache(maxsize=1)
def get_demo_skill_graph():
    return build_demo_skill_graph()


def run_skill_graph(user_request: str) -> dict[str, object]:
    graph = get_demo_skill_graph()
    result = graph.invoke({"user_request": user_request})
    return {
        "user_request": user_request,
        "available_skills": result.get("available_skills", []),
        "selected_skill": result.get("selected_skill"),
        "route_reason": result.get("route_reason"),
        "skill_context": result.get("skill_context"),
        "skill_result": result.get("skill_result"),
        "final_response": result.get("final_response"),
    }
