from __future__ import annotations

import logging

from fastapi import APIRouter

from skill_project.api.schemas import (
    CommonRes,
    LangGraphSkillReq,
    LangGraphSkillResult,
    ResCodeEnum,
)
from skill_project.langgraph_skill.service import (
    run_skill_graph,
    run_sql_skill_agent,
)


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
            summary="运行 LangGraph skill demo",
            description="当前仓库内置的旅游领域 LangGraph skill 示例接口。",
        )
        self.router.add_api_route(
            "/api/v1/langgraph-sql-skill",
            self.run_langgraph_sql_skill,
            methods=["POST"],
            response_model=CommonRes[LangGraphSkillResult],
            summary="运行 SQL assistant on-demand skills 示例",
            description=(
                "参考官方教程“Build a SQL assistant with on-demand skills”的接口示例。"
                "该接口不会预先注入完整 SQL 专家上下文，而是先暴露轻量 skill 列表，"
                "再根据请求通过大模型按需加载 sales analytics 或 inventory management skill。"
            ),
        )

    async def run_langgraph_skill(
        self,
        req: LangGraphSkillReq,
    ) -> CommonRes[LangGraphSkillResult]:
        """运行旅游场景的 LangGraph skill 示例。"""
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

    async def run_langgraph_sql_skill(
        self,
        req: LangGraphSkillReq,
    ) -> CommonRes[LangGraphSkillResult]:
        """运行会真实调用大模型的 SQL assistant on-demand skills 示例。"""
        logging.info(
            "[run_langgraph_sql_skill] request=%s model=%s",
            req.user_request,
            req.model,
        )
        try:
            result = run_sql_skill_agent(
                user_request=req.user_request,
                model_name=req.model,
            )
            return CommonRes.success(LangGraphSkillResult(**result))
        except Exception as exc:
            logging.exception("[run_langgraph_sql_skill] failed")
            return CommonRes.error(
                code=ResCodeEnum.COMMON_ERROR.code,
                message=str(exc),
            )
