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
import json
import logging

"""
负责管理 agent 与手机 MCP 服务之间的连接，以及截图这类基础手机能力调用。

可以把这个类理解成“手机侧能力的入口适配器”：
- initialize 负责建立连接
- _take_screenshot 负责真正调用远端截图能力
- take_screenshot 负责对外暴露更稳定的截图入口，并同步更新屏幕尺寸
"""

logger = logging.getLogger(__name__)


class Mobile:
    def __init__(self, service_client=None, mcp_hub=None):
        self.phone_width: int | None = None
        self.phone_height: int | None = None
        self.mcp_hub = mcp_hub
        self.service_client = service_client
        self.session_payload: dict | None = None

    async def initialize(
        self,
        pod_id: str,
        product_id: str,
        tos_bucket: str,
        tos_region: str,
        tos_endpoint: str,
        auth_token: str,
    ):
        self.session_payload = {
            "pod_id": pod_id,
            "product_id": product_id,
            "authorization_token": auth_token,
            "tos_bucket": tos_bucket,
            "tos_region": tos_region,
            "tos_endpoint": tos_endpoint,
        }

    async def _take_screenshot(self) -> dict:
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                if self.service_client:
                    if not self.session_payload:
                        raise ValueError("mobile client is not initialized")
                    result = await self.service_client.take_screenshot(self.session_payload)
                    return {
                        "screenshot": result["result"]["screenshot_url"],
                        "screenshot_dimensions": (int(result["result"]["width"]), int(result["result"]["height"])),
                    }
                else:
                    raise ValueError("No service client available")
            except Exception as e:
                retry_count += 1
                logger.error(f"截图异常，重试第 {retry_count} 次。错误: {e}")
                if retry_count >= max_retries:
                    raise ValueError(f"截图失败，已重试 {max_retries} 次。最后错误: {e}")
                await asyncio.sleep(1)
        raise ValueError(f"截图失败，已重试 {max_retries} 次")

    def change_phone_dimensions(self, width: int, height: int):
        # 0 通常意味着无效尺寸，所以这里避免用坏值覆盖掉已有宽高。
        if width != 0:
            self.phone_width = width
        if height != 0:
            self.phone_height = height

    async def take_screenshot(self) -> tuple[int, int]:
        screenshot_state = await self._take_screenshot()
        # 每次截图后都同步更新尺寸，解决横竖屏切换导致的坐标基准变化问题。
        self.change_phone_dimensions(
            screenshot_state.get("screenshot_dimensions")[0],
            screenshot_state.get("screenshot_dimensions")[1],
        )
        return screenshot_state

    def get_session_payload(self) -> dict:
        if not self.session_payload:
            raise ValueError("mobile client is not initialized")
        return self.session_payload
