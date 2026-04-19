from __future__ import annotations

import logging

from fastapi import APIRouter

from skill_project.api.schemas import (
    CommonRes,
    ResCodeEnum,
    ScenarioRunReq,
    SkillItem,
    ValidateSkillReq,
    ValidationResult,
)
from skill_project.services.skill_service import (
    SCENARIOS,
    list_skills,
    run_scenario,
    run_validation,
)


class DeepAgentAPI:
    def __init__(self) -> None:
        self.router = APIRouter()
        self._register_routes()

    def _register_routes(self) -> None:
        self.router.add_api_route(
            "/api/v1/skills",
            self.get_skills,
            methods=["GET"],
            response_model=CommonRes[list[SkillItem]],
        )
        self.router.add_api_route(
            "/api/v1/scenarios",
            self.get_scenarios,
            methods=["GET"],
            response_model=CommonRes[dict[str, dict[str, str]]],
        )
        self.router.add_api_route(
            "/api/v1/validate-skill",
            self.validate_skill,
            methods=["POST"],
            response_model=CommonRes[ValidationResult],
        )
        self.router.add_api_route(
            "/api/v1/run-scenario",
            self.validate_scenario,
            methods=["POST"],
            response_model=CommonRes[ValidationResult],
        )

    async def get_skills(self) -> CommonRes[list[SkillItem]]:
        return CommonRes.success([SkillItem(**item) for item in list_skills()])

    async def get_scenarios(self) -> CommonRes[dict[str, dict[str, str]]]:
        return CommonRes.success(SCENARIOS)

    async def validate_skill(
        self,
        req: ValidateSkillReq,
    ) -> CommonRes[ValidationResult]:
        logging.info("[validate_skill] scenario=%s model=%s", req.scenario, req.model)
        try:
            result = run_validation(
                prompt=req.prompt,
                model_name=req.model,
                scenario=req.scenario,
            )
            return CommonRes.success(ValidationResult(**result))
        except Exception as exc:
            logging.exception("[validate_skill] failed")
            return CommonRes.error(
                code=ResCodeEnum.COMMON_ERROR.code,
                message=str(exc),
            )

    async def validate_scenario(
        self,
        req: ScenarioRunReq,
    ) -> CommonRes[ValidationResult]:
        logging.info(
            "[validate_scenario] scenario=%s model=%s", req.scenario, req.model
        )
        try:
            result = run_scenario(
                scenario=req.scenario,
                model_name=req.model,
            )
            return CommonRes.success(ValidationResult(**result))
        except Exception as exc:
            logging.exception("[validate_scenario] failed")
            return CommonRes.error(
                code=ResCodeEnum.COMMON_ERROR.code,
                message=str(exc),
            )
