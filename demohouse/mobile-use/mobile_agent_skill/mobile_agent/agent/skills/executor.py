from typing import Any


class SkillExecutor:
    # 这里维护“模型层技能名”到“新服务 tool 路由名”的映射关系。
    # 这样模型始终只面对统一的 skill 语义，而底层服务实现可以独立演进。
    TOOL_MAPPING = {
        "mobile:tap": "tap",
        "mobile:take_screenshot": "take_screenshot",
        "mobile:swipe": "swipe",
        "mobile:text_input": "text_input",
        "mobile:launch_app": "launch_app",
        "mobile:close_app": "close_app",
        "mobile:list_apps": "list_apps",
        "mobile:back": "back",
        "mobile:home": "home",
        "mobile:menu": "menu",
    }

    def __init__(self, service):
        # `service` 一般是 MobileUseServiceHTTPClient，
        # 它负责把技能执行真正发到 `mobile_use_service`。
        self.service = service

    async def execute(
        self,
        skill_name: str,
        params: dict[str, Any],
        context: dict[str, Any],
    ) -> Any:
        # 第一步：把 skill 名转换成新服务认识的 tool 名。
        tool_name = self.TOOL_MAPPING.get(skill_name)
        if not tool_name:
            raise ValueError(f"Unknown skill: {skill_name}")

        # 第二步：从上下文里拿到当前云手机会话信息。
        # 新服务执行动作时必须知道 pod_id、product_id、鉴权 token 等数据。
        session = context.get("session")
        if session is None:
            raise ValueError("session context is required")

        # 第三步：统一通过 HTTP 服务调用。
        # 这样 agent 本身不需要关心 OpenAPI 细节，只负责“决定做什么”。
        return await self.service.call_tool(tool_name, session=session, args=params or {})
