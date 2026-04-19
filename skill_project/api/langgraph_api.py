from __future__ import annotations

import logging

from fastapi import APIRouter

from skill_project.api.schemas import (
    CommonRes,
    LangGraphSkillReq,
    LangGraphSkillResult,
    ResCodeEnum,
)
from skill_project.langgraph_skill.service import run_skill_graph


class LangGraphAPI:
    def __init__(self) -> None:
        self.router = APIRouter()
        self._register_routes()

    def _register_routes(self) -> None:
        self.router.add_api_route(
            "/api/v1/langgraph-skill",
            self.run_langgraph_skill,
            methods=["POST"],
            response_model=CommonRes[LangGraphSkillResult],
        )

    async def run_langgraph_skill(
        self,
        req: LangGraphSkillReq,
    ) -> CommonRes[LangGraphSkillResult]:
        logging.info("[run_langgraph_skill] request=%s", req.user_request)
        try:
            result = run_skill_graph(req.user_request)
            return CommonRes.success(LangGraphSkillResult(**result))
        except Exception as exc:
            logging.exception("[run_langgraph_skill] failed")
            return CommonRes.error(
                code=ResCodeEnum.COMMON_ERROR.code,
                message=str(exc),
            )
