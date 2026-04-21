from __future__ import annotations

from enum import Enum
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

from skill_project.services.skill_service import SCENARIOS

T = TypeVar("T")


class ResCodeEnum(Enum):
    SUCCESS = (0, "Success")
    COMMON_ERROR = (1, "Server error")

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message


class CommonRes(BaseModel, Generic[T]):
    code: int = Field(default=ResCodeEnum.SUCCESS.code)
    message: str = Field(default=ResCodeEnum.SUCCESS.message)
    data: T | None = Field(default=None)

    @classmethod
    def success(cls, data: T | None = None) -> "CommonRes[T]":
        return cls(
            code=ResCodeEnum.SUCCESS.code,
            message=ResCodeEnum.SUCCESS.message,
            data=data,
        )

    @classmethod
    def error(
        cls,
        code: int = ResCodeEnum.COMMON_ERROR.code,
        message: str = ResCodeEnum.COMMON_ERROR.message,
    ) -> "CommonRes[None]":
        return cls(code=code, message=message, data=None)


class SkillItem(BaseModel):
    name: str
    description: str
    path: str


class ValidateSkillReq(BaseModel):
    prompt: str = Field(..., description="The user prompt passed to the LLM.")
    model: str | None = Field(default=None, description="Override the default model.")
    scenario: str | None = Field(
        default=None,
        description=f"Optional scenario label for bookkeeping: {', '.join(sorted(SCENARIOS))}",
    )


class ScenarioRunReq(BaseModel):
    scenario: str = Field(..., description=f"One of: {', '.join(sorted(SCENARIOS))}")
    model: str | None = Field(default=None, description="Override the default model.")


class LangGraphSkillReq(BaseModel):
    user_request: str = Field(
        ..., description="The user request routed through the LangGraph skill flow."
    )
    model: str | None = Field(default=None, description="Override the default model.")


class ValidationResult(BaseModel):
    scenario: str | None = None
    title: str | None = None
    model: str
    prompt: str
    response: str


class LangGraphSkillResult(BaseModel):
    user_request: str
    available_skills: list[str]
    selected_skill: str | None = None
    loaded_skills: list[str] = Field(default_factory=list)
    route_reason: str | None = None
    skill_context: str | None = None
    skill_result: str | None = None
    final_response: str | None = None


class ReplayCaseItem(BaseModel):
    request: str
    expected_keywords: list[str] = Field(default_factory=list)
    forbidden_keywords: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    notes: str | None = None


class SkillCandidateItem(BaseModel):
    candidate_id: str
    skill_name: str
    description: str
    when_to_use: str
    markdown: str
    source_count: int
    trigger_keywords: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    tool_hints: list[str] = Field(default_factory=list)
    status: str
    created_at: str
    updated_at: str
    replay_reports: list[str] = Field(default_factory=list)
    promotion_notes: str | None = None


class ReplayResultItem(BaseModel):
    case_id: str
    request: str
    output: str
    passed: bool
    score: float
    matched_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    violations: list[str] = Field(default_factory=list)


class ReplayReportItem(BaseModel):
    report_id: str
    candidate_id: str
    average_score: float
    pass_rate: float
    min_required_average: float
    min_required_pass_rate: float
    passed: bool
    created_at: str
    results: list[ReplayResultItem] = Field(default_factory=list)


class SkillApprovalReq(BaseModel):
    reviewer: str = Field(..., description="Reviewer identity for audit trail.")
    notes: str | None = Field(default=None, description="Optional approval notes.")


class SkillReplayReq(BaseModel):
    replay_cases: list[ReplayCaseItem] = Field(
        ..., description="Replay cases used to validate the candidate skill."
    )
    min_average_score: float = Field(default=0.7, ge=0.0, le=1.0)
    min_pass_rate: float = Field(default=0.8, ge=0.0, le=1.0)


class SkillPromoteReq(BaseModel):
    report_id: str | None = Field(
        default=None,
        description="Optional replay report id that must have passed before promotion.",
    )
    promotion_notes: str | None = Field(
        default=None, description="Optional notes attached to the active skill."
    )
