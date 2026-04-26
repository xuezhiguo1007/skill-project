from __future__ import annotations

from skill_project.evolution_skill_loader import build_evolution_skill_service
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


def build_registry(
    base_skills: list[SkillSpec],
    *,
    include_generated_skills: bool = True,
) -> SkillRegistry:
    merged_skills = list(base_skills)
    if include_generated_skills:
        existing_names = {skill.name for skill in merged_skills}
        for skill in build_evolution_skill_service().load_skill_specs():
            if skill.name in existing_names:
                continue
            merged_skills.append(skill)
    return SkillRegistry(merged_skills)


def create_demo_registry() -> SkillRegistry:
    return build_registry(
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


def create_sql_demo_registry() -> SkillRegistry:
    return build_registry(
        [
            SkillSpec(
                name="sales_analytics",
                description="分析订单、收入、客单价和时间趋势类 SQL 需求。",
                when_to_use=(
                    "用户提到销售额、营收、订单量、按月趋势、Top customers、"
                    "按地区汇总等分析型 SQL 问题时使用。"
                ),
                handler_type="context",
                trigger_keywords=(
                    "sales",
                    "revenue",
                    "order",
                    "orders",
                    "gmv",
                    "monthly",
                    "trend",
                    "customer",
                    "customers",
                    "region",
                    "销售额",
                    "营收",
                    "订单",
                    "趋势",
                    "客户",
                    "地区",
                ),
                content=(
                    "# Sales Analytics Skill\n"
                    "You are working on analytical SQL for business reporting.\n"
                    "Prefer aggregation queries over raw row dumps.\n"
                    "Validate the time grain first, then identify metrics, dimensions, "
                    "and filters before drafting SQL.\n"
                    "When useful, explain likely tables such as `orders`, `order_items`, "
                    "`customers`, and `products`."
                ),
                context_text=(
                    "回答时先澄清指标、时间粒度和过滤条件，再给出 SQL 思路。"
                    "优先生成适合分析的聚合查询，并提示可能涉及的事实表和维表。"
                ),
            ),
            SkillSpec(
                name="inventory_management",
                description="处理库存、补货、缺货风险和仓库维度的 SQL 需求。",
                when_to_use=(
                    "用户提到库存余量、补货建议、低库存、仓库状态、SKU 库存周转、"
                    "缺货预警等运维型 SQL 问题时使用。"
                ),
                handler_type="context",
                trigger_keywords=(
                    "inventory",
                    "stock",
                    "warehouse",
                    "reorder",
                    "restock",
                    "sku",
                    "low stock",
                    "库存",
                    "仓库",
                    "补货",
                    "缺货",
                    "sku",
                ),
                content=(
                    "# Inventory Management Skill\n"
                    "You are working on operational SQL for inventory workflows.\n"
                    "Focus on current stock, reorder thresholds, warehouse balances, "
                    "and SKU-level exceptions.\n"
                    "Highlight joins that commonly involve `inventory`, `warehouses`, "
                    "`products`, and `purchase_orders`."
                ),
                context_text=(
                    "回答时优先识别库存快照口径、补货阈值和仓库维度。"
                    "如果需求像运营看板，优先输出按 SKU 或仓库汇总的 SQL。"
                ),
            ),
        ]
    )
