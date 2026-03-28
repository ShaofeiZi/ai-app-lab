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

from mobile_agent.agent.cost.calculator import CostCalculator
from mobile_agent.agent.mobile.doubao_action_parser import (
    DoubaoActionSpaceParser,
)
from mobile_agent.agent.mobile.client import Mobile
from mobile_agent.agent.skills.executor import SkillExecutor
from mobile_agent.agent.skills.policy import SkillPolicyResolver
from mobile_agent.agent.skills.registry import SkillRegistry
from mobile_agent.agent.skills.service_client import build_default_service_client
from mobile_agent.agent.tools.tools import Tools
from .infra.logger import AgentLogger
from mobile_agent.config.settings import get_agent_config, get_settings
from mobile_agent.agent.prompt.doubao_vision_pro import doubao_system_prompt
from mobile_agent.agent.graph.builder import graph
from mobile_agent.agent.graph.context import agent_object_manager


class MobileUseAgent:
    name = "mobile_use"

    def __init__(self):
        # 这里初始化的是“不会跟某一次任务绑定”的长期成员：
        # 例如提示词、日志器、MCP 连接管理器、云手机客户端和成本统计器。
        self.prompt = doubao_system_prompt
        self.logger = AgentLogger(__name__)

        agent_config = get_agent_config(MobileUseAgent.name)
        self.logger.info(f"agent_config: {agent_config}")

        self.max_steps = agent_config.max_steps
        self.step_interval = agent_config.step_interval
        self.service_client = build_default_service_client()
        self.mobile_client = Mobile(service_client=self.service_client)
        self.cost_calculator = CostCalculator(MobileUseAgent.name)
        self.tools = None

    async def initialize(
        self,
        pod_id: str,
        auth_token: str,
        product_id: str,
        tos_bucket: str,
        tos_region: str,
        tos_endpoint: str,
    ):
        # initialize 只做“把这台云手机运行起来需要的依赖装好”，
        # 还不真正开始执行用户任务。
        self.logger.set_context(pod_id=pod_id)
        await self.mobile_client.initialize(
            pod_id=pod_id,
            product_id=product_id,
            tos_bucket=tos_bucket,
            tos_region=tos_region,
            tos_endpoint=tos_endpoint,
            auth_token=auth_token,
        )
        # 下面这段是新版 skill 方案的核心装配过程：
        # 1. 先构建完整技能注册表
        # 2. 再按策略过滤
        # 3. 最后把剩余技能装配成 Tools 对象
        registry = SkillRegistry()
        settings = get_settings()
        policy = SkillPolicyResolver(
            allowlist=set(settings.skill_policy.allowlist)
            if settings.skill_policy.allowlist is not None
            else None,
            denylist=set(settings.skill_policy.denylist),
        )
        filtered_skills = policy.filter(registry.list_all(), context={"pod_id": pod_id})
        executor = SkillExecutor(service=self.service_client)
        self.tools = await Tools.from_skill_registry(
            registry=SkillRegistry.from_skills(filtered_skills),
            executor=executor,
            # 这里把 session 放进工具上下文，
            # 这样每次具体执行技能时都能拿到访问新服务所需的云手机身份信息。
            context={"session": self.mobile_client.get_session_payload()},
        )

        return self

    async def aclose(self) -> None:
        # agent 生命周期结束时，把底层 HTTP 连接也一起释放掉。
        await self.service_client.aclose()

    async def run(
        self,
        query: str,
        is_stream: bool,
        task_id: str,
        session_id: str,
        thread_id: str,
        sse_connection: asyncio.Event,
        phone_width: int,
        phone_height: int,
    ):
        try:
            # 一个 thread_id 对应一次 LangGraph 执行上下文。
            # 这里先把和本次任务强相关的字段写到实例或初始状态里，后面每个图节点都会依赖这些信息。
            self.logger.set_context(thread_id=session_id, chat_thread_id=thread_id)
            self.task_id = task_id
            self.stream = is_stream
            initial_state = {
                "user_prompt": query,
                "iteration_count": 0,
                "task_id": task_id,
                "thread_id": thread_id,
                "is_stream": is_stream,
                "max_iterations": self.max_steps,
                "step_interval": self.step_interval,
            }
            # LangGraph 的 state 适合放“可序列化、可追踪”的轻量数据，
            # 但像 mobile_client、tools、action_parser 这种复杂对象不适合反复塞进 state。
            # 所以这里交给 agent_object_manager，用 thread_id 做索引集中保管。
            agent_object_manager.create_context(
                thread_id=thread_id,
                mobile_client=self.mobile_client,
                tools=self.tools,
                sse_connection=sse_connection,
                action_parser=DoubaoActionSpaceParser(
                    phone_width=phone_width,
                    phone_height=phone_height,
                ),
                cost_calculator=self.cost_calculator,
            )

            config = {
                "configurable": {"thread_id": thread_id},
                "recursion_limit": self.max_steps * 3,
            }

            # graph.astream 会持续产出 LangGraph 的流式事件。
            # 当前函数不自己“消费”这些事件，而是继续 yield 给上层路由，
            # 这样 HTTP SSE 响应就能把每一步思考和工具执行过程实时推给前端。
            async for chunk in graph.astream(
                input=initial_state,
                config=config,
                stream_mode=["messages", "custom"],
            ):
                yield chunk
        finally:
            if self.stream:
                self.logger.info("stream mode, not support cost calculator")
            else:
                self.cost_calculator.print_cost()
            # 不管任务是成功、失败还是被取消，最后都要清掉 thread 上下文，
            # 否则旧任务残留对象会污染后续会话，甚至造成内存泄漏。
            agent_object_manager.destroy_context(thread_id)
