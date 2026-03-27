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

from typing import Literal, Optional
from pydantic import BaseModel


class MessageMeta(BaseModel):
    """
    这里定义的是一条消息附带的“补充说明”。

    对初学者来说，可以把它理解成消息正文旁边的一张小标签：
    - 这条内容是哪个模型生成的
    - 大概用了多少 token
    - 为什么这次输出结束了

    这些字段本身不会直接显示给用户，但前后端在调试、统计和排查问题时会用到。
    """

    finish_reason: Optional[str] = None
    model: Optional[str] = None
    prompt_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


class SSEContentMessageData(BaseModel):
    """
    这是最基础的 SSE 文本消息结构。

    SSE 是一种“服务端不断往前端推送小段消息”的机制，
    所以前端收到的不是一次性的大结果，而是一条条增量事件。
    这个类描述的就是这些事件里最常见的一类：带正文文本的消息。
    """

    id: str
    task_id: str
    role: str
    content: str
    response_meta: Optional[MessageMeta] = None


class SSEThinkMessageData(SSEContentMessageData):
    """
    think 类型表示“模型正在思考中的解释文本”。

    它继承了普通文本消息的全部字段，只额外把 type 固定成 "think"，
    这样前端就能根据 type 决定用“思考气泡”而不是普通聊天气泡来渲染。
    """

    type: Literal["think"]


class UserInterruptMessageData(SSEContentMessageData):
    """
    这类消息表示“当前流程需要用户插话或补充输入”。

    例如模型卡住了、信息不够了，或者需要用户确认下一步时，
    后端可以发出 user_interrupt，让前端知道这不是普通回答，
    而是一次需要用户参与的中断点。
    """

    type: Literal["user_interrupt"]
    interrupt_type: Literal["text"]


class SummaryMessageData(SSEContentMessageData):
    """
    这是任务完成后的总结消息。

    它和 think 一样是文本消息，但语义不同：
    think 代表中间过程，
    summary 代表“这一轮任务最后得出的结论或结果说明”。
    """

    type: Literal["summary"]


class SSEToolCallMessageData(BaseModel):
    """
    这是“工具调用事件”的专用数据结构。

    和普通文本消息不同，工具调用需要描述更多状态：
    - 是哪个工具
    - 处于开始、结束还是成功
    - 当前这条数据是工具输入还是工具输出

    前端据此可以把工具执行过程展示成一段可追踪的时间线。
    """

    id: str
    task_id: str
    tool_id: str
    type: Literal["tool"]
    status: Literal["start", "stop", "success"]
    tool_type: Literal["tool_input", "tool_output"]
    tool_name: str
    tool_input: Optional[str] = None
    tool_output: Optional[str] = None
