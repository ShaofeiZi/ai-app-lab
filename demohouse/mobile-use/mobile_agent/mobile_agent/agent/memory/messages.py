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
from typing import List
from langchain_core.messages import BaseMessage


class AgentMessages:
    """
    这是对消息列表的一层轻包装。

    直接操作原始 list 虽然也能完成工作，但这里额外包一层有两个好处：
    1. 把常见操作统一收口，例如追加、替换、按索引取值。
    2. 把“消息转换成 OpenAI 所需格式”这样的领域逻辑放到一个固定位置，
       避免散落在业务代码各处。
    """

    def __init__(self, messages: List[BaseMessage]):
        self._messages: List[BaseMessage] = messages

    def get_messages(self):
        # 返回当前保存的完整消息列表，供上层继续拼接 prompt 或写入状态。
        return self._messages

    def length(self):
        return len(self._messages)

    def index(self, index: int) -> BaseMessage:
        # 这里显式做边界检查，是为了把“索引越界”变成更好理解的业务报错。
        if self._messages and 0 <= index < self.length():
            return self._messages[index]
        raise IndexError(f"消息索引 {index} 超出范围")

    def append(self, message: BaseMessage):
        # 在对话末尾追加一条新消息，最常见的场景是加入新的用户输入或模型回复。
        self._messages.append(message)

    def replace(self, idx, message):
        # 用新消息替换指定位置的旧消息，常用于“先占位，后回填”。
        if 0 <= idx < len(self._messages):
            self._messages[idx] = message
        else:
            raise IndexError(f"消息索引 {idx} 超出范围")

    def insert(self, idx, message):
        # 插入比 append 更灵活，适合把 system/tool 消息插回到中间位置。
        if 0 <= idx <= len(self._messages):
            self._messages.insert(idx, message)
        else:
            raise IndexError(f"插入索引 {idx} 超出范围")

    def replace_all(self, messages):
        # 整体替换通常用于“裁剪历史消息”或“从持久化存储恢复消息”。
        self._messages = messages

    @staticmethod
    def convert_langchain_to_openai_messages(
        messages: List[BaseMessage],
    ) -> List[dict]:
        """
        将 LangChain 的消息对象转换成 OpenAI 接口所需的字典格式。

        两套框架都在描述“对话消息”，但字段名字和组织方式并不完全一样。
        所以这里要做一次“翻译”，把上游内部对象整理成下游 API 能直接消费的数据。
        """
        openai_messages = []

        for msg in messages:
            # 第一步先把不同框架里的消息类型名称映射成 OpenAI 熟悉的 role。
            if msg.type == "human":
                role = "user"
            elif msg.type == "ai":
                role = "assistant"
            elif msg.type == "system":
                role = "system"
            elif msg.type == "tool":
                role = "tool"
            elif msg.type == "function":
                role = "function"
            else:
                role = msg.type  # 兜底

            message_dict = {"role": role, "content": msg.content}

            # 如果这条 AI 消息包含工具调用信息，还要把工具名和参数一并带上。
            # 注意：OpenAI 期望 arguments 是 JSON 字符串，而不是 Python dict。
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                message_dict["tool_calls"] = []
                for tool_call in msg.tool_calls:
                    message_dict["tool_calls"].append(
                        {
                            "id": tool_call["id"],
                            "type": "function",
                            "function": {
                                "name": tool_call["name"],
                                "arguments": json.dumps(tool_call["args"]),
                            },
                        }
                    )

            # tool 消息通常要指明“它是在回应哪个 tool_call”，
            # 否则模型很难把一条工具结果和之前的调用意图对应起来。
            if hasattr(msg, "tool_call_id") and msg.tool_call_id:
                message_dict["tool_call_id"] = msg.tool_call_id

            openai_messages.append(message_dict)

        return openai_messages
