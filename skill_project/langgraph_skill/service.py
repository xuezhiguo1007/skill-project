from __future__ import annotations

from functools import lru_cache

from skill_project.llm import create_chat_model
from skill_project.services.skill_service import extract_text
from skill_project.langgraph_skill.agent import create_sql_skill_agent
from skill_project.langgraph_skill.graph import (
    build_context_demo_skill_graph,
    build_demo_skill_graph,
)
from skill_project.langgraph_skill.registry import create_sql_demo_registry


@lru_cache(maxsize=1)
def get_demo_skill_graph():
    return build_demo_skill_graph()


@lru_cache(maxsize=1)
def get_sql_demo_skill_graph():
    return build_context_demo_skill_graph(create_sql_demo_registry())


def run_skill_graph(user_request: str) -> dict[str, object]:
    graph = get_demo_skill_graph()
    result = graph.invoke({"user_request": user_request})
    return {
        "user_request": user_request,
        "available_skills": result.get("available_skills", []),
        "selected_skill": result.get("selected_skill"),
        "loaded_skills": result.get("loaded_skills", []),
        "route_reason": result.get("route_reason"),
        "skill_context": result.get("skill_context"),
        "skill_result": result.get("skill_result"),
        "final_response": result.get("final_response"),
    }


def run_sql_skill_graph(user_request: str) -> dict[str, object]:
    graph = get_sql_demo_skill_graph()
    result = graph.invoke({"user_request": user_request})
    return {
        "user_request": user_request,
        "available_skills": result.get("available_skills", []),
        "selected_skill": result.get("selected_skill"),
        "loaded_skills": result.get("loaded_skills", []),
        "route_reason": result.get("route_reason"),
        "skill_context": result.get("skill_context"),
        "skill_result": result.get("skill_result"),
        "final_response": result.get("final_response"),
    }


def run_sql_skill_agent(
    user_request: str,
    model_name: str | None = None,
) -> dict[str, object]:
    registry = create_sql_demo_registry()
    model = create_chat_model(model_name)
    agent = create_sql_skill_agent(model=model, registry=registry)
    result = agent.invoke(
        {
            "messages": [{"role": "user", "content": user_request}],
            "loaded_skills": [],
        },
        config={"configurable": {"thread_id": "langgraph-sql-skill-demo"}},
    )
    messages = result.get("messages", [])
    final_response = extract_text(messages[-1]) if messages else ""
    return {
        "user_request": user_request,
        "available_skills": registry.list_names(),
        "selected_skill": result.get("selected_skill"),
        "loaded_skills": result.get("loaded_skills", []),
        "route_reason": (
            f"Loaded skill(s): {', '.join(result.get('loaded_skills', []))}."
            if result.get("loaded_skills")
            else "No skill was loaded by the SQL assistant."
        ),
        "skill_context": result.get("skill_context"),
        "skill_result": None,
        "final_response": final_response,
    }
