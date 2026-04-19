from __future__ import annotations

from skill_project.langgraph_skill.models import SkillSpec


class SkillRegistry:
    def __init__(self, skills: list[SkillSpec] | None = None):
        self._skills: dict[str, SkillSpec] = {}
        for skill in skills or []:
            self.register(skill)

    def register(self, skill: SkillSpec) -> None:
        self._skills[skill.name] = skill

    def get(self, name: str) -> SkillSpec | None:
        return self._skills.get(name)

    def list(self) -> list[SkillSpec]:
        return list(self._skills.values())

    def list_names(self) -> list[str]:
        return [skill.name for skill in self.list()]

    def match(self, request: str) -> SkillSpec | None:
        scored = [(skill.score(request), skill) for skill in self.list()]
        scored.sort(key=lambda item: item[0], reverse=True)
        best_score, best_skill = scored[0] if scored else (0, None)
        if not best_skill or best_score <= 0:
            return None
        return best_skill


def create_demo_registry() -> SkillRegistry:
    return SkillRegistry(
        [
            SkillSpec(
                name="travel_itinerary",
                description="为旅行场景生成按天拆分的轻量行程计划。",
                when_to_use="用户明确提到行程、天数安排、路线、景点串联、节奏规划时使用。",
                handler_type="subgraph",
                trigger_keywords=("行程", "路线", "景点", "几天", "旅游", "日程"),
                content=(
                    "# Travel Itinerary Skill\n"
                    "将用户需求整理成逐日行程。\n"
                    "输出必须分天展示，并补充上午、下午、晚上的安排建议。"
                ),
                context_text=(
                    "输出时优先按天拆分，并覆盖上午、下午、晚上安排。"
                    "同时补充交通节奏、用餐建议和一条出行提醒。"
                ),
                entrypoint="travel_itinerary",
            ),
            SkillSpec(
                name="travel_shopping",
                description="为旅行准备物品、装备和伴手礼建议。",
                when_to_use="用户明确提到购物清单、出行装备、防晒防水、伴手礼时使用。",
                handler_type="context",
                trigger_keywords=("购物", "装备", "伴手礼", "防晒", "防水", "准备什么"),
                content=(
                    "# Travel Shopping Skill\n"
                    "先区分出发前准备与当地购买，再按必要性和预算排序。"
                    "每项建议都要说明用途、预算档位和是否建议提前购买。"
                ),
                context_text=(
                    "输出时区分出发前准备和目的地当地购买，"
                    "每项建议都需要解释用途和预算取舍。"
                ),
            ),
        ]
    )
