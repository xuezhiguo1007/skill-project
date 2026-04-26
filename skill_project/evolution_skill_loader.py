from __future__ import annotations

import importlib.util
import sys
from functools import lru_cache

from skill_project import PROJECT_ROOT


@lru_cache(maxsize=1)
def load_evolution_skill_module():
    module_path = PROJECT_ROOT / "skill_project" / "evolution-skill" / "service.py"
    spec = importlib.util.spec_from_file_location(
        "skill_project.evolution_skill_runtime", module_path
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load evolution skill module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def build_evolution_skill_service():
    module = load_evolution_skill_module()
    return module.EvolutionSkillService(project_root=PROJECT_ROOT)
