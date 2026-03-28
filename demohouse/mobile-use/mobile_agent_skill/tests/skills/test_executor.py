import pytest

from mobile_agent.agent.skills.executor import SkillExecutor


class FakeService:
    async def call_tool(self, tool_name, session, args=None):
        return {
            "success": True,
            "tool_name": tool_name,
            "args": args,
            "session": session,
        }


@pytest.mark.asyncio
async def test_executor_dispatches_to_handler():
    executor = SkillExecutor(service=FakeService())
    result = await executor.execute(
        "mobile:tap",
        {"x": 3, "y": 4},
        context={"session": {"pod_id": "pod-1"}},
    )
    assert result["success"] is True
    assert result["tool_name"] == "tap"
    assert result["args"]["x"] == 3
