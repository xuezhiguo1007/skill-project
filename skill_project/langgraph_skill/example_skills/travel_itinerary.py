from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from skill_project.langgraph_skill.state import SkillGraphState


def _draft_itinerary(state: SkillGraphState) -> SkillGraphState:
    request = state.get("user_request", "")
    context = state.get("skill_context", "")
    return {
        "skill_result": (
            "# 旅游行程规划\n\n"
            f"原始需求：{request}\n\n"
            "## 第一天\n"
            "上午：抵达并入住，安排轻量活动。\n"
            "下午：前往核心景点，控制步行强度。\n"
            "晚上：预留海边散步和本地晚餐。\n\n"
            "## 第二天\n"
            "上午：主景点深度游。\n"
            "下午：补充拍照和休息时间。\n"
            "晚上：安排日落或夜景。\n\n"
            "## 出行提醒\n"
            f"{context}"
        )
    }


def build_travel_itinerary_skill_graph():
    graph = StateGraph(SkillGraphState)
    graph.add_node("draft_itinerary", _draft_itinerary)
    graph.add_edge(START, "draft_itinerary")
    graph.add_edge("draft_itinerary", END)
    return graph.compile()
