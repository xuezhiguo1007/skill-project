from __future__ import annotations

import importlib
import importlib.metadata
import logging

from fastapi import APIRouter

from skill_project.api.schemas import (
    CommonRes,
    DeepAgentProfileCheckReq,
    DeepAgentProfileCheckResult,
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
        self.router.add_api_route(
            "/api/v1/deep-agent/profile-check",
            self.check_profile_config,
            methods=["POST"],
            response_model=CommonRes[DeepAgentProfileCheckResult],
            summary="验证 DeepAgents profiles 配置能力",
            description=(
                "检查当前 deepagents 版本是否支持 HarnessProfileConfig 和 "
                "register_harness_profile。支持时会注册一份测试配置；不支持时返回"
                "缺失符号和版本诊断。该接口不调用模型。"
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

    async def check_profile_config(
        self,
        req: DeepAgentProfileCheckReq,
    ) -> CommonRes[DeepAgentProfileCheckResult]:
        """验证当前 deepagents profiles API 是否可用，并尝试注册测试配置。"""
        logging.info("[check_profile_config] profile_key=%s", req.profile_key)
        try:
            result = self._check_profile_config(req)
            return CommonRes.success(result)
        except Exception as exc:
            logging.exception("[check_profile_config] failed")
            return CommonRes.error(
                code=ResCodeEnum.COMMON_ERROR.code,
                message=str(exc),
            )

    def _check_profile_config(
        self,
        req: DeepAgentProfileCheckReq,
    ) -> DeepAgentProfileCheckResult:
        required_symbols = [
            "HarnessProfileConfig",
            "register_harness_profile",
        ]
        version = importlib.metadata.version("deepagents")
        required_version = ">=0.5.4"

        deepagents = importlib.import_module("deepagents")
        missing_symbols = [
            symbol for symbol in required_symbols if not hasattr(deepagents, symbol)
        ]
        config = {
            "system_prompt_suffix": req.system_prompt_suffix,
            "excluded_tools": req.excluded_tools,
            "excluded_middleware": req.excluded_middleware,
            "general_purpose_subagent": {
                "enabled": not req.disable_general_purpose_subagent
            },
        }

        if missing_symbols:
            return DeepAgentProfileCheckResult(
                deepagents_version=version,
                required_version=required_version,
                supported=False,
                registered=False,
                profile_key=req.profile_key,
                config=config,
                message=(
                    "Current deepagents package does not expose the documented "
                    "profiles API. Upgrade deepagents before using YAML/JSON "
                    "HarnessProfileConfig registration."
                ),
                missing_symbols=missing_symbols,
            )

        profile_config_cls = getattr(deepagents, "HarnessProfileConfig")
        register_harness_profile = getattr(deepagents, "register_harness_profile")
        register_harness_profile(
            req.profile_key,
            profile_config_cls.from_dict(config),
        )

        return DeepAgentProfileCheckResult(
            deepagents_version=version,
            required_version=required_version,
            supported=True,
            registered=True,
            profile_key=req.profile_key,
            config=config,
            message="Harness profile config registered successfully.",
        )
