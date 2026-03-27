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
响应中间件 - 统一处理API返回格式
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Any, Union
import json
import logging
from mobile_agent.exception.api import APIException

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """账户鉴权中间件"""

    async def dispatch(self, request: Request, call_next):
        # 这里读取的是外层网关或调用方传进来的账户标识。
        # 后续所有业务路由都依赖它做“这个会话属于谁”的校验。
        account_id = request.headers.get("X-Account-Id")
        faas_instance_name = request.headers.get("x-faas-instance-name")
        logger.info(f"账户ID: {account_id}，FaaS实例名称: {faas_instance_name}")

        # 检查是否提供了账户ID
        if not account_id:
            return JSONResponse(
                content=wrap_error_response(
                    code=401,
                    message="账户ID不存在，鉴权失败",
                ),
                status_code=401,
                media_type="application/json",
            )

        # request.state 可以理解成“本次请求专属的临时存储区”。
        # 这样后面的路由就不用一层层传 account_id 了。
        request.state.account_id = account_id

        # 继续处理请求
        response = await call_next(request)
        return response


class ResponseMiddleware(BaseHTTPMiddleware):
    """
    响应中间件，统一处理成功和失败的返回格式

    成功格式：
    {
        "result": {...}
    }

    失败格式：
    {
        "error": {
            "code": xxx,
            "message": "错误信息"
        }
    }
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            # 先让真正的路由逻辑运行，拿到它原始返回的 Response。
            response = await call_next(request)

            # SSE 事件流不是普通 JSON，不能再包一层 result/error，
            # 否则前端就无法按事件流协议解析了。
            if not isinstance(response, JSONResponse):
                return response

            # 这里把 JSONResponse 的 body 取出来，判断它是不是已经包装好的格式。
            response_body = json.loads(response.body.decode())

            # 某些路由或异常处理逻辑本身已经返回了标准结构，
            # 再包装一次就会变成 result.result 这种难看的嵌套。
            if isinstance(response_body, dict) and (
                "result" in response_body or "error" in response_body
            ):
                return response

            # 普通成功响应统一包成 {"result": ..., "error": {"code": 0, ...}}，
            # 这样前端不需要分别处理很多种返回格式。
            return JSONResponse(
                content=wrap_response_data(response_body),
                status_code=response.status_code,
                headers=dict(response.headers),
            )

        except APIException as api_error:
            # APIException 代表“业务上可预期的失败”，
            # 例如参数不对、会话不存在，而不是程序崩溃。
            logger.warning(f"业务报错: {api_error}")

            return JSONResponse(
                content=wrap_error_response(api_error.code, api_error.message),
                status_code=200,
                media_type="application/json",
            )

        except Exception as e:
            # 剩下的异常都按未知错误处理，并保留日志方便排查。
            logger.exception(f"请求处理异常: {e}")

            # 包装错误响应
            return JSONResponse(
                content=wrap_error_response(500, f"服务器内部错误: {str(e)}"),
                status_code=500,
                media_type="application/json",
            )


def wrap_response_data(data: Any) -> Dict[str, Any]:
    """
    包装正常返回的数据

    Args:
        data: 要返回的数据

    Returns:
        Dict: 格式化后的响应数据
    """
    return {"result": data, "error": {"code": 0, "message": "success"}}


def wrap_error_response(
    code: int, message: str
) -> Dict[str, Dict[str, Union[int, str]]]:
    """
    包装错误返回的数据

    Args:
        code: 错误码
        message: 错误信息

    Returns:
        Dict: 格式化后的错误响应数据
    """
    return {"error": {"code": code, "message": message}}
