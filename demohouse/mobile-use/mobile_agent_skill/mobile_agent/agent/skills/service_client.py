import asyncio
from typing import Any

import httpx

from mobile_agent.config.settings import get_settings


class MobileUseServiceHTTPClient:
    """
    新版技能链路访问 `mobile_use_service` 的 HTTP 客户端。

    这个类的职责很单纯：
    - 负责把 agent 内部的调用请求转换成 HTTP POST
    - 统一处理 base_url、超时和连接复用
    - 屏蔽前后端之间的协议细节，让上层只关心“调用哪个 tool”
    """

    def __init__(
        self,
        *,
        base_url: str,
        timeout_seconds: float = 30,
        client: httpx.AsyncClient | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self._client = client
        self._owns_client = client is None

    async def aclose(self) -> None:
        # 只有“自己创建的 client”才在这里负责关闭。
        # 如果外部把 client 注入进来，就说明连接生命周期由外层管理。
        if self._client is not None and self._owns_client:
            await self._client.aclose()

    async def call_tool(
        self,
        tool_name: str,
        *,
        session: dict[str, Any],
        args: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        # 每一次调用都会把“当前会话信息 + 工具参数”一起发给新服务。
        # 这样新服务可以做到完全无状态，不必自己维护会话缓存。
        client = self._ensure_client()
        payload: dict[str, Any] = {"session": session}
        if args is not None:
            payload["args"] = args

        response = await client.post(
            f"{self.base_url}/mobile-use/api/v1/tools/{tool_name}",
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        # 某些代理层会把真实业务结果包在 `result` 字段里，
        # 这里顺手做一层兼容展开，减少上层判断分支。
        if isinstance(data, dict) and "result" in data:
            return data["result"]
        return data

    async def take_screenshot(self, session: dict[str, Any]) -> dict[str, Any]:
        # 截图是 Agent 每一轮推理都高频依赖的能力，所以单独提供一个语义更直接的方法。
        result = await self.call_tool("take_screenshot", session=session)
        return {"result": result}

    def _ensure_client(self) -> httpx.AsyncClient:
        # 懒加载 AsyncClient 的好处是：
        # 如果当前进程只是被导入但还没真的发请求，就不会提前创建连接池。
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout_seconds)
        return self._client


def build_default_service_client() -> MobileUseServiceHTTPClient:
    # 默认客户端从统一配置里取服务地址和超时，便于不同环境切换。
    settings = get_settings()
    return MobileUseServiceHTTPClient(
        base_url=settings.mobile_use_service.url,
        timeout_seconds=settings.mobile_use_service.timeout_seconds,
    )
