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

from typing import Any, Dict, Optional
from langgraph.prebuilt.chat_agent_executor import AgentState
from mobile_agent.agent.infra.model import ToolCall
from mobile_agent.agent.tools.tools import Tools


class SharedState(AgentState):
    # thread_id 用来索引线程级上下文对象。
    thread_id: str
    # task_id 是发给前端时标记这一轮任务的唯一标识。
    task_id: str
    # chunk_id 常用于把一次模型输出串成同一条前端消息。
    chunk_id: str
    # user_prompt 是用户最初下达的目标，例如“安装某个 APP 并完成某件事”。
    user_prompt: str
    is_stream: bool  # 是否流式输出
    iteration_count: int  # 当前迭代次数
    max_iterations: int  # 最大迭代次数


class ToolCallState(SharedState):
    tools: Tools  # 当前任务可用的工具集合
    tool_call_str: Optional[str]  # 工具调用字符串
    tool_call: ToolCall  # MCP工具调用
    tool_output: Optional[Dict[str, Any]]  # 工具调用的输出结果
    current_tool_call_id: str  # 前端用它把同一次工具调用的输入/输出事件关联起来


class MobileUseAgentState(ToolCallState):
    screenshot: Optional[str]  # 截图的url链接
    screenshot_dimensions: Optional[tuple[int, int]]  # 截图的(宽度, 高度)信息
    # 手机界面不是瞬间稳定的，所以工具执行后通常要留一点缓冲时间再截图。
    step_interval: float
