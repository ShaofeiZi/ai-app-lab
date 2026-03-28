from mobile_agent.agent.mobile.doubao_action_parser import DoubaoActionSpaceParser


def test_click_maps_to_skill_tap_name():
    parser = DoubaoActionSpaceParser(phone_width=720, phone_height=1520)
    result = parser.to_mcp_tool_call('click(start_box="<bbox>10 10 20 20</bbox>")')
    assert result["name"] == "mobile:tap"


def test_invalid_click_returns_error_action():
    parser = DoubaoActionSpaceParser(phone_width=720, phone_height=1520)
    result = parser.to_mcp_tool_call('click(start_box="<bbox>bad data</bbox>")')
    assert result["name"] == "error_action"
    assert "click(" in result["arguments"]["content"]


def test_invalid_type_returns_error_action():
    parser = DoubaoActionSpaceParser(phone_width=720, phone_height=1520)
    result = parser.to_mcp_tool_call("type()")
    assert result["name"] == "error_action"
    assert "type(" in result["arguments"]["content"]
