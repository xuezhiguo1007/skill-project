from __future__ import annotations

import logging

from fastapi import APIRouter

from skill_project.api.schemas import (
    CommonRes,
    ReplayReportItem,
    ResCodeEnum,
    SkillApprovalReq,
    SkillCandidateItem,
    SkillPromoteReq,
    SkillReplayReq,
)
from skill_project.skill_evolution import (
    ReplayCase,
    SkillEvolutionRepository,
    SkillEvolutionService,
)


class SkillEvolutionAPI:
    def __init__(self) -> None:
        self.router = APIRouter()
        self.repository = SkillEvolutionRepository()
        self.service = SkillEvolutionService(repository=self.repository)
        self._register_routes()

    def _register_routes(self) -> None:
        self.router.add_api_route(
            "/api/v1/skill-evolution/candidates",
            self.list_candidates,
            methods=["GET"],
            response_model=CommonRes[list[SkillCandidateItem]],
        )
        self.router.add_api_route(
            "/api/v1/skill-evolution/approved",
            self.list_approved,
            methods=["GET"],
            response_model=CommonRes[list[SkillCandidateItem]],
        )
        self.router.add_api_route(
            "/api/v1/skill-evolution/active",
            self.list_active,
            methods=["GET"],
            response_model=CommonRes[list[SkillCandidateItem]],
        )
        self.router.add_api_route(
            "/api/v1/skill-evolution/candidates/{candidate_id}/approve",
            self.approve_candidate,
            methods=["POST"],
            response_model=CommonRes[SkillCandidateItem],
        )
        self.router.add_api_route(
            "/api/v1/skill-evolution/candidates/{candidate_id}/replay",
            self.replay_candidate,
            methods=["POST"],
            response_model=CommonRes[ReplayReportItem],
        )
        self.router.add_api_route(
            "/api/v1/skill-evolution/candidates/{candidate_id}/promote",
            self.promote_candidate,
            methods=["POST"],
            response_model=CommonRes[SkillCandidateItem],
        )

    async def list_candidates(self) -> CommonRes[list[SkillCandidateItem]]:
        return CommonRes.success(
            [
                SkillCandidateItem(**item.model_dump(mode="json"))
                for item in self.repository.list_candidates()
            ]
        )

    async def list_approved(self) -> CommonRes[list[SkillCandidateItem]]:
        return CommonRes.success(
            [
                SkillCandidateItem(**item.model_dump(mode="json"))
                for item in self.repository.list_approved()
            ]
        )

    async def list_active(self) -> CommonRes[list[SkillCandidateItem]]:
        return CommonRes.success(
            [
                SkillCandidateItem(**item.model_dump(mode="json"))
                for item in self.repository.list_active()
            ]
        )

    async def approve_candidate(
        self,
        candidate_id: str,
        req: SkillApprovalReq,
    ) -> CommonRes[SkillCandidateItem]:
        logging.info(
            "[approve_candidate] candidate_id=%s reviewer=%s",
            candidate_id,
            req.reviewer,
        )
        try:
            candidate = self.service.approve_candidate(
                candidate_id,
                reviewer=req.reviewer,
                notes=req.notes,
            )
            return CommonRes.success(
                SkillCandidateItem(**candidate.model_dump(mode="json"))
            )
        except Exception as exc:
            logging.exception("[approve_candidate] failed")
            return CommonRes.error(
                code=ResCodeEnum.COMMON_ERROR.code,
                message=str(exc),
            )

    async def replay_candidate(
        self,
        candidate_id: str,
        req: SkillReplayReq,
    ) -> CommonRes[ReplayReportItem]:
        logging.info(
            "[replay_candidate] candidate_id=%s cases=%s",
            candidate_id,
            len(req.replay_cases),
        )
        try:
            replay_cases = [
                ReplayCase(**item.model_dump()) for item in req.replay_cases
            ]
            report = self.service.replay_candidate(
                candidate_id,
                replay_cases,
                min_average_score=req.min_average_score,
                min_pass_rate=req.min_pass_rate,
            )
            return CommonRes.success(ReplayReportItem(**report.model_dump(mode="json")))
        except Exception as exc:
            logging.exception("[replay_candidate] failed")
            return CommonRes.error(
                code=ResCodeEnum.COMMON_ERROR.code,
                message=str(exc),
            )

    async def promote_candidate(
        self,
        candidate_id: str,
        req: SkillPromoteReq,
    ) -> CommonRes[SkillCandidateItem]:
        logging.info("[promote_candidate] candidate_id=%s", candidate_id)
        try:
            candidate = self.service.promote_candidate(
                candidate_id,
                report_id=req.report_id,
                promotion_notes=req.promotion_notes,
            )
            return CommonRes.success(
                SkillCandidateItem(**candidate.model_dump(mode="json"))
            )
        except Exception as exc:
            logging.exception("[promote_candidate] failed")
            return CommonRes.error(
                code=ResCodeEnum.COMMON_ERROR.code,
                message=str(exc),
            )
