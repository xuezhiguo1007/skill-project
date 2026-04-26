from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from skill_project.llm import create_chat_model


def utc_now() -> datetime:
    return datetime.now(UTC)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def slugify_skill_name(name: str) -> str:
    normalized = re.sub(r"[^a-z0-9_\u4e00-\u9fff]+", "_", name.lower()).strip("_")
    return normalized or "evolved_skill"


@dataclass(slots=True)
class EvolvedSkill:
    skill_id: str
    name: str
    description: str
    when_to_use: str
    trigger_keywords: list[str]
    tags: list[str]
    example_queries: list[str]
    usage_count: int
    version: int
    content: str
    created_at: str
    updated_at: str
    last_query: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "name": self.name,
            "description": self.description,
            "when_to_use": self.when_to_use,
            "trigger_keywords": self.trigger_keywords,
            "tags": self.tags,
            "example_queries": self.example_queries,
            "usage_count": self.usage_count,
            "version": self.version,
            "content": self.content,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_query": self.last_query,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "EvolvedSkill":
        return cls(
            skill_id=payload["skill_id"],
            name=payload["name"],
            description=payload["description"],
            when_to_use=payload["when_to_use"],
            trigger_keywords=list(payload.get("trigger_keywords", [])),
            tags=list(payload.get("tags", [])),
            example_queries=list(payload.get("example_queries", [])),
            usage_count=int(payload.get("usage_count", 0)),
            version=int(payload.get("version", 1)),
            content=payload["content"],
            created_at=payload["created_at"],
            updated_at=payload["updated_at"],
            last_query=payload.get("last_query", ""),
        )


class KeywordExtractionResult(BaseModel):
    skill_name: str = Field(..., description="Suggested stable skill name.")
    keywords: list[str] = Field(
        default_factory=list, description="Core trigger keywords."
    )
    tags: list[str] = Field(
        default_factory=list, description="Short tags for indexing."
    )
    description: str = Field(..., description="Short summary of the skill.")
    when_to_use: str = Field(..., description="When to use this skill.")


class MatchDecision(BaseModel):
    matched_skill_id: str | None = Field(default=None)
    matched_score: float = Field(default=0.0, ge=0.0, le=1.0)
    should_create: bool = Field(
        ..., description="Whether a new skill should be created."
    )
    should_update: bool = Field(
        ..., description="Whether the matched skill should be updated."
    )
    reason: str = Field(..., description="Why this decision was made.")


class SkillRewriteResult(BaseModel):
    name: str = Field(..., description="Stable skill name.")
    description: str = Field(..., description="Updated skill description.")
    when_to_use: str = Field(..., description="Updated usage guidance.")
    trigger_keywords: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    content: str = Field(..., description="Final SKILL markdown.")


class EvolutionSkillService:
    def __init__(self, project_root: Path, model_name: str | None = None):
        self.project_root = project_root
        self.root_dir = project_root / "generated_skills" / "evolution"
        self.skills_dir = self.root_dir / "skills"
        self.model_name = model_name
        self._ensure_layout()

    def list_skills(self) -> list[EvolvedSkill]:
        items = [
            EvolvedSkill.from_dict(json.loads(path.read_text(encoding="utf-8")))
            for path in sorted(self.skills_dir.glob("*.json"))
        ]
        items.sort(key=lambda item: item.updated_at, reverse=True)
        return items

    def evolve(self, query: str) -> dict[str, Any]:
        normalized_query = " ".join(query.split())
        if not normalized_query:
            raise ValueError("Query must not be empty.")

        extraction = self._extract_skill_signals(normalized_query)
        skills = self.list_skills()
        decision = self._decide_match_or_create(normalized_query, extraction, skills)

        if decision.should_create or decision.matched_skill_id is None:
            skill = self._create_skill(normalized_query, extraction)
            self._save_skill(skill)
            return {
                "action": "created",
                "reason": decision.reason,
                "matched": False,
                "matched_score": round(decision.matched_score, 4),
                "skill": skill,
            }

        skill = next(
            item for item in skills if item.skill_id == decision.matched_skill_id
        )
        skill.usage_count += 1
        skill.last_query = normalized_query
        skill.updated_at = utc_now().isoformat()

        if decision.should_update:
            rewritten = self._rewrite_skill(
                query=normalized_query,
                extraction=extraction,
                skill=skill,
            )
            skill.name = slugify_skill_name(rewritten.name)
            skill.description = rewritten.description
            skill.when_to_use = rewritten.when_to_use
            skill.trigger_keywords = rewritten.trigger_keywords[:12]
            skill.tags = rewritten.tags[:6]
            skill.content = rewritten.content
            skill.example_queries = self._merge_unique(
                skill.example_queries,
                [normalized_query],
                limit=6,
            )
            skill.version += 1
            self._save_skill(skill)
            return {
                "action": "updated",
                "reason": decision.reason,
                "matched": True,
                "matched_score": round(decision.matched_score, 4),
                "skill": skill,
            }

        skill.example_queries = self._merge_unique(
            skill.example_queries,
            [normalized_query],
            limit=6,
        )
        self._save_skill(skill)
        return {
            "action": "reused",
            "reason": decision.reason,
            "matched": True,
            "matched_score": round(decision.matched_score, 4),
            "skill": skill,
        }

    def load_skill_specs(self):
        from skill_project.langgraph_skill.models import SkillSpec

        return [
            SkillSpec(
                name=skill.name,
                description=skill.description,
                when_to_use=skill.when_to_use,
                handler_type="context",
                trigger_keywords=tuple(skill.trigger_keywords),
                content=skill.content,
                context_text=skill.description,
            )
            for skill in self.list_skills()
        ]

    def _create_skill(
        self,
        query: str,
        extraction: KeywordExtractionResult,
    ) -> EvolvedSkill:
        now = utc_now().isoformat()
        rewritten = self._rewrite_skill(query=query, extraction=extraction, skill=None)
        return EvolvedSkill(
            skill_id=new_id("evo_skill"),
            name=slugify_skill_name(rewritten.name),
            description=rewritten.description,
            when_to_use=rewritten.when_to_use,
            trigger_keywords=rewritten.trigger_keywords[:12],
            tags=rewritten.tags[:6],
            example_queries=[query],
            usage_count=1,
            version=1,
            content=rewritten.content,
            created_at=now,
            updated_at=now,
            last_query=query,
        )

    def _extract_skill_signals(self, query: str) -> KeywordExtractionResult:
        return self._invoke_structured(
            KeywordExtractionResult,
            [
                (
                    "system",
                    "你需要从单条用户查询中提取技能信号。"
                    "请返回简洁、可复用、稳定的技能抽象字段。"
                    "不要把整条查询原样复制为技能名。"
                    "优先提取噪音更低的领域术语和可复用的能力范围。",
                ),
                (
                    "user",
                    f"请分析这条查询，并提取可复用的技能信号。\n\n查询内容：\n{query}",
                ),
            ],
        )

    def _decide_match_or_create(
        self,
        query: str,
        extraction: KeywordExtractionResult,
        skills: list[EvolvedSkill],
    ) -> MatchDecision:
        if not skills:
            return MatchDecision(
                matched_skill_id=None,
                matched_score=0.0,
                should_create=True,
                should_update=False,
                reason="当前还没有已进化技能，因此应创建一个新技能。",
            )

        candidates = json.dumps(
            [
                {
                    "skill_id": skill.skill_id,
                    "name": skill.name,
                    "description": skill.description,
                    "when_to_use": skill.when_to_use,
                    "trigger_keywords": skill.trigger_keywords,
                    "example_queries": skill.example_queries,
                    "usage_count": skill.usage_count,
                    "version": skill.version,
                    "last_query": skill.last_query,
                }
                for skill in skills
            ],
            ensure_ascii=False,
            indent=2,
        )
        return self._invoke_structured(
            MatchDecision,
            [
                (
                    "system",
                    "你需要判断一条新的用户查询应该创建新技能、复用已有技能，还是更新已有技能。"
                    "只有当现有技能无法较好覆盖该请求时，才创建新技能。"
                    "当匹配到的技能需要吸收新的能力范围、示例或触发词时，将 should_update 设为 true。"
                    "matched_score 必须保持在 0 到 1 之间。",
                ),
                (
                    "user",
                    "当前查询：\n"
                    f"{query}\n\n"
                    "提取出的查询信号：\n"
                    f"{extraction.model_dump_json(indent=2)}\n\n"
                    "现有技能：\n"
                    f"{candidates}\n\n"
                    "请返回最佳决策。",
                ),
            ],
        )

    def _rewrite_skill(
        self,
        *,
        query: str,
        extraction: KeywordExtractionResult,
        skill: EvolvedSkill | None,
    ) -> SkillRewriteResult:
        existing_skill_json = (
            json.dumps(skill.to_dict(), ensure_ascii=False, indent=2)
            if skill is not None
            else "null"
        )
        result = self._invoke_structured(
            SkillRewriteResult,
            [
                (
                    "system",
                    "你需要为一个智能体系统维护可复用的 SKILL.md 内容。"
                    "请使用 Markdown 编写简洁、可复用、面向执行的技能说明。"
                    "技能内容必须包含以下章节：Description、When to Use、Trigger Keywords、Procedure、Example Queries。"
                    "如果提供了现有技能，请在保留其稳定意图的前提下融合新的查询。"
                    "触发关键词应保持可复用，避免过于具体、只出现一次的短语。",
                ),
                (
                    "user",
                    "当前查询：\n"
                    f"{query}\n\n"
                    "提取出的查询信号：\n"
                    f"{extraction.model_dump_json(indent=2)}\n\n"
                    "现有技能（null 表示需要新建技能）：\n"
                    f"{existing_skill_json}\n\n"
                    "请重写或创建最终的可复用技能。",
                ),
            ],
        )
        result.name = slugify_skill_name(result.name)
        if not result.trigger_keywords:
            result.trigger_keywords = extraction.keywords[:8]
        if not result.tags:
            result.tags = extraction.tags[:4] or result.trigger_keywords[:4]
        return result

    def _invoke_structured(
        self,
        schema: type[BaseModel],
        messages: list[tuple[str, str]],
    ) -> BaseModel:
        model = create_chat_model(self.model_name)
        try:
            return model.with_structured_output(schema).invoke(messages)
        except Exception:
            fallback_messages = [
                *messages,
                (
                    "user",
                    "请严格只返回一个 JSON 对象，不要输出任何解释、标题、前后缀、代码块标记。"
                    "返回结果必须能被 JSON.parse 直接解析，并且字段必须完整。"
                    "JSON Schema 如下：\n"
                    f"{json.dumps(schema.model_json_schema(), ensure_ascii=False, indent=2)}",
                ),
            ]
            response = model.invoke(fallback_messages)
            content = self._extract_json_object(getattr(response, "content", response))
            return schema.model_validate_json(content)

    def _extract_json_object(self, raw_content: Any) -> str:
        if isinstance(raw_content, str):
            text = raw_content.strip()
        elif isinstance(raw_content, list):
            parts: list[str] = []
            for item in raw_content:
                if isinstance(item, str):
                    parts.append(item)
                    continue
                if isinstance(item, dict) and isinstance(item.get("text"), str):
                    parts.append(item["text"])
            text = "\n".join(parts).strip()
        else:
            text = str(raw_content).strip()

        if not text:
            raise ValueError("Model returned empty content for structured response.")

        fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, flags=re.DOTALL)
        if fenced:
            return fenced.group(1)

        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and start < end:
            return text[start : end + 1]

        raise ValueError(f"Model did not return valid JSON content: {text}")

    def _save_skill(self, skill: EvolvedSkill) -> None:
        payload = json.dumps(skill.to_dict(), ensure_ascii=False, indent=2)
        (self.skills_dir / f"{skill.skill_id}.json").write_text(
            payload, encoding="utf-8"
        )

    def _ensure_layout(self) -> None:
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self.skills_dir.mkdir(parents=True, exist_ok=True)

    def _merge_unique(
        self, base: list[str], extra: list[str], *, limit: int
    ) -> list[str]:
        merged = list(dict.fromkeys([*base, *extra]))
        return merged[:limit]
