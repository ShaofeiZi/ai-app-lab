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

import asyncio
import json
import logging
from mobile_agent.exception.sse import SSEException
from mobile_agent.agent.memory.context_manager import ContextManager
from mobile_agent.agent.graph.sse_output import (
    format_sse,
    get_writer_think,
    get_writer_tool_input,
    get_writer_tool_output,
)
from mobile_agent.agent.infra.message_web import (
    SSEThinkMessageData,
)
from mobile_agent.agent.graph.state import MobileUseAgentState
import uuid
from langgraph.config import get_stream_writer
from mobile_agent.agent.llm.doubao import DoubaoLLM
from mobile_agent.agent.graph.context import agent_object_manager

logger = logging.getLogger(__name__)


def normalize_tool_execution_result(
    tool_call: dict,
    result: str,
) -> tuple[bool, dict[str, str]]:
    """
    根据工具返回内容推断这次执行应该被视为成功还是失败。

    SkillTool 会把 service 的返回序列化成 JSON 字符串。
    如果里面显式带了 `success=false`，这里就必须停止把它包装成“操作下发成功”。
    """
    parsed: dict[str, object] | None = None
    try:
        parsed = json.loads(result)
    except Exception:
        parsed = None

    success = True
    if isinstance(parsed, dict) and "success" in parsed:
        success = bool(parsed.get("success"))

    suffix = "操作下发成功" if success else "操作下发失败"
    return success, {
        "result": f"{tool_call['name']}:({tool_call['arguments']})\n{result}\n{suffix}"
    }


async def prepare_node(state: MobileUseAgentState):
    # 为当前线程初始化上下文管理器，并注册到全局对象管理器中。
    # 后续 model/tool 节点都会通过 thread_id 取回这一份上下文，避免在状态里反复搬运复杂对象。
    context_manager = ContextManager(messages=list(state.get("messages", [])))
    thread_id = state.get("thread_id")
    agent_object_manager.add_context_object(
        thread_id, "context_manager", context_manager
    )

    context_manager.add_system_message(DoubaoLLM.prompt)

    # 这里主动先写出一条“思考中”事件，原因是当前模型接入层无法稳定流出 think 内容。
    # 这样前端至少能在真正结果返回前展示一个占位状态，避免用户误以为请求卡死。
    sse_writer = get_stream_writer()
    sse_writer(
        format_sse(
            SSEThinkMessageData(
                id=str(uuid.uuid4()),
                task_id=state.get("task_id"),
                role="assistant",
                type="think",
                content="深度思考中...",
            )
        )
    )
    # 把补充过 system prompt 的消息重新写回状态，保证后续节点读取到的是最新上下文。
    state.update(messages=context_manager.get_messages())
    return state


async def model_node(state: MobileUseAgentState) -> MobileUseAgentState:
    """大模型节点，根据当前状态计算行动和工具调用"""

    mobile = agent_object_manager.get_mobile_client(state.get("thread_id"))
    context_manager = agent_object_manager.get_context_manager(state.get("thread_id"))
    iteration_count = state.get("iteration_count")

    # 每一轮推理前都先刷新截图，让模型基于最新屏幕状态做决策。
    screenshot_state = await mobile.take_screenshot()
    state.update(screenshot=screenshot_state.get("screenshot"))
    state.update(screenshot_dimensions=screenshot_state.get("screenshot_dimensions"))

    # 首轮与后续轮次的消息组织方式不同：
    # 首轮只需要拼用户目标和初始截图，后续轮次还要带上工具执行结果与迭代次数。
    if iteration_count == 0:
        context_manager.add_user_initial_message(
            message=state.get("user_prompt"), screenshot_url=state.get("screenshot")
        )
    else:
        context_manager.add_user_iteration_message(
            message=state.get("user_prompt"),
            iteration_count=iteration_count,
            tool_output=state.get("tool_output"),
            screenshot_url=state.get("screenshot"),
            screenshot_dimensions=state.get("screenshot_dimensions"),
        )

    # 控制上下文中的图片数量，避免多轮执行后消息体膨胀过快，影响成本与模型输入长度。
    context_manager.keep_last_n_images_in_messages(5)
    state.update(messages=context_manager.get_messages())

    # 模型实例与 thread_id 绑定，便于在一轮任务内复用线程级别的上下文和流式输出通道。
    llm = DoubaoLLM(thread_id=state.get("thread_id"), is_stream=state.get("is_stream"))

    # 在真正调用模型前更新步数统计，确保成本计算与执行轮次保持一致。
    cost_calculator = agent_object_manager.get_cost_calculator(state.get("thread_id"))
    cost_calculator.update_step(iteration_count)

    # 模型返回四部分结果：
    # chunk_id 用于串联前端消息，
    # content 是完整回答，
    # summary 是非流式时展示给前端的摘要，
    # tool_call 是后续工具节点要解析的动作描述。
    chunk_id, content, summary, tool_call = await llm.async_chat(
        context_manager.get_messages()
    )

    logger.info(f"content========: {content}")

    if not state.get("is_stream"):
        # 非流式模式下没有增量 think 输出，因此这里补发一条 summary 给前端。
        sse_writer = get_stream_writer()
        sse_writer(get_writer_think(state, chunk_id, summary))

    # 把模型产物固化回状态，供后续解析工具、继续迭代和最终回放使用。
    context_manager.add_ai_message(content)

    state.update(
        tool_call_str=tool_call,
        iteration_count=iteration_count + 1,
        chunk_id=chunk_id,
        messages=context_manager.get_messages(),
    )

    return state


async def tool_valid_node(state: MobileUseAgentState) -> MobileUseAgentState:
    """工具验证节点，验证工具调用是否有效"""
    tool_call_str = state.get("tool_call_str")
    action_parser = agent_object_manager.get_action_parser(state.get("thread_id"))
    # 解析工具调用前先注入当前屏幕尺寸，避免坐标类动作在不同分辨率上解析失真。
    action_parser.change_phone_dimensions(
        width=state.get("screenshot_dimensions")[0],
        height=state.get("screenshot_dimensions")[1],
    )
    tool_call = action_parser.to_mcp_tool_call(tool_call_str)
    if tool_call is None:
        tool_call = {"name": "error_action", "arguments": {"content": tool_call_str}}
    state.update(tool_call=tool_call)

    tools = agent_object_manager.get_tools(state.get("thread_id"))
    tool_name = tool_call.get("name")

    if tools.is_special_tool(tool_name):
        # 特殊工具不走通用工具执行节点，而是在这里直接消费并写回专用消息，
        # 例如结束、等待或其他需要特殊渲染/记忆策略的动作。
        sse_writer = get_stream_writer()
        content = await tools.exec(tool_call)
        sse_writer(format_sse(tools.get_special_message(tool_name, content, state)))
        state.update(tool_output=tools.get_special_memory(tool_name))
        return state

    # 普通技能会继续流向 tool_node，在那里真正调用新版 mobile_use_service。
    return state


async def tool_node(state: MobileUseAgentState) -> MobileUseAgentState:
    """工具执行节点，执行工具调用"""
    # 如果前端已经断开 SSE，就没有必要继续向下执行真实操作，直接终止这一轮。
    if agent_object_manager.get_sse_connection(state.get("thread_id")).is_set():
        logger.info("tool_node start, sse 断开链接")
        raise SSEException()

    tool_call = state.get("tool_call")
    sse_writer = get_stream_writer()
    # 先把工具输入透出给前端，保证用户可以看到模型到底决定调用了什么动作。
    sse_writer(get_writer_tool_input(state, tool_call))

    logger.info(f"tool_call========: {tool_call}")
    try:
        tools = agent_object_manager.get_tools(state.get("thread_id"))
        result = await tools.exec(tool_call)
        # 这里把原始结果包装成统一字符串，后续迭代时模型会把它作为上一轮工具反馈继续消费。
        success, output = normalize_tool_execution_result(tool_call, result)
        state.update(tool_output=output)
        # 某些设备操作需要等待界面稳定，否则下一轮截图可能仍停留在旧画面。
        if success:
            await asyncio.sleep(state.get("step_interval"))

    except Exception as e:
        logger.error(f"tool_call_client.call error: {e}")
        output = {"result": f"Error: {str(e)}"}
        # 失败时先发 stop 事件，让前端知道这次工具调用提前终止。
        sse_writer((get_writer_tool_output(state, tool_call, output, status="stop")))
        state.update(tool_output=output)

    logger.info(f"tool_output========: {state.get('tool_output')}")

    # 无论是否异常，最后都写一条工具输出事件，保持前端状态机的消费路径一致。
    if "操作下发失败" in output["result"] or output["result"].startswith("Error:"):
        sse_writer(get_writer_tool_output(state, tool_call, output, status="stop"))
    else:
        sse_writer(get_writer_tool_output(state, tool_call, output, status="success"))

    return state


def handle_parse_failure(state: MobileUseAgentState) -> bool:
    tool_call = state.get("tool_call")

    # 约定 `error_action` 代表动作解析失败，而不是模型真的想调用名为 error_action 的工具。
    if not tool_call or (
        isinstance(tool_call, dict) and tool_call.get("name") == "error_action"
    ):
        iteration_count = state.get("iteration_count", 0)
        max_iterations = state.get("max_iterations")

        # 只要还没达到上限，就允许回到模型节点重新生成动作，避免一次解析失败直接结束任务。
        if iteration_count < max_iterations:
            return True

    return False


async def should_react_continue(state: MobileUseAgentState) -> str:
    """条件边，决定是否继续执行"""
    # 这是工具执行后的轮次控制：
    # 达到最大步数则结束，否则继续回到模型节点观察最新页面并做下一轮决策。
    iteration_count = state.get("iteration_count", 0)
    max_iterations = state.get(
        "max_iterations",
    )

    if iteration_count >= max_iterations:
        return "finish"

    return "continue"


async def should_tool_exec_continue(state: MobileUseAgentState) -> str:
    """条件边，决定是否继续执行"""
    tool_call = state.get("tool_call")
    # 工具解析失败，重新生成action
    if not tool_call or tool_call.get("name") == "error_action":
        return "retry"

    tools = agent_object_manager.get_tools(state.get("thread_id"))
    if tools.is_special_tool(tool_call.get("name")):
        # 特殊工具已经在 tool_valid_node 中就地执行完毕，因此图流程可以直接结束。
        return "finish"

    # 工具执行成功，继续执行
    return "continue"
