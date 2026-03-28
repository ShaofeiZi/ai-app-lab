# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# Licensed under the 【火山方舟】原型应用软件自用许可协议
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at 
#     https://www.volcengine.com/docs/82379/1433703
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import uuid
from pydantic import BaseModel

from mobile_agent.agent.infra.message_web import (
    SSEThinkMessageData,
    SSEToolCallMessageData,
)
from mobile_agent.agent.llm.stream_pipe import stream_pipeline
from mobile_agent.agent.graph.state import MobileUseAgentState
from mobile_agent.agent.infra.model import ToolCall


def format_sse(data: dict | BaseModel | None = None, **kwargs) -> str:
    # 统一把字典或 Pydantic 模型编码成 SSE data 行，所有上游节点都通过这一层保持输出格式一致。
    if isinstance(data, BaseModel):
        data = data.model_dump()
    else:
        if not data:
            data = {}
        data.update(kwargs)
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


def stream_messages(update, is_stream: bool, task_id: str):
    """
    把 LangGraph 的事件流翻译成前端真正能消费的 SSE 文本。

    这里的关键思想是：
    LangGraph 关心“图执行发生了什么”，
    前端关心“现在该把哪种消息卡片画出来”。
    所以中间必须有一层协议转换。
    """
    # 某些上游已经产出完整的 SSE 文本，这里直接透传，避免重复编码。
    if isinstance(update, str) and update.startswith("data: "):
        yield update
        return

    eventType = update[0]
    if eventType == "custom":
        # custom 事件约定为“已经准备好的前端消息”，不再做结构化拆分。
        yield update[1]
        return
    elif eventType == "messages":
        if not is_stream:
            return
        if isinstance(update, tuple) and len(update) == 2:
            mode, data = update
            message_chunk, metadata = data
            if (
                message_chunk.content
                and metadata.get("langgraph_node") == "model"
                and message_chunk.type == "AIMessageChunk"
            ):
                # stream_pipeline 负责把模型的增量 token 聚合成更适合前端展示的 think 片段，
                # 例如处理 chunk 拼接、去重或节流。
                pipe_result = stream_pipeline.pipe(
                    id=message_chunk.id,
                    delta=message_chunk.content,
                )
                if not pipe_result:
                    return
                (id, delta) = pipe_result
                if not delta:
                    return
                yield format_sse(
                    SSEThinkMessageData(
                        id=id,
                        task_id=task_id,
                        role="assistant",
                        type="think",
                        content=delta,
                    )
                )
        return
    else:
        # 保留未知事件类型的原始提示，便于调试新的 LangGraph 事件分支。
        yield f"Unknown event type: {eventType}"


def get_writer_tool_input(state: MobileUseAgentState, tool_call: ToolCall):
    # 每次工具调用都生成独立 tool_id，前端可以用它把 start/stop/success 事件串成同一张卡片。
    state.update(current_tool_call_id=str(uuid.uuid4()))
    return format_sse(
        SSEToolCallMessageData(
            id=state.get("chunk_id"),
            task_id=state.get("task_id"),
            tool_id=state.get("current_tool_call_id"),
            type="tool",
            tool_type="tool_input",
            tool_name=tool_call["name"],
            tool_input=json.dumps(tool_call["arguments"], ensure_ascii=False),
            status="start",
        )
    )


def get_writer_tool_output(
    state: MobileUseAgentState, tool_call: ToolCall, output, status
):
    current_tool_call_id = state.get("current_tool_call_id")
    if current_tool_call_id:
        # 输出发出后立即清空 current_tool_call_id，避免下一次工具调用错误复用旧 ID。
        state.update(current_tool_call_id="")

        return format_sse(
            SSEToolCallMessageData(
                id=state.get("chunk_id"),
                task_id=state.get("task_id"),
                tool_id=current_tool_call_id,
                type="tool",
                tool_type="tool_output",
                tool_name=tool_call["name"],
                tool_input=json.dumps(tool_call["arguments"], ensure_ascii=False),
                tool_output=json.dumps(output["result"], ensure_ascii=False),
                status=status,
            )
        )
    # 理论上每个 tool_output 都应该先有 tool_input。
    # 如果这里拿不到 current_tool_call_id，通常说明调用顺序出了问题，返回 None 让上游保守处理。


def get_writer_think(state: MobileUseAgentState, chunk_id: str, summary: str):
    # 非流式模式下会走这里，把模型总结直接包装成 think 消息，保持前端消费协议不变。
    return format_sse(
        SSEThinkMessageData(
            id=chunk_id,
            task_id=state.get("task_id"),
            role="assistant",
            type="think",
            content=summary,
        )
    )
