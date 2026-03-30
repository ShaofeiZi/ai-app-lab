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
会话相关路由

提供云手机会话的创建、重置和管理功能。
会话用于维护用户与云手机之间的状态关联，包括鉴权信息和设备信息。
"""

from fastapi import APIRouter, Request, status
import logging
import uuid
from mobile_agent.config.settings import get_settings
from mobile_agent.middleware.middleware import APIException
from mobile_agent.service.session.manager import session_manager
from pydantic import BaseModel, Field
from typing import Optional

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/mobile-use/api/v1/session",
    tags=["会话管理"],
)


class CreateSessionRequest(BaseModel):
    """
    创建会话请求模型

    用于创建新的云手机会话或刷新已有会话的连接状态。
    """
    thread_id: Optional[str] = Field(
        None,
        description="线程ID，用于标识前端会话。不提供则自动生成新的UUID",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    product_id: str = Field(
        ...,
        description="产品ID，从云手机控制台获取",
        examples=["prod_abc123"]
    )
    pod_id: str = Field(
        ...,
        description="Pod ID，云手机设备标识",
        examples=["pod_xyz789"]
    )


class PodInfo(BaseModel):
    """
    云手机Pod信息

    包含云手机会话所需的所有连接和认证信息。
    """
    token: dict = Field(
        ...,
        description="STS临时凭证，包含AccessKey、SecretKey和SessionToken"
    )
    size: dict = Field(
        ...,
        description="云手机屏幕分辨率，{width: int, height: int}"
    )
    product_id: str = Field(..., description="产品ID")
    pod_id: str = Field(..., description="Pod ID")
    expired_time: int = Field(..., description="Pod剩余可用时间（秒）")
    account_id: str = Field(..., description="云手机账号ID")


class CreateSessionResponse(BaseModel):
    """
    创建会话响应模型
    """
    thread_id: str = Field(..., description="线程ID，前端会话标识")
    chat_thread_id: str = Field(..., description="Agent对话上下文ID，用于维护多轮对话历史")
    pod: PodInfo = Field(..., description="云手机Pod完整信息")


@router.post(
    "/create",
    response_model=CreateSessionResponse,
    summary="创建或刷新云手机会话",
    description="""
    创建新的云手机会话或刷新已有会话的连接状态。

    ## 功能说明
    - **新会话创建**: 当不提供 thread_id 或 thread_id 不存在时，创建全新会话
    - **会话刷新**: 当提供已存在的 thread_id 时，刷新Pod鉴权信息和设备状态

    ## 会话类型区分
    - **thread_id**: 前端会话ID，标识用户与云手机的连接会话
    - **chat_thread_id**: Agent对话上下文ID，用于维护Agent内部的多轮对话记忆

    ## 典型使用流程
    1. 前端首次访问时调用此接口创建会话
    2. 获取thread_id和pod信息后，开始与Agent交互
    3. 前端刷新或断线重连时，携带原thread_id调用此接口刷新会话
    """,
    tags=["会话管理"],
    responses={
        200: {
            "description": "会话创建或刷新成功",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "thread_id": {"type": "string", "description": "线程ID"},
                            "chat_thread_id": {"type": "string", "description": "对话上下文ID"},
                            "pod": {
                                "type": "object",
                                "properties": {
                                    "token": {
                                        "type": "object",
                                        "properties": {
                                            "AccessKeyID": {"type": "string"},
                                            "SecretAccessKey": {"type": "string"},
                                            "SessionToken": {"type": "string"},
                                            "CurrentTime": {"type": "string"},
                                            "ExpiredTime": {"type": "string"}
                                        }
                                    },
                                    "size": {
                                        "type": "object",
                                        "properties": {
                                            "width": {"type": "integer"},
                                            "height": {"type": "integer"}
                                        }
                                    },
                                    "product_id": {"type": "string"},
                                    "pod_id": {"type": "string"},
                                    "expired_time": {"type": "integer"},
                                    "account_id": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            }
        },
        400: {"description": "请求参数错误 - product_id 或 pod_id 格式无效"},
        401: {"description": "认证失败 - 用户未登录或Token无效"},
        403: {"description": "会话不匹配 - thread_id 不属于当前账户"},
        404: {"description": "Pod不存在 - 指定的pod_id无效或已释放"},
        500: {"description": "服务端错误 - 会话创建失败"}
    }
)
async def create_session(request: Request, body: CreateSessionRequest):
    """
    创建或刷新云手机会话。

    ## 请求处理逻辑
    1. 校验请求参数，提取 account_id（来自中间件）
    2. 调用 pod_manager 获取 Pod 最新状态和鉴权信息
    3. 根据 thread_id 存在性决定创建新会话或刷新已有会话
    4. 返回完整会话信息供前端渲染云手机

    ## 注意事项
    - thread_id 是“前端会话ID”，chat_thread_id 是“Agent对话上下文ID”
    - 刷新会话不会改变 thread_id，但会更新 Pod 鉴权信息
    - 会话超时时间默认2小时，Pod过期时间由云手机服务决定
    """
    account_id = request.state.account_id
    thread_id = body.thread_id
    product_id = body.product_id
    pod_id = body.pod_id

    if thread_id and session_manager.has_thread(thread_id):
        response_json = await session_manager.validate(
            device_id=pod_id,
            product_id=product_id,
        )

        logger.info(f"更新会话状态: {thread_id} {response_json}")
        session = session_manager.update_thread_state(
            thread_id,
            device_info=response_json["device_info"],
            auth_info=response_json["auth_info"],
        )
    else:
        thread_id = str(uuid.uuid4())
        response_json = await session_manager.validate(
            device_id=pod_id,
            product_id=product_id,
        )
        logger.info(f"创建会话成功: {thread_id} {response_json}")
        session = session_manager.create_thread(
            account_id,
            thread_id,
            device_info=response_json["device_info"],
            auth_info=response_json["auth_info"],
        )
    return {
        "thread_id": thread_id,
        "chat_thread_id": session.chat_thread_id,
        "pod": {
            "token": session.sts_token.model_dump(),
            "size": session.pod_size.model_dump(),
            "product_id": session.product_id,
            "pod_id": session.pod_id,
            "expired_time": session.pod_session_expired_time,
            "account_id": session.pod_account_id,
        },
    }


class ResetSessionRequest(BaseModel):
    """
    重置会话请求模型

    用于在保持同一台云手机的情况下，重置Agent对话上下文。
    """
    thread_id: str = Field(
        ...,
        description="需要重置的线程ID",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )


class ResetSessionResponse(BaseModel):
    """
    重置会话响应模型
    """
    thread_id: str = Field(..., description="线程ID（保持不变）")
    chat_thread_id: str = Field(..., description="新的Agent对话上下文ID")


@router.post(
    "/reset",
    response_model=ResetSessionResponse,
    summary="重置Agent对话上下文",
    description="""
    在不更换云手机的情况下，重置Agent的对话上下文。

    ## 功能说明
    - 保持 thread_id 不变（云手机会话连续）
    - 生成新的 chat_thread_id（对话记忆重置）
    - 停止当前正在执行的任务

    ## 使用场景
    - 用户想要开始新的话题，但不想断开云手机连接
    - 对话轮次达到上限，需要开始新的对话链
    - 用户主动要求"重新开始"

    ## 与创建会话的区别
    | 操作 | thread_id | chat_thread_id | Pod资源 |
    |------|-----------|-----------------|---------|
    | 创建 | 新生成    | 新生成          | 新分配  |
    | 重置 | 保持不变  | 新生成          | 保持不变 |
    """,
    tags=["会话管理"],
    responses={
        200: {
            "description": "会话重置成功",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "thread_id": {"type": "string", "description": "线程ID（不变）"},
                            "chat_thread_id": {"type": "string", "description": "新的对话上下文ID"}
                        }
                    }
                }
            }
        },
        400: {"description": "请求参数错误 - thread_id 未提供"},
        403: {
            "description": "会话无权限或已被清除",
            "content": {
                "application/json": {
                    "examples": {
                        "not_found": {"value": {"code": 403, "message": "会话已被清除，请重新开始会话"}},
                        "mismatch": {"value": {"code": 403, "message": "当前会话不匹配"}}
                    }
                }
            }
        },
        500: {"description": "服务端错误 - 会话重置失败"}
    }
)
async def reset_session(request: Request, body: ResetSessionRequest):
    """
    重置Agent对话上下文。

    ## 执行流程
    1. 校验 thread_id 是否存在
    2. 验证请求账户与会话账户是否匹配
    3. 停止当前 SSE 连接（让正在执行的任务尽快停止）
    4. 生成新的 chat_thread_id 并更新会话状态
    5. 返回新的 chat_thread_id，前端据此清空对话历史

    ## 注意事项
    - 重置的是"对话记忆"，不是"云手机连接"
    - Pod资源不会释放，继续计费
    - 如果有任务正在执行，会立即触发取消
    """
    account_id = request.state.account_id
    thread_id = body.thread_id

    if not thread_id:
        raise APIException(code=400, message="参数不正确")

    if not session_manager.has_thread(thread_id):
        raise APIException(code=403, message="会话已被清除，请重新开始会话")

    old_session = session_manager.get_thread_state(thread_id)
    if old_session.account_id != account_id:
        raise APIException(code=403, message="当前会话不匹配")

    new_chat_thread_id = str(uuid.uuid4())

    logger.info(f"重置会话: {old_session.chat_thread_id} -> {new_chat_thread_id}")

    session_manager.reset_thread(thread_id, new_chat_thread_id)

    return {"thread_id": thread_id, "chat_thread_id": new_chat_thread_id}
