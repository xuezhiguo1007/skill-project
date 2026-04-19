from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

SkillHandlerType = Literal["context", "subgraph"]


@dataclass(slots=True)
class SkillSpec:
    name: str
    description: str
    when_to_use: str
    handler_type: SkillHandlerType
    trigger_keywords: tuple[str, ...] = field(default_factory=tuple)
    content: str = ""
    context_text: str = ""
    entrypoint: str | None = None

    def score(self, text: str) -> int:
        lowered = text.lower()
        return sum(1 for keyword in self.trigger_keywords if keyword.lower() in lowered)
