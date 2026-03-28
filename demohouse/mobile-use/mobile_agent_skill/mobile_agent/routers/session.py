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
"""

from fastapi import APIRouter, Request
import logging
import uuid
from mobile_agent.config.settings import get_settings
from mobile_agent.middleware.middleware import APIException
from mobile_agent.service.session.manager import session_manager
from pydantic import BaseModel, Field
from typing import Optional

logger = logging.getLogger(__name__)
# 创建路由
router = APIRouter(
    prefix="/mobile-use/api/v1/session",
    tags=["session"],
)


class CreateSessionRequest(BaseModel):
    thread_id: Optional[str] = Field(None, description="线程ID，如果不提供则自动生成")
    product_id: str = Field(..., description="产品ID")
    pod_id: str = Field(..., description="Pod ID")


@router.post("/create")
async def create_session(request: Request, body: CreateSessionRequest):
    # create_session 的任务是：
    # 1. 校验并拿到 pod 的最新可用信息；
    # 2. 如果已有 thread，就刷新它；
    # 3. 如果没有，就创建一个全新的会话。
    account_id = request.state.account_id
    thread_id = body.thread_id
    product_id = body.product_id
    pod_id = body.pod_id

    if thread_id and session_manager.has_thread(thread_id):
        # 老会话继续使用时，不重新生成 thread_id，
        # 只刷新 pod 与鉴权信息，保证浏览器刷新后还能接着用原会话。
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
        # 新会话会生成新的 thread_id。
        # 注意：thread_id 是“前端会话 ID”，而 chat_thread_id 是“Agent 对话上下文 ID”，两者用途不同。
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
    # 返回给前端的是“渲染云手机 + 继续发任务”所需的最小完整信息集合。
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
    thread_id: str = Field(..., description="需要重置的线程ID")


@router.post("/reset")
async def reset_session(request: Request, body: ResetSessionRequest):
    """
    重置会话，保持同一个 pod 但切换到新的 chat_thread_id
    """
    account_id = request.state.account_id
    thread_id = body.thread_id

    if not thread_id:
        raise APIException(code=400, message="参数不正确")

    # 检查旧会话是否存在
    if not session_manager.has_thread(thread_id):
        raise APIException(code=403, message="会话已被清除，请重新开始会话")

    old_session = session_manager.get_thread_state(thread_id)
    if old_session.account_id != account_id:
        raise APIException(code=403, message="当前会话不匹配")

    # 这里不会换掉最外层 thread_id，
    # 只会重置内部 chat_thread_id，相当于“同一台云手机上开启一段新的对话记忆”。
    new_chat_thread_id = str(uuid.uuid4())

    logger.info(f"重置会话: {old_session.chat_thread_id} -> {new_chat_thread_id}")

    # session 修改 chat_thread_id
    session_manager.reset_thread(thread_id, new_chat_thread_id)

    # 前端收到后会清空旧消息列表，并从新的对话上下文重新开始。
    return {"thread_id": thread_id, "chat_thread_id": new_chat_thread_id}
