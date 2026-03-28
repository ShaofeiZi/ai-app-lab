import pytest

from mobile_agent.agent.tools.tools import Tools


@pytest.mark.asyncio
async def test_tools_are_built_from_skill_registry_not_mcp():
    tools = await Tools.from_skill_registry()
    names = {tool.name for tool in tools.prompt_tools()}
    assert "mobile:tap" in names
    assert "mobile:take_screenshot" in names
    assert "mobile:swipe" in names
    assert "finished" in names
