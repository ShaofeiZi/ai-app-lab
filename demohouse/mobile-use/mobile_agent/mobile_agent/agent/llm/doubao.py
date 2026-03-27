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

from typing import List
from langchain_core.messages import BaseMessage
import asyncio
import logging
from mobile_agent.config.settings import get_agent_config, get_model_config
from mobile_agent.agent.memory.messages import AgentMessages
from mobile_agent.agent.prompt.doubao_vision_pro import doubao_system_prompt
from mobile_agent.agent.graph.context import agent_object_manager
from mobile_agent.agent.llm.stream_pipe import stream_pipeline
from langchain_openai import ChatOpenAI
from openai import OpenAI


class DoubaoLLM:
    prompt = doubao_system_prompt

    def __init__(self, thread_id: str, is_stream: bool):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.is_stream = is_stream
        self.thread_id = thread_id

        # 这里从统一配置里取出当前 agent 该用哪个模型、温度是多少、最大输出多少 token。
        agent_config = get_agent_config("mobile_use")
        if agent_config.modelKey:
            model_config = get_model_config(agent_config.modelKey)
            self.model_name = model_config.model
            self.base_url = model_config.base_url
            self.api_key = model_config.api_key
            self.temperature = model_config.temperature
            self.max_tokens = model_config.max_tokens

        # LangChain 版本的 ChatOpenAI 主要用在流式场景；
        # 非流式场景下，下面的 _invoke_sync_model 还会直接走 OpenAI 客户端，
        # 因为那样更容易拿到 token usage 统计。
        self.llm = ChatOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            model=self.model_name,
            streaming=is_stream,
            max_completion_tokens=self.max_tokens,
            temperature=self.temperature,
            stream_usage=True,
        )

    async def async_chat(
        self, messages: List[BaseMessage]
    ) -> tuple[str, str, str, str]:
        """调用模型并处理重试逻辑"""
        # 模型调用不是 100% 稳定的，可能遇到临时网络问题或上游报错。
        # 这里做一个有限次数重试，避免偶发失败直接让整轮任务中断。
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                chunk_id, content, summary, tool_call = await self._invoke_model(
                    messages
                )

                return chunk_id, content, summary, tool_call

            except asyncio.CancelledError as e:
                # cancel 不处理，直接向外抛出
                raise e

            except Exception as e:
                retry_count += 1
                self.logger.error(f"模型调用失败，重试第 {retry_count} 次。错误: {e}")

                if retry_count >= max_retries:
                    raise e

                await asyncio.sleep(1)

    async def _invoke_model(self, messages: List[BaseMessage]) -> tuple[str, str, str]:
        # 是否流式会直接决定调用哪条分支：
        # 流式分支逐块消费 token，非流式分支一次拿完整结果。
        if self.is_stream:
            return await self._invoke_stream_model(messages)
        else:
            return await self._invoke_sync_model(messages)

    async def _invoke_stream_model(
        self, messages: List[BaseMessage]
    ) -> tuple[str, str, str]:
        # 流式模式下，这里并不直接把每个 chunk 返回给上层；
        # 而是交给 stream_pipeline 聚合，最后得到 content / summary / tool_call 三段结果。
        index = 0
        chunk_id = ""
        response = self.llm.astream(messages)
        async for chunk in response:
            if index == 0:
                # 第一块 chunk 最重要的是拿到稳定的 chunk_id，
                # 前端和后续图节点都靠它来串联这一轮模型输出。
                chunk_id = chunk.id
                stream_pipeline.create(id=chunk_id)
            index += 1
        content, summary, tool_call = stream_pipeline.complete(id=chunk_id)

        return chunk_id, content, summary, tool_call

    async def _invoke_sync_model(
        self, messages: List[BaseMessage]
    ) -> tuple[str, str, str]:
        use_openai_client = True
        # Ark API 在 LangChain 这层不方便稳定拿到 token usage，
        # 所以这里在非流式模式下直接走 OpenAI 兼容客户端。
        if use_openai_client:
            client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            response = client.chat.completions.create(
                model=self.model_name,
                messages=AgentMessages.convert_langchain_to_openai_messages(messages),
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            content = response.choices[0].message.content
            output_tokens = response.usage.completion_tokens
            input_tokens = response.usage.prompt_tokens

            cost_calculator = agent_object_manager.get_cost_calculator(self.thread_id)
            if cost_calculator:
                # 把输入 / 输出 token 记到成本统计器里，便于后面估算调用成本。
                cost_calculator.record_cost(
                    input_tokens=input_tokens, output_tokens=output_tokens
                )

        else:
            response = self.llm.invoke(messages)
            content = response.content
        # 同步模式虽然不是边生成边展示，但仍然复用同一个 stream_pipeline，
        # 这样最终得到的 summary / tool_call 解析流程和流式模式保持一致。
        stream_pipeline.create(id=response.id)
        stream_pipeline.pipe(id=response.id, delta=content)
        content, summary, tool_call = stream_pipeline.complete(id=response.id)

        return response.id, content, summary, tool_call
