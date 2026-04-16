from pydantic import BaseModel, Field


class Settings(BaseModel):
    api_title: str = Field(default="Skill Project")
    api_version: str = Field(default="0.1.0")
    api_description: str = Field(
        default="A FastAPI wrapper for validating local skills with an LLM."
    )
    default_model: str = Field(default="gpt-4.1-mini")


SETTINGS = Settings()
