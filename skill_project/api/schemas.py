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
    route_reason: str | None = None
    skill_context: str | None = None
    skill_result: str | None = None
    final_response: str | None = None
