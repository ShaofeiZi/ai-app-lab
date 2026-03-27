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
from mobile_agent.config.settings import MOBILE_USE_MCP_NAME, get_settings
from mobile_agent.agent.utils.image import get_dimensions_from_url
from mobile_agent.agent.tools.mcp import MCPHub

"""
负责管理 agent 与手机 MCP 服务之间的连接，以及截图这类基础手机能力调用。

可以把这个类理解成“手机侧能力的入口适配器”：
- initialize 负责建立连接
- _take_screenshot 负责真正调用远端截图能力
- take_screenshot 负责对外暴露更稳定的截图入口，并同步更新屏幕尺寸
"""

logger = logging.getLogger(__name__)


class Mobile:
    def __init__(self, mcp_hub: MCPHub):
        # 初始时还不知道设备分辨率，所以先记为 None。
        # 后续拿到截图后，会把真实宽高写回这里，供动作坐标换算使用。
        self.phone_width: int | None = None
        self.phone_height: int | None = None
        self.mcp_hub = mcp_hub

    async def initialize(
        self,
        pod_id: str,
        product_id: str,
        tos_bucket: str,
        tos_region: str,
        tos_endpoint: str,
        auth_token: str,
    ):
        """
        初始化 mobile-use MCP 会话。

        这一步的本质是把设备信息、产品信息、对象存储信息和授权头整理成配置，
        交给 MCPHub 建立连接。后续所有手机操作都依赖这里建立的会话。
        """
        self.mcp_hub.add_mcp_json(
            MOBILE_USE_MCP_NAME,
            {
                "url": get_settings().mobile_use_mcp.url,
                "transport": "streamable_http",
                "headers": {
                    "Authorization": auth_token,
                    "X-ACEP-DeviceId": pod_id,
                    "X-ACEP-ProductId": product_id,
                    "X-ACEP-TosBucket": tos_bucket,
                    "X-ACEP-TosRegion": tos_region,
                    "X-ACEP-TosEndpoint": tos_endpoint,
                },
            },
        )
        await self.mcp_hub.session(MOBILE_USE_MCP_NAME)

    async def _take_screenshot(self) -> dict:
        """
        请求远端手机截图，并在失败时自动重试。

        这里返回的不只是图片地址，还尽量附带宽高，
        因为后续点击、滑动等动作需要基于当前屏幕尺寸做坐标换算。
        """
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                # 截图动作由 MCP 服务真正执行，本地只负责发起调用与解析返回值。
                result = await self.mcp_hub.call_tool(
                    mcp_server_name=MOBILE_USE_MCP_NAME,
                    name="take_screenshot",
                    arguments={},
                )

                text = result.content[0].text
                try:
                    # 优先走结构化 JSON 解析，因为这种结果最完整。
                    parsed_data = json.loads(text)
                    screenshot_url = parsed_data["result"]["screenshot_url"]
                    width = int(parsed_data["result"]["width"])
                    height = int(parsed_data["result"]["height"])
                except (json.JSONDecodeError, KeyError, TypeError):
                    # 如果远端没有返回标准 JSON，就退化为“先拿地址，再主动探测图片尺寸”。
                    logger.warning("主动解析截屏长宽")
                    screenshot_url = text
                    (
                        width,
                        height,
                    ) = await get_dimensions_from_url(screenshot_url)

                logger.info(
                    f"截图成功，重试次数: {retry_count}, 截图尺寸: {width}x{height}"
                )

                return {
                    "screenshot": screenshot_url,
                    "screenshot_dimensions": (width, height),
                }

            except Exception as e:
                # 截图失败不立刻放弃，而是做有限次重试，提升链路稳定性。
                retry_count += 1
                logger.error(f"截图异常，重试第 {retry_count} 次。错误: {e}")

                if retry_count >= max_retries:
                    raise ValueError(
                        f"截图失败，已重试 {max_retries} 次。最后错误: {e}"
                    )

                # 使用异步 sleep，避免等待时阻塞整个事件循环。
                await asyncio.sleep(1)

        # 理论上上面的 raise 已经会提前退出，这里保留最终兜底分支，语义更完整。
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
