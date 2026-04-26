from __future__ import annotations

import logging

from fastapi import APIRouter

from skill_project.api.schemas import (
    CommonRes,
    EvolutionSkillEvolveReq,
    EvolutionSkillEvolveResult,
    EvolutionSkillItem,
    ResCodeEnum,
)
from skill_project.evolution_skill_loader import build_evolution_skill_service


class EvolutionSkillAPI:
    def __init__(self) -> None:
        self.router = APIRouter()
        self.service = build_evolution_skill_service()
        self._register_routes()

    def _register_routes(self) -> None:
        self.router.add_api_route(
            "/api/v1/evolution-skills",
            self.list_evolution_skills,
            methods=["GET"],
            response_model=CommonRes[list[EvolutionSkillItem]],
        )
        self.router.add_api_route(
            "/api/v1/evolution-skills/evolve",
            self.evolve_skill,
            methods=["POST"],
            response_model=CommonRes[EvolutionSkillEvolveResult],
        )

    async def list_evolution_skills(self) -> CommonRes[list[EvolutionSkillItem]]:
        try:
            items = [
                EvolutionSkillItem(**skill.to_dict())
                for skill in self.service.list_skills()
            ]
            return CommonRes.success(items)
        except Exception as exc:
            logging.exception("[list_evolution_skills] failed")
            return CommonRes.error(
                code=ResCodeEnum.COMMON_ERROR.code,
                message=str(exc),
            )

    async def evolve_skill(
        self,
        req: EvolutionSkillEvolveReq,
    ) -> CommonRes[EvolutionSkillEvolveResult]:
        logging.info("[evolve_skill] query=%s", req.query)
        try:
            result = self.service.evolve(req.query)
            return CommonRes.success(
                EvolutionSkillEvolveResult(
                    action=result["action"],
                    reason=result["reason"],
                    matched=result["matched"],
                    matched_score=result["matched_score"],
                    skill=EvolutionSkillItem(**result["skill"].to_dict()),
                )
            )
        except Exception as exc:
            logging.exception("[evolve_skill] failed")
            return CommonRes.error(
                code=ResCodeEnum.COMMON_ERROR.code,
                message=str(exc),
            )
