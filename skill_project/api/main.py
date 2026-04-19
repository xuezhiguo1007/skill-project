from fastapi import FastAPI

from skill_project.api.deep_agent_api import DeepAgentAPI
from skill_project.api.langgraph_api import LangGraphAPI
from skill_project.api.lifespan import lifespan_manager
from skill_project.api.schemas import CommonRes
from skill_project.core.config import SETTINGS

app = FastAPI(
    title=SETTINGS.api_title,
    description=SETTINGS.api_description,
    version=SETTINGS.api_version,
    lifespan=lifespan_manager,
)


@app.get("/health")
async def health() -> CommonRes[dict[str, str]]:
    return CommonRes.success({"status": "ok"})


deep_agent_api = DeepAgentAPI()
langgraph_api = LangGraphAPI()

app.include_router(deep_agent_api.router)
app.include_router(langgraph_api.router)
