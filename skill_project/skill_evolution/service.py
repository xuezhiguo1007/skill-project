from __future__ import annotations

from skill_project.skill_evolution.evaluator import ReplayEvaluator
from skill_project.skill_evolution.generator import SkillGenerator
from skill_project.skill_evolution.models import (
    ApprovalDecision,
    ReplayCase,
    ReplayReport,
)
from skill_project.skill_evolution.storage import SkillEvolutionRepository


class SkillEvolutionService:
    def __init__(
        self,
        repository: SkillEvolutionRepository | None = None,
        generator: SkillGenerator | None = None,
        evaluator: ReplayEvaluator | None = None,
    ):
        self.repository = repository or SkillEvolutionRepository()
        self.generator = generator or SkillGenerator()
        self.evaluator = evaluator or ReplayEvaluator()

    def create_candidate(self, trajectories, **kwargs):
        candidate = self.generator.generate(trajectories, **kwargs)
        return self.repository.save_candidate(candidate)

    def approve_candidate(
        self,
        candidate_id: str,
        *,
        reviewer: str,
        notes: str | None = None,
    ):
        return self.repository.record_approval(
            candidate_id,
            ApprovalDecision(reviewer=reviewer, approved=True, notes=notes),
        )

    def reject_candidate(
        self,
        candidate_id: str,
        *,
        reviewer: str,
        notes: str | None = None,
    ):
        return self.repository.record_approval(
            candidate_id,
            ApprovalDecision(reviewer=reviewer, approved=False, notes=notes),
        )

    def replay_candidate(
        self,
        candidate_id: str,
        cases: list[ReplayCase],
        *,
        min_average_score: float = 0.7,
        min_pass_rate: float = 0.8,
    ) -> ReplayReport:
        candidate = self.repository.get_candidate(candidate_id)
        report = self.evaluator.evaluate(
            candidate,
            cases,
            min_average_score=min_average_score,
            min_pass_rate=min_pass_rate,
        )
        return self.repository.save_report(report)

    def promote_candidate(
        self,
        candidate_id: str,
        *,
        report_id: str | None = None,
        promotion_notes: str | None = None,
    ):
        if report_id is not None:
            report = self.repository.get_report(report_id)
            if report.candidate_id != candidate_id:
                raise ValueError("Replay report does not belong to this candidate.")
            if not report.passed:
                raise ValueError(
                    "Cannot promote a candidate with a failed replay report."
                )
        candidate = self.repository.get_candidate(candidate_id)
        if candidate.status != "approved":
            raise ValueError("Candidate must be approved before promotion.")
        return self.repository.promote_candidate(
            candidate_id,
            promotion_notes=promotion_notes,
        )

    def run_full_cycle(
        self,
        *,
        trajectories,
        replay_cases: list[ReplayCase],
        reviewer: str,
        candidate_name: str | None = None,
        reviewer_notes: str | None = None,
        promotion_notes: str | None = None,
    ):
        candidate = self.create_candidate(trajectories, skill_name=candidate_name)
        approved = self.approve_candidate(
            candidate.candidate_id,
            reviewer=reviewer,
            notes=reviewer_notes,
        )
        report = self.replay_candidate(approved.candidate_id, replay_cases)
        if not report.passed:
            return {
                "candidate": approved,
                "report": report,
                "promoted": None,
            }
        promoted = self.promote_candidate(
            approved.candidate_id,
            report_id=report.report_id,
            promotion_notes=promotion_notes,
        )
        return {
            "candidate": approved,
            "report": report,
            "promoted": promoted,
        }
