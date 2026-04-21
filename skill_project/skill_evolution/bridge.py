from __future__ import annotations

import json
from pathlib import Path

from skill_project import PROJECT_ROOT
from skill_project.langgraph_skill.models import SkillSpec


def load_active_skill_specs(root_dir: Path | None = None) -> list[SkillSpec]:
    active_dir = (root_dir or (PROJECT_ROOT / "generated_skills")) / "active"
    if not active_dir.exists():
        return []

    skills: list[SkillSpec] = []
    for path in sorted(active_dir.iterdir()):
        if not path.is_dir():
            continue
        metadata_path = path / "metadata.json"
        markdown_path = path / "SKILL.md"
        if not metadata_path.exists() or not markdown_path.exists():
            continue
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        skills.append(
            SkillSpec(
                name=metadata["skill_name"],
                description=metadata["description"],
                when_to_use=metadata["when_to_use"],
                handler_type="context",
                trigger_keywords=tuple(metadata.get("trigger_keywords", [])),
                content=markdown_path.read_text(encoding="utf-8"),
                context_text=metadata["description"],
            )
        )
    return skills
