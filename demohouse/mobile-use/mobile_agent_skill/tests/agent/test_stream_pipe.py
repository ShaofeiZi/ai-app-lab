from mobile_agent.agent.llm.stream_pipe import StreamPipe


def test_pipe_auto_creates_missing_id_and_returns_summary_delta():
    pipe = StreamPipe()

    result = pipe.pipe("run--missing", "Summary: 先打开Via")

    assert result == ("run--missing", "先打开Via")
    assert pipe.pipes["run--missing"].content == "Summary: 先打开Via"


def test_create_is_idempotent_after_pipe():
    pipe = StreamPipe()

    pipe.pipe("run--same", "Summary: 搜索北京烤鸭")
    cached_content = pipe.pipes["run--same"].content

    pipe.create("run--same")

    assert pipe.pipes["run--same"].content == cached_content


def test_complete_works_when_pipe_arrives_before_create():
    pipe = StreamPipe()

    pipe.pipe("run--late-create", "Summary: 打开Via\nAction: open_app(name=\"Via\")")
    pipe.create("run--late-create")

    content, summary, tool_call = pipe.complete("run--late-create")

    assert content == 'Summary: 打开Via\nAction: open_app(name="Via")'
    assert summary == "打开Via"
    assert tool_call == 'open_app(name="Via")'
