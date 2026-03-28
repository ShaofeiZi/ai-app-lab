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
import uuid
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import logging
from mobile_agent.exception.sse import SSEException
from mobile_agent.agent.graph.sse_output import (
    format_sse,
    stream_messages,
)
from mobile_agent.agent.infra.message_web import SummaryMessageData
from mobile_agent.agent.mobile_use_agent import MobileUseAgent
from mobile_agent.middleware.middleware import APIException
from mobile_agent.service.session.manager import session_manager
import langgraph.errors
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# 创建路由
router = APIRouter(
    prefix="/mobile-use/api/v1/agent",
    tags=["agent"],
)


async def stream_generator(
    task_id: str,
    agent: MobileUseAgent,
    is_stream: bool,
    message: str,
    thread_id: str,
):
    try:
        # thread_id 对应的是前端这次云手机会话，
        # session 里保存了 pod 大小、鉴权信息、chat_thread_id 等后续必需数据。
        session = session_manager.get_thread_state(thread_id)
        async for chunk in agent.run(
            message,
            is_stream=is_stream,
            session_id=thread_id,
            thread_id=session.chat_thread_id,
            task_id=task_id,
            sse_connection=session.sse_connection,
            phone_width=session.pod_size.width,
            phone_height=session.pod_size.height,
        ):
            if session.sse_connection.is_set():
                # 前端如果主动点了取消，会把 Event 置位。
                # 这里尽快终止执行，避免已经没人在看时还继续操作真实设备。
                agent.logger.info("主动取消任务")
                raise SSEException()
            for message_part in stream_messages(chunk, is_stream, agent.task_id):
                # 一个 LangGraph chunk 可能会被拆成多条前端 SSE 消息，
                # 比如 think 片段、工具输入、工具输出等。
                yield message_part

    except langgraph.errors.GraphRecursionError:
        agent.logger.info(
            f"Agent stream for thread {thread_id} was GraphRecursionError"
        )
        yield format_sse(
            SummaryMessageData(
                id=str(uuid.uuid4()),
                task_id=task_id,
                role="assistant",
                type="summary",
                content="Agent 对话次数到达限制，如您想要继续对话，请提示“继续”",
            )
        )
    except asyncio.CancelledError:
        # 这里通常对应服务端任务被取消或连接中断，不再继续向外抛业务异常。
        agent.logger.info(f"Agent stream for thread {thread_id} was cancelled")
    except SSEException:
        # SSEException 是“主动停止”的正常控制流，不应当被当成真正错误报警。
        agent.logger.info("sse closed")
    except Exception as e:
        # 忽略 LangGraph 内部的回调错误
        if "callback" in str(e).lower() and "nonetype" in str(e).lower():
            agent.logger.warning(f"LangGraph callback error (ignored): {e}")
        agent.logger.error(f"run error: {e}")
        raise e
    finally:
        # 不论生成器怎么结束，都关闭 agent 侧的 MCP 连接。
        await agent.aclose()


class AgentStreamRequest(BaseModel):
    message: str = Field(..., description="用户输入的消息")
    thread_id: str = Field(..., description="线程ID")
    is_stream: bool = Field(False, description="是否流式响应")


@router.post("/stream")
async def agent_stream(request: Request, body: AgentStreamRequest):
    """
    流式响应API

    Args:
        request: 包含message、podId和threadId的请求

    Returns:
        StreamingResponse: 事件流响应
    """
    try:
        # 账户 ID 来自中间件，message / thread_id 来自请求体。
        account_id = request.state.account_id
        user_prompt = body.message
        thread_id = body.thread_id
        is_stream = body.is_stream

        logger.info(f"收到请求: {user_prompt}, {thread_id}")

        if not user_prompt or not thread_id:
            # 对于参数验证错误，使用400状态码
            raise APIException(code=200, message="message 和 thread_id 是必需的")

        if not session_manager.has_thread(thread_id):
            raise APIException(code=403, message="会话已被清除，请重新开始会话")

        session = session_manager.get_thread_state(thread_id)
        # set_sse_connection 会为这个 thread 准备一份 Event 对象，
        # 之后取消任务时就靠它来通知执行链路尽快停下。
        session_manager.set_sse_connection(thread_id)

        if session.account_id != account_id:
            raise APIException(code=403, message="当前会话不匹配")

        agent = MobileUseAgent()
        logger.info(
            f"初始化agent: {thread_id} {session.chat_thread_id} {session.pod_id}, {session.product_id}"
        )
        await agent.initialize(
            pod_id=session.pod_id,
            auth_token=session.authorization_token,
            product_id=session.product_id,
            tos_bucket=session.tos_bucket,
            tos_region=session.tos_region,
            tos_endpoint=session.tos_endpoint,
        )
        logger.info(
            f"agent 初始化成功: {session.chat_thread_id} {session.pod_id}, {session.product_id}"
        )

        task_id = str(uuid.uuid4())
        # StreamingResponse 会把生成器里的内容逐段写给浏览器，
        # 因此前端可以边看 Agent 思考，边看工具执行，不必等整个任务结束。
        return StreamingResponse(
            content=stream_generator(task_id, agent, is_stream, user_prompt, thread_id),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache, no-transform",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
                "Content-Type": "text/event-stream",
                "Access-Control-Allow-Origin": "*",
            },
        )

    except APIException as api_error:
        # 抛出让中间件处理
        logger.exception(f"API error: {api_error}")
        raise api_error

    except Exception as agent_error:
        # 对于未知异常，使用通用错误处理
        logger.exception(f"Agent error: {agent_error}")
        raise agent_error


class CancelAgentRequest(BaseModel):
    thread_id: str = Field(..., description="线程ID")


@router.post("/cancel")
async def cancel_agent(request: Request, body: CancelAgentRequest):
    """
    取消智能代理
    """
    account_id = request.state.account_id
    thread_id = body.thread_id

    if not thread_id:
        raise APIException(code=400, message="thread_id 是必需的")

    if session_manager.has_thread(thread_id):
        session = session_manager.get_thread_state(thread_id)
        if session.account_id != account_id:
            raise APIException(code=403, message="会话已被清除，请重新开始会话")

    # 取消动作本质上不是“杀掉 Python 进程”，
    # 而是把对应 thread 的 SSE 断开标记设为 true，让执行链路自愿停下来。
    session_manager.stop_sse_connection(thread_id)

    # 返回成功结果，会被中间件包装为 {"result": {"success": true}}
    return {"success": True}
