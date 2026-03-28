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

from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from openai.types.chat import (
    ChatCompletionContentPartImageParam,
    ChatCompletionContentPartTextParam,
)
from openai.types.chat.chat_completion_content_part_image_param import ImageURL
from datetime import datetime

from mobile_agent.agent.memory.messages import AgentMessages


class ContextManager:
    def __init__(self, messages: list[BaseMessage]):
        # AgentMessages 是对原始消息数组的再封装。
        # 这样后续插入、替换 system message、裁剪图片等操作可以集中在一个对象上完成。
        self._messages = AgentMessages(messages)

    def _append(self, message: BaseMessage):
        self._messages.append(message)

    def get_messages(self):
        return self._messages.get_messages()

    def length(self):
        return self._messages.length()

    def add_system_message(self, message: str):
        """系统消息"""
        system_message = SystemMessage(content=message)
        # system message 永远放在最前面。
        # 如果原来已经有 system message，就替换它，避免堆出多条互相冲突的系统指令。
        if self._messages.length() > 0 and self._messages.index(0).type == "system":
            self._messages.replace(0, system_message)
        else:
            self._messages.insert(0, system_message)

    def add_user_initial_message(self, message: str, screenshot_url: str):
        """初始消息"""
        # 首轮消息会同时带上“当前时间、用户任务、第一张截图”。
        # 这样模型一开始就知道目标是什么，也知道当前手机屏幕长什么样。
        user_content = f"当前时间点 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ，用户任务: {message}\n请帮我完成任务"
        self._append(
            ContextManager.get_snapshot_user_prompt(
                url=screenshot_url, user_content=user_content
            )
        )

    def add_user_iteration_message(
        self,
        message: str,
        iteration_count: int,
        tool_output: str,
        screenshot_url: str,
        screenshot_dimensions: tuple,
    ):
        """
        ReAct 迭代中的消息
        """
        # 后续轮次的 user message 本质上是在告诉模型：
        # “这是原任务、这是上一轮工具执行结果、这是执行后的新截图，请继续判断下一步”。
        user_content = (
            f"当前轮次迭代次数 {iteration_count}\n"
            f"用户任务: {message}\n"
            f"当前轮次工具下发结果: {tool_output}， "
            f"请观察截图， 当前截图分辨率为 {screenshot_dimensions[0]}x{screenshot_dimensions[1]} 并根据截图和工具下发结果 \n"
        )
        self._append(
            ContextManager.get_snapshot_user_prompt(
                url=screenshot_url, user_content=user_content
            )
        )

    def add_ai_message(self, content: str):
        """添加AI消息"""
        # 把模型原始回答也存回上下文，下一轮模型就能看到自己上一轮说过什么。
        self._append(AIMessage(role="assistant", content=content))

    def keep_last_n_images_in_messages(self, keep_n: int):
        """保留最后n张图片URL"""
        # 多轮执行时，图片消息会越来越多，prompt 会迅速变大。
        # 这里的策略是只保留最近 N 张截图，让模型仍能看到近期状态变化，但不至于把上下文撑爆。
        all_image_parts = []
        messages = self._messages.get_messages()
        for msg in messages:
            if msg.type == "human" and isinstance(msg.content, list):
                for i, part in enumerate(msg.content):
                    if isinstance(part, dict) and part.get("type") == "image_url":
                        # 记录“哪条消息里有哪张图片”，后面就能从旧到新删除。
                        all_image_parts.append((msg, part, i))
        total_images = len(all_image_parts)
        if total_images <= keep_n:
            return
        to_remove_count = total_images - keep_n
        # 从最早的图片开始删，保证最近几轮的视觉上下文还在。
        for i in range(to_remove_count):
            msg, part, _ = all_image_parts[i]
            if part in msg.content:
                msg.content.remove(part)

        self._messages.replace_all(messages)


    @staticmethod
    def get_snapshot_user_prompt(url: str, user_content: str) -> HumanMessage:
        # OpenAI 多模态消息的格式不是简单字符串，
        # 而是一个 content 列表，其中一项是图片，一项是文字说明。
        snap_content = ChatCompletionContentPartImageParam(
            image_url=ImageURL(url=url), type="image_url"
        )
        user_message = ChatCompletionContentPartTextParam(
            text=user_content, type="text"
        )
        # 最终生成的是一条 HumanMessage，模型会把它理解成“用户给的一次多模态输入”。
        screenshot_message = HumanMessage(
            role="user", content=[snap_content, user_message]
        )
        return screenshot_message
