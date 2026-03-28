import base64
from typing import Any

from mobile_use_service.client.commands import (
    ANDROID_KEY_EVENT_MAP,
    CLEAR_INPUT_COMMAND,
    INPUT_TEXT_COMMAND,
    SCREENSHOT_COMMAND,
    SCREENSHOT_COMMAND_TYPE,
    SCREEN_SWIPE_COMMAND,
    SCREEN_SWIPE_TIME_MS,
    SCREEN_TAP_COMMAND,
    SELECT_INPUT_METHOD_COMMAND,
    SHELL_COMMAND_TYPE,
)
from mobile_use_service.client.compat import (
    build_tos_config_base64,
    decode_authorization_token,
    parse_screenshot_output,
)
from mobile_use_service.client.volc_openapi import VolcMobileUseClient
from mobile_use_service.config.settings import get_settings
from mobile_use_service.models.result import ActionResult, ScreenshotResult
from mobile_use_service.models.session import MobileUseSession


class MobileUseService:
    """HTTP service used by the skill-based agent runtime."""

    def __init__(self, client=None):
        # service 层的定位是“把一个动作请求翻译成具体执行方式”。
        # 它不关心模型怎么思考，只关心：
        # - 当前会话是谁
        # - 要执行哪个动作
        # - 走 OpenAPI 还是兼容命令
        settings = get_settings()
        self.client = client or VolcMobileUseClient(
            host=settings.openapi.host,
            region=settings.openapi.region,
            service=settings.openapi.service,
            version=settings.openapi.version,
            timeout_seconds=settings.openapi.timeout_seconds,
        )
        self.settings = settings

    def take_screenshot(self, session: MobileUseSession) -> ScreenshotResult:
        # 截图是最核心的只读能力。
        # Agent 每走一轮都会先截图，再决定下一步动作。
        if self.client and hasattr(self.client, "get_screenshot"):
            data = self.client.get_screenshot(session)
            return ScreenshotResult(**data)

        try:
            auth_info = decode_authorization_token(session.authorization_token)
            tos_config = build_tos_config_base64(
                access_key=auth_info["access_key"],
                secret_key=auth_info["secret_key"],
                session_token=auth_info["session_token"],
                bucket=session.tos_bucket,
                region=session.tos_region,
                endpoint=session.tos_endpoint,
            )
            output = self.client.run_sync_command(
                session,
                command=SCREENSHOT_COMMAND % tos_config,
                permission_type=SCREENSHOT_COMMAND_TYPE,
            )
            data = parse_screenshot_output(output)
            return ScreenshotResult(**data)
        except Exception:
            # mock fallback 主要服务本地联调或接口不可用时的兜底场景。
            # 真正生产环境如果不希望“看起来成功但其实没真的执行”，就应关闭它。
            if not self.settings.allow_mock_fallback:
                raise
            return ScreenshotResult(
                screenshot_url=f"https://example.com/screenshots/{getattr(session, 'pod_id', 'unknown')}.png",
                width=720,
                height=1520,
            )

    def _action_result(
        self,
        action_name: str,
        payload: dict[str, Any] | None = None,
        *,
        success: bool = True,
    ) -> ActionResult:
        # 统一构造 ActionResult，保证所有动作接口的返回结构一致。
        return ActionResult(action_name=action_name, payload=payload or {}, success=success)

    def _run_action(self, session, action_name, payload=None):
        # 如果底层 client 已经提供“高级动作接口”，优先走这里。
        if self.client and hasattr(self.client, "run_action"):
            res = self.client.run_action(session, action_name, payload)
            return ActionResult(**res)
        return self._action_result(action_name, payload)

    def _run_or_fallback(
        self,
        func,
        *,
        action_name: str,
        payload: dict[str, Any] | None = None,
    ) -> ActionResult:
        # 兼容分支的思路是：
        # 先执行真正动作；
        # 如果失败且允许 mock，就明确告诉上游“这次是真失败，只是没有抛异常中断服务”，
        # 避免 agent 把它误当成手机状态已经变化。
        try:
            func()
        except Exception as exc:
            if not self.settings.allow_mock_fallback:
                raise
            fallback_payload = dict(payload or {})
            fallback_payload.update(
                {
                    "fallback_used": True,
                    "error": str(exc),
                }
            )
            return self._action_result(
                action_name,
                fallback_payload,
                success=False,
            )
        return self._action_result(action_name, payload)

    def tap(self, session: MobileUseSession, x: int, y: int) -> ActionResult:
        # 点击动作只需要最终点坐标。
        # 坐标换算这件事已经在 agent 侧的 action parser 做完了。
        if hasattr(self.client, "run_action"):
            return self._run_action(session, "tap", {"x": x, "y": y})
        return self._run_or_fallback(
            lambda: self.client.run_sync_command(
                session,
                command=SCREEN_TAP_COMMAND % (x, y),
                permission_type=SHELL_COMMAND_TYPE,
            ),
            action_name="tap",
            payload={"x": x, "y": y},
        )

    def swipe(
        self,
        session: MobileUseSession,
        from_x: int,
        from_y: int,
        to_x: int,
        to_y: int,
    ) -> ActionResult:
        payload = {
            "from_x": from_x,
            "from_y": from_y,
            "to_x": to_x,
            "to_y": to_y,
        }
        # swipe 除了坐标之外，还隐含一个“滑动时长”，这里在命令常量里统一维护。
        if hasattr(self.client, "run_action"):
            return self._run_action(session, "swipe", payload)
        return self._run_or_fallback(
            lambda: self.client.run_sync_command(
                session,
                command=SCREEN_SWIPE_COMMAND
                % (from_x, from_y, to_x, to_y, SCREEN_SWIPE_TIME_MS),
                permission_type=SHELL_COMMAND_TYPE,
            ),
            action_name="swipe",
            payload=payload,
        )

    def text_input(self, session: MobileUseSession, text: str) -> ActionResult:
        if hasattr(self.client, "run_action"):
            return self._run_action(session, "text_input", {"text": text})

        def _runner() -> None:
            # 输入文字前先切输入法、清空旧输入，再广播新文本。
            # 这里之所以做成三步，是因为很多安卓云机环境不能直接稳定用单条命令输中文。
            self.client.run_sync_command(
                session,
                command=SELECT_INPUT_METHOD_COMMAND,
                permission_type=SHELL_COMMAND_TYPE,
            )
            self.client.run_sync_command(
                session,
                command=CLEAR_INPUT_COMMAND,
                permission_type=SHELL_COMMAND_TYPE,
            )
            encoded_text = base64.b64encode(text.encode("utf-8")).decode("utf-8")
            self.client.run_sync_command(
                session,
                command=INPUT_TEXT_COMMAND % encoded_text,
                permission_type=SHELL_COMMAND_TYPE,
            )

        return self._run_or_fallback(
            _runner,
            action_name="text_input",
            payload={"text": text},
        )

    def launch_app(self, session: MobileUseSession, package_name: str) -> ActionResult:
        if hasattr(self.client, "run_action"):
            return self._run_action(session, "launch_app", {"package_name": package_name})
        return self._run_or_fallback(
            lambda: self.client.launch_app(session, package_name),
            action_name="launch_app",
            payload={"package_name": package_name},
        )

    def close_app(self, session: MobileUseSession, package_name: str) -> ActionResult:
        if hasattr(self.client, "run_action"):
            return self._run_action(session, "close_app", {"package_name": package_name})
        return self._run_or_fallback(
            lambda: self.client.close_app(session, package_name),
            action_name="close_app",
            payload={"package_name": package_name},
        )

    def list_apps(self, session: MobileUseSession) -> ActionResult:
        apps: list[dict[str, Any]] = []
        if hasattr(self.client, "run_action"):
            return self._run_action(session, "list_apps", {"apps": apps})
        if hasattr(self.client, "list_apps"):
            response = self.client.list_apps(session)
            row_items = ((response.get("Result") or {}).get("Row")) or []
            for item in row_items:
                # 这里把上游接口返回的字段重新整理成更稳定、更前端友好的结构。
                apps.append(
                    {
                        "app_id": item.get("AppID") or item.get("AppId"),
                        "app_name": item.get("AppName"),
                        "package_name": item.get("PackageName"),
                        "install_status": item.get("InstallStatus"),
                    }
                )
        return self._action_result("list_apps", {"apps": apps})

    def back(self, session: MobileUseSession) -> ActionResult:
        return self._key_event(session, "back")

    def home(self, session: MobileUseSession) -> ActionResult:
        return self._key_event(session, "home")

    def menu(self, session: MobileUseSession) -> ActionResult:
        return self._key_event(session, "menu")

    def terminate(self, session: MobileUseSession, reason: str) -> ActionResult:
        # terminate 当前是一个语义化结果，不真的去“销毁云机”。
        # 它更像告诉上游：这条任务链应该到此为止了。
        return self._action_result("terminate", {"reason": reason})

    def _key_event(self, session: MobileUseSession, key: str) -> ActionResult:
        key_code = ANDROID_KEY_EVENT_MAP[key]
        if hasattr(self.client, "run_action"):
            return self._run_action(session, key)
        return self._run_or_fallback(
            lambda: self.client.run_sync_command(
                session,
                command=f"input keyevent {key_code}",
                permission_type=SHELL_COMMAND_TYPE,
            ),
            action_name=key,
        )
