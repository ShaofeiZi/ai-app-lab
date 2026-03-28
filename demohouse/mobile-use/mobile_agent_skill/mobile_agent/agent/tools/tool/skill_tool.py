from typing import Optional
import json

from mobile_agent.agent.tools.tool.abc import Tool
from mobile_agent.agent.skills.definitions import SkillDefinition


class SkillTool(Tool):
    def __init__(self, skill: SkillDefinition, executor=None, context=None):
        super().__init__(
            name=skill.name,
            description=skill.description,
            parameters=skill.parameters_schema,
        )
        self.skill = skill
        self.executor = executor
        self.context = context or {}

    async def handler(self, args: Optional[dict] = {}) -> str | None:
        if self.executor:
            result = await self.executor.execute(self.skill.name, args or {}, self.context)
            if hasattr(result, "model_dump"):
                return json.dumps(result.model_dump())
            elif hasattr(result, "dict"):
                return json.dumps(result.dict())
            return json.dumps(result)
        return json.dumps({"message": "Skill executed without executor"})
