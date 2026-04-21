from __future__ import annotations

import json
from pathlib import Path

from skill_project import PROJECT_ROOT
from skill_project.skill_evolution.models import (
    ApprovalDecision,
    ReplayReport,
    SkillCandidate,
)


class SkillEvolutionRepository:
    def __init__(self, root_dir: Path | None = None):
        self.root_dir = root_dir or (PROJECT_ROOT / "generated_skills")
        self.candidates_dir = self.root_dir / "candidates"
        self.approved_dir = self.root_dir / "approved"
        self.active_dir = self.root_dir / "active"
        self.rejected_dir = self.root_dir / "rejected"
        self.reports_dir = self.root_dir / "reports"
        self._ensure_layout()

    def save_candidate(self, candidate: SkillCandidate) -> SkillCandidate:
        candidate.touch()
        self._write_json(
            self.candidates_dir / f"{candidate.candidate_id}.json", candidate
        )
        return candidate

    def get_candidate(self, candidate_id: str) -> SkillCandidate:
        return SkillCandidate.model_validate_json(
            (self.candidates_dir / f"{candidate_id}.json").read_text(encoding="utf-8")
        )

    def list_candidates(self) -> list[SkillCandidate]:
        items = [
            SkillCandidate.model_validate_json(path.read_text(encoding="utf-8"))
            for path in sorted(self.candidates_dir.glob("*.json"))
        ]
        items.sort(key=lambda item: item.updated_at, reverse=True)
        return items

    def list_approved(self) -> list[SkillCandidate]:
        return self._load_candidate_dir(self.approved_dir)

    def list_rejected(self) -> list[SkillCandidate]:
        return self._load_candidate_dir(self.rejected_dir)

    def list_active(self) -> list[SkillCandidate]:
        items: list[SkillCandidate] = []
        for path in sorted(self.active_dir.iterdir()):
            if not path.is_dir():
                continue
            metadata_path = path / "metadata.json"
            if not metadata_path.exists():
                continue
            items.append(
                SkillCandidate.model_validate_json(
                    metadata_path.read_text(encoding="utf-8")
                )
            )
        items.sort(key=lambda item: item.updated_at, reverse=True)
        return items

    def record_approval(
        self,
        candidate_id: str,
        decision: ApprovalDecision,
    ) -> SkillCandidate:
        candidate = self.get_candidate(candidate_id)
        candidate.approvals.append(decision)
        candidate.status = "approved" if decision.approved else "rejected"
        self.save_candidate(candidate)
        target_dir = self.approved_dir if decision.approved else self.rejected_dir
        self._write_json(target_dir / f"{candidate.candidate_id}.json", candidate)
        return candidate

    def save_report(self, report: ReplayReport) -> ReplayReport:
        self._write_json(self.reports_dir / f"{report.report_id}.json", report)
        candidate = self.get_candidate(report.candidate_id)
        if report.report_id not in candidate.replay_reports:
            candidate.replay_reports.append(report.report_id)
        self.save_candidate(candidate)
        return report

    def get_report(self, report_id: str) -> ReplayReport:
        return ReplayReport.model_validate_json(
            (self.reports_dir / f"{report_id}.json").read_text(encoding="utf-8")
        )

    def promote_candidate(
        self,
        candidate_id: str,
        *,
        promotion_notes: str | None = None,
    ) -> SkillCandidate:
        candidate = self.get_candidate(candidate_id)
        if candidate.status != "approved":
            raise ValueError("Only approved candidates can be promoted.")
        candidate.status = "active"
        candidate.promotion_notes = promotion_notes
        self.save_candidate(candidate)
        active_dir = self.active_dir / candidate.skill_name
        active_dir.mkdir(parents=True, exist_ok=True)
        (active_dir / "SKILL.md").write_text(candidate.markdown, encoding="utf-8")
        self._write_json(active_dir / "metadata.json", candidate)
        return candidate

    def _ensure_layout(self) -> None:
        for directory in (
            self.root_dir,
            self.candidates_dir,
            self.approved_dir,
            self.active_dir,
            self.rejected_dir,
            self.reports_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)

    def _load_candidate_dir(self, directory: Path) -> list[SkillCandidate]:
        items = [
            SkillCandidate.model_validate_json(path.read_text(encoding="utf-8"))
            for path in sorted(directory.glob("*.json"))
        ]
        items.sort(key=lambda item: item.updated_at, reverse=True)
        return items

    def _write_json(self, path: Path, payload) -> None:
        path.write_text(
            json.dumps(payload.model_dump(mode="json"), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
