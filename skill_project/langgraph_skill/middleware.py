from __future__ import annotations

from collections.abc import Callable

from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse
from langchain.messages import SystemMessage

from skill_project.langgraph_skill.registry import SkillRegistry, create_demo_registry
from skill_project.langgraph_skill.tools import build_load_skill_tool


class SkillMiddleware(AgentMiddleware):
    """Expose lightweight skill descriptions and a load_skill tool."""

    def __init__(self, registry: SkillRegistry | None = None):
        self.registry = registry or create_demo_registry()
        self.tools = [build_load_skill_tool(self.registry)]
        self.skills_prompt = "\n".join(
            [
                f"- **{skill.name}**: {skill.description}"
                for skill in self.registry.list()
            ]
        )

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        skills_addendum = (
            "\n\n## Available Skills\n\n"
            f"{self.skills_prompt}\n\n"
            "When a request needs detailed domain instructions, call the "
            "`load_skill` tool to load the full skill content on demand."
        )
        new_content = list(request.system_message.content_blocks) + [
            {"type": "text", "text": skills_addendum}
        ]
        modified_request = request.override(
            system_message=SystemMessage(content=new_content)
        )
        return handler(modified_request)
