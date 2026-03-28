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

from typing import Optional
from pydantic import BaseModel


class ToolFunction(BaseModel):
    """
    这是工具调用里真正的“函数描述”部分。

    可以把它理解成：
    - `name` 说明要调用哪个工具
    - `arguments` 是传给这个工具的参数，通常是 JSON 字符串
    """

    name: str
    arguments: str


class ToolCall(BaseModel):
    """
    这是和 OpenAI / LangChain 工具调用格式对齐的数据模型。

    Agent 在“模型产出动作”与“本地真正执行工具”之间，需要一个统一的数据载体。
    这个类就是那层中间表示，方便不同模块用同一种结构传递工具调用信息。
    """

    id: Optional[str] = None  # 可选字段，当通过提示词做工具调用时可能为空
    type: str
    function: ToolFunction
    index: Optional[int] = None
