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

"""
Agent相关路由

提供与云手机Agent交互的核心接口，包括：
- 发送用户消息并获取流式响应
- 取消正在执行的任务
"""

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

router = APIRouter(
    prefix="/mobile-use/api/v1/agent",
    tags=["Agent交互"],
)


async def stream_generator(
    task_id: str,
    agent: MobileUseAgent,
    is_stream: bool,
    message: str,
    thread_id: str,
):
    """
    SSE流生成器

    从Agent获取响应并转换为SSE格式流式推送给前端。
    """
    try:
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
                agent.logger.info("主动取消任务")
                raise SSEException()
            for message_part in stream_messages(chunk, is_stream, agent.task_id):
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
                content="Agent 对话次数到达限制，如您想要继续对话，请提示「继续」",
            )
        )
    except asyncio.CancelledError:
        agent.logger.info(f"Agent stream for thread {thread_id} was cancelled")
    except SSEException:
        agent.logger.info("sse closed")
    except Exception as e:
        if "callback" in str(e).lower() and "nonetype" in str(e).lower():
            agent.logger.warning(f"LangGraph callback error (ignored): {e}")
        agent.logger.error(f"run error: {e}")
        raise e
    finally:
        await agent.aclose()


class AgentStreamRequest(BaseModel):
    """
    Agent流式请求模型

    用于发送用户消息给Agent并获取流式响应。
    """
    message: str = Field(
        ...,
        description="用户输入的消息/指令",
        examples=["帮我打开微信，然后给朋友发一条消息"]
    )
    thread_id: str = Field(
        ...,
        description="线程ID，对应已创建的云手机会话",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    is_stream: bool = Field(
        False,
        description="是否启用流式响应模式。true则逐段返回AI思考过程和工具执行结果"
    )


class CancelAgentRequest(BaseModel):
    """
    取消Agent任务请求模型
    """
    thread_id: str = Field(
        ...,
        description="线程ID，要取消的任务所属的会话",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )


class CancelAgentResponse(BaseModel):
    """
    取消Agent任务响应模型
    """
    success: bool = Field(..., description="取消操作是否成功")


@router.post(
    "/stream",
    summary="发送消息并获取Agent流式响应",
    description="""
    核心Agent交互接口，用于发送用户指令并获取Agent的流式响应。

    ## 功能特点
    - **SSE流式响应**: 实时推送Agent思考过程、工具调用和执行结果
    - **多轮对话记忆**: 通过chat_thread_id维护对话上下文
    - **任务取消支持**: 可通过cancel接口主动终止正在执行的任务

    ## 消息类型
    Agent返回的SSE消息包含以下类型：
    - **think**: Agent思考过程，展示推理步骤
    - **tool_input**: 工具调用输入参数
    - **tool_output**: 工具执行结果
    - **summary**: 任务完成总结
    - **error**: 执行错误信息
    - **text**: 文本消息

    ## 典型使用流程
    1. 通过 /session/create 创建会话，获得 thread_id
    2. 携带 thread_id 调用此接口发送用户指令
    3. 前端接收SSE流并实时展示Agent执行过程
    4. 可随时调用 /agent/cancel 终止任务
    """,
    tags=["Agent交互"],
    responses={
        200: {
            "description": "SSE流式响应",
            "content": {
                "text/event-stream": {
                    "schema": {
                        "type": "string",
                        "example": "event: message\\ndata: {\"type\": \"think\", \"content\": \"思考中...\"}"
                    }
                }
            }
        },
        400: {
            "description": "请求参数错误 - message 或 thread_id 为空",
            "content": {
                "application/json": {
                    "example": {"code": 200, "message": "message 和 thread_id 是必需的"}
                }
            }
        },
        403: {
            "description": "会话无权限或已被清除",
            "content": {
                "application/json": {
                    "examples": {
                        "cleared": {"value": {"code": 403, "message": "会话已被清除，请重新开始会话"}},
                        "mismatch": {"value": {"code": 403, "message": "当前会话不匹配"}}
                    }
                }
            }
        },
        500: {
            "description": "服务端执行错误",
            "content": {
                "application/json": {
                    "example": {"code": 500, "message": "Agent执行异常: ..."}
                }
            }
        }
    }
)
async def agent_stream(request: Request, body: AgentStreamRequest):
    """
    发送消息给Agent并获取流式响应。

    ## 请求处理
    1. 验证 session 存在性和账户权限
    2. 初始化 SSE 连接事件（用于取消信号）
    3. 创建并初始化 MobileUseAgent
    4. 返回 StreamingResponse，实时推送执行过程

    ## SSE消息格式
    每条消息格式为 `event: message\\ndata: {...}\\n\\n`

    ## 响应内容示例
    ```json
    // 思考过程
    {"type": "think", "content": "用户想要打开微信..."}

    // 工具调用
    {"type": "tool_input", "tool": "launch_app", "input": {"package_name": "com.tencent.mm"}}

    // 工具结果
    {"type": "tool_output", "tool": "launch_app", "output": {"success": true}}

    // 完成总结
    {"type": "summary", "content": "已成功打开微信"}
    ```

    ## 注意事项
    - 前端必须处理SSE连接断开的情况
    - 任务执行时间可能较长，建议设置超时机制
    - Agent会自动进行多轮工具调用直到任务完成
    """
    try:
        account_id = request.state.account_id
        user_prompt = body.message
        thread_id = body.thread_id
        is_stream = body.is_stream

        logger.info(f"收到请求: {user_prompt}, {thread_id}")

        if not user_prompt or not thread_id:
            raise APIException(code=200, message="message 和 thread_id 是必需的")

        if not session_manager.has_thread(thread_id):
            raise APIException(code=403, message="会话已被清除，请重新开始会话")

        session = session_manager.get_thread_state(thread_id)
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
        logger.exception(f"API error: {api_error}")
        raise api_error

    except Exception as agent_error:
        logger.exception(f"Agent error: {agent_error}")
        raise agent_error


@router.post(
    "/cancel",
    response_model=CancelAgentResponse,
    summary="取消正在执行的Agent任务",
    description="""
    取消指定会话中正在执行的Agent任务。

    ## 功能说明
    - 不是"杀掉进程"，而是设置SSE断开标记
    - Agent检测到标记后会主动停止执行
    - 返回成功即表示取消信号已发出

    ## 使用场景
    - 用户主动取消耗时的操作
    - 前端页面切换，不再需要当前任务结果
    - 发现任务方向错误，需要重新开始

    ## 取消机制
    1. 调用此接口会设置 session.sse_connection Event
    2. Agent在下一轮工具调用前检查此Event
    3. 检测到取消信号后抛出 SSEException 终止执行
    """,
    tags=["Agent交互"],
    responses={
        200: {
            "description": "取消信号已发送",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "success": {"type": "boolean", "example": True}
                        }
                    }
                }
            }
        },
        400: {
            "description": "请求参数错误 - thread_id 未提供",
            "content": {
                "application/json": {
                    "example": {"code": 400, "message": "thread_id 是必需的"}
                }
            }
        },
        403: {
            "description": "会话无权限",
            "content": {
                "application/json": {
                    "example": {"code": 403, "message": "会话已被清除，请重新开始会话"}
                }
            }
        }
    }
)
async def cancel_agent(request: Request, body: CancelAgentRequest):
    """
    取消正在执行的Agent任务。

    ## 执行流程
    1. 验证 thread_id 存在性和账户权限
    2. 调用 stop_sse_connection 设置取消标记
    3. 返回成功响应（不等待Agent实际停止）

    ## 注意事项
    - 这是一个异步取消机制，不保证立即停止
    - Agent可能在当前工具调用完成后才响应取消
    - 多次调用 cancel 是安全的
    """
    account_id = request.state.account_id
    thread_id = body.thread_id

    if not thread_id:
        raise APIException(code=400, message="thread_id 是必需的")

    if session_manager.has_thread(thread_id):
        session = session_manager.get_thread_state(thread_id)
        if session.account_id != account_id:
            raise APIException(code=403, message="会话已被清除，请重新开始会话")

    session_manager.stop_sse_connection(thread_id)

    return {"success": True}
