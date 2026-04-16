import logging

from fastapi import FastAPI

from skill_project.api.lifespan import lifespan_manager
from skill_project.api.schemas import (
    CommonRes,
    ResCodeEnum,
    ScenarioRunReq,
    SkillItem,
    ValidateSkillReq,
    ValidationResult,
)
from skill_project.core.config import SETTINGS
from skill_project.services.skill_service import SCENARIOS, list_skills, run_scenario, run_validation

app = FastAPI(
    title=SETTINGS.api_title,
    description=SETTINGS.api_description,
    version=SETTINGS.api_version,
    lifespan=lifespan_manager,
)


@app.get("/health")
async def health() -> CommonRes[dict[str, str]]:
    return CommonRes.success({"status": "ok"})


@app.get("/api/v1/skills")
async def get_skills() -> CommonRes[list[SkillItem]]:
    return CommonRes.success([SkillItem(**item) for item in list_skills()])


@app.get("/api/v1/scenarios")
async def get_scenarios() -> CommonRes[dict[str, dict[str, str]]]:
    return CommonRes.success(SCENARIOS)


@app.post("/api/v1/validate-skill")
async def validate_skill(req: ValidateSkillReq) -> CommonRes[ValidationResult]:
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


@app.post("/api/v1/run-scenario")
async def validate_scenario(req: ScenarioRunReq) -> CommonRes[ValidationResult]:
    logging.info("[validate_scenario] scenario=%s model=%s", req.scenario, req.model)
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
