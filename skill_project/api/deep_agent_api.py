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
            summary="验证自定义提示词是否命中 skill",
            description=(
                "直接接收调用方传入的 prompt，并使用该 prompt 执行一次技能验证。"
                "适合调试任意自定义请求，观察代理是否会命中本地 skill 或子代理。"
                "请求中的 scenario 仅用于结果标记，不会参与 prompt 生成。"
            ),
        )
        self.router.add_api_route(
            "/api/v1/run-scenario",
            self.validate_scenario,
            methods=["POST"],
            response_model=CommonRes[ValidationResult],
            summary="运行预置场景验证",
            description=(
                "根据 scenario 名称从服务端预置场景中读取 prompt，再执行一次技能验证。"
                "适合跑固定样例、回归验证和对比不同模型在同一场景下的表现。"
                "该接口不接收自定义 prompt。"
            ),
        )

    async def get_skills(self) -> CommonRes[list[SkillItem]]:
        return CommonRes.success([SkillItem(**item) for item in list_skills()])

    async def get_scenarios(self) -> CommonRes[dict[str, dict[str, str]]]:
        return CommonRes.success(SCENARIOS)

    async def validate_skill(
        self,
        req: ValidateSkillReq,
    ) -> CommonRes[ValidationResult]:
        """使用调用方直接传入的 prompt 执行 skill 验证。"""
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
        """执行服务端预定义的场景，并返回场景标题、prompt 和响应结果。"""
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
