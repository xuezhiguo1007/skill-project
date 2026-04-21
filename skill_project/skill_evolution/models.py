from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field

SkillCandidateStatus = Literal["candidate", "approved", "active", "rejected"]


def utc_now() -> datetime:
    return datetime.now(UTC)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class TaskTrajectory(BaseModel):
    request: str
    final_response: str
    succeeded: bool = True
    summary: str | None = None
    correction_notes: list[str] = Field(default_factory=list)
    tools_used: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class ReplayCase(BaseModel):
    request: str
    expected_keywords: list[str] = Field(default_factory=list)
    forbidden_keywords: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    notes: str | None = None


class ApprovalDecision(BaseModel):
    reviewer: str
    approved: bool
    notes: str | None = None
    created_at: datetime = Field(default_factory=utc_now)


class ReplayResult(BaseModel):
    case_id: str
    request: str
    output: str
    passed: bool
    score: float
    matched_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    violations: list[str] = Field(default_factory=list)


class ReplayReport(BaseModel):
    report_id: str = Field(default_factory=lambda: new_id("report"))
    candidate_id: str
    average_score: float
    pass_rate: float
    min_required_average: float
    min_required_pass_rate: float
    passed: bool
    created_at: datetime = Field(default_factory=utc_now)
    results: list[ReplayResult] = Field(default_factory=list)


class SkillCandidate(BaseModel):
    candidate_id: str = Field(default_factory=lambda: new_id("skill"))
    skill_name: str
    description: str
    when_to_use: str
    markdown: str
    source_count: int
    trigger_keywords: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    tool_hints: list[str] = Field(default_factory=list)
    status: SkillCandidateStatus = "candidate"
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    approvals: list[ApprovalDecision] = Field(default_factory=list)
    replay_reports: list[str] = Field(default_factory=list)
    promotion_notes: str | None = None

    def touch(self) -> None:
        self.updated_at = utc_now()
