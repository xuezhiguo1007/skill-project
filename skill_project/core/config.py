from __future__ import annotations

import os
import tomllib

from pydantic import BaseModel, Field

from skill_project import PROJECT_ROOT

ENV_NAME = "APP_ENV"
DEFAULT_ENV = "local"
SUPPORTED_ENVS = {"dev", "test", "local", "prod"}
CONFIG_DIR = PROJECT_ROOT / "config"


class Settings(BaseModel):
    env: str = Field(default=DEFAULT_ENV)
    api_title: str = Field(default="Skill Project")
    api_version: str = Field(default="0.1.0")
    api_description: str = Field(
        default="A FastAPI wrapper for validating local skills with an LLM."
    )
    default_model: str = Field(default="glm-5-no-think-fast")
    openai_api_key: str = Field(default="sk-9Tsyhrb8-zVUom91z-6JTWgCRR-zKwI2t7E")
    openai_base_url: str | None = Field(
        default="https://fastai.enncloud.cn/v1/chat/completions"
    )


def resolve_env() -> str:
    env = os.getenv(ENV_NAME, DEFAULT_ENV).strip().lower() or DEFAULT_ENV
    if env not in SUPPORTED_ENVS:
        raise RuntimeError(
            f"Unsupported {ENV_NAME}={env!r}. Expected one of: {', '.join(sorted(SUPPORTED_ENVS))}."
        )
    return env


def load_settings() -> Settings:
    env = resolve_env()
    config_path = CONFIG_DIR / f"{env}.toml"
    if not config_path.exists():
        raise RuntimeError(f"Config file not found: {config_path}")

    with config_path.open("rb") as fp:
        payload = tomllib.load(fp)

    config_data = payload.get("app", {})
    llm_data = payload.get("llm", {})
    return Settings(
        env=env,
        **config_data,
        **llm_data,
    )


SETTINGS = load_settings()
