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

from abc import ABC, abstractmethod
import json
from typing import Optional


class Tool(ABC):
    """
    所有工具的抽象基类。

    这里统一了一个工具最基本的三件事：
    1. 它叫什么，给模型看的说明是什么。
    2. 它接收什么参数。
    3. 真正执行时由哪个 handler 负责。

    这样无论是本地特殊工具，还是从 MCP 拉回来的远程工具，
    上层都可以用一致的方式管理和调用。
    """

    def __init__(
        self,
        name: str,
        description: str,
        parameters: dict,
        is_special_tool: Optional[bool] = False,
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.is_special_tool = is_special_tool

    async def call(self, args: Optional[dict] = {}) -> str:
        # call 是统一入口，内部再把具体工作交给子类实现的 handler。
        # 这里顺手把 None 规范成空字符串，减少上层判空分支。
        result = await self.handler(args)
        if result is None:
            return ""
        return result

    @abstractmethod
    async def handler(self, args: Optional[dict] = {}) -> str | None:
        # 抽象方法的意思是：父类只规定接口，不提供具体实现。
        # 每个具体工具都必须给出自己的处理逻辑，否则这个类不能直接实例化。
        pass

    def get_tool_schema_for_openai(self):
        # 这里返回的是 OpenAI function calling 需要的标准 schema。
        # 上层会把它们统一发给模型，让模型知道“有哪些工具可用、怎么传参”。
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def get_prompt_string(self):
        # 有些场景不直接走 function calling，而是把工具说明拼进 prompt 文本里。
        # 这个方法就是把结构化参数压成一段可阅读的字符串。
        json_str = json.dumps(self.parameters)
        return (
            f"name: {self.name}\ndescription: {self.description}\narguments: {json_str}"
        )


class SpecialTool(Tool):
    """
    SpecialTool 表示“除了执行结果，还需要额外特殊处理”的工具。

    例如 finished 这种工具，不只是返回一段文本，
    还会生成一条适合前端展示的总结消息，并写入一段特殊记忆。
    """

    def __init__(self, name: str, description: str, parameters: dict):
        super().__init__(name, description, parameters, is_special_tool=True)

    def special_message(self, content: str, args: dict) -> str | None:
        # 让子类按需生成额外消息对象；默认不做任何事。
        pass

    def special_memory(self) -> str | None:
        # 让子类返回一段“执行后记忆”，供 agent 在下一轮继续参考。
        pass
