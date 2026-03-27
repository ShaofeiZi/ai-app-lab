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

from mobile_agent.agent.infra.message_web import SummaryMessageData
from mobile_agent.agent.tools.tool.abc import SpecialTool


class FinishedTool(SpecialTool):
    """
    这是告诉 agent “任务已经完成”的特殊工具。

    它的作用不是去操作手机，而是把最终结果正式收口：
    - handler 返回总结文本
    - special_message 生成给前端展示的 summary 消息
    - special_memory 生成一段供下一轮对话使用的记忆提示
    """

    def __init__(self):
        super().__init__(
            name="finished",
            description="If the task is completed, call this action. You must summary the task result in content.",
            parameters={
                "content": {
                    "type": "string",
                    "description": "The content to summary the task result",
                }
            },
        )

    async def handler(self, args: dict):
        # finished 的执行结果非常简单：直接把模型总结的 content 往上传回去。
        return args.get("content")

    def special_message(self, content: str, args: dict):
        # 这里把普通字符串封装成前端可识别的 summary 事件。
        # 这样页面就能把“任务总结”作为一种独立消息类型展示出来。
        return SummaryMessageData(
            id=args.get("chunk_id"),
            task_id=args.get("task_id"),
            role="assistant",
            type="summary",
            content=content,
        )

    def special_memory(self):
        # 这段记忆相当于告诉后续轮次：
        # “上一轮已经完成，请根据新的用户输入开始下一步，而不是重复之前的收尾。”
        return "上一轮任务已经完成，更多的根据用户新的输入完成任务"
