from mobile_agent.agent.graph.nodes import normalize_tool_execution_result


def test_normalize_tool_execution_result_marks_successful_json_as_success():
    success, output = normalize_tool_execution_result(
        {"name": "mobile:tap", "arguments": {"x": 1, "y": 2}},
        '{"action_name":"tap","success":true,"payload":{"x":1,"y":2}}',
    )

    assert success is True
    assert "操作下发成功" in output["result"]


def test_normalize_tool_execution_result_marks_failed_json_as_stop():
    success, output = normalize_tool_execution_result(
        {"name": "mobile:tap", "arguments": {"x": 1, "y": 2}},
        '{"action_name":"tap","success":false,"payload":{"error":"device command failed"}}',
    )

    assert success is False
    assert "操作下发失败" in output["result"]
    assert "device command failed" in output["result"]
