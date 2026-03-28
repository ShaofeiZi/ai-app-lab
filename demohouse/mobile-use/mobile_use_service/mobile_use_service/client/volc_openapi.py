from typing import Any

import requests

from mobile_use_service.client.auth import VolcLikeAuth
from mobile_use_service.client.compat import decode_authorization_token
from mobile_use_service.client.compat import normalize_run_sync_result
from mobile_use_service.models.session import MobileUseSession


class VolcMobileUseClient:
    def __init__(
        self,
        host: str,
        *,
        region: str = "cn-north-1",
        service: str = "ACEP",
        version: str = "2025-05-01",
        timeout_seconds: float = 30,
        session: requests.Session | None = None,
    ):
        self.host = host.rstrip("/")
        self.region = region
        self.service = service
        self.version = version
        self.timeout_seconds = timeout_seconds
        self.session = session or requests.Session()

    def build_common_headers(self) -> dict[str, str]:
        # 当前服务发送的都是 JSON 请求，因此这里固定设置 Content-Type。
        return {
            "Content-Type": "application/json;charset=UTF-8",
        }

    def build_runtime_payload(self, session: MobileUseSession) -> dict[str, Any]:
        # 这类公共字段会在多个接口中重复使用，抽出来后更便于复用和测试。
        return {
            "PodId": session.pod_id,
            "ProductId": session.product_id,
        }

    def _auth(self, session: MobileUseSession) -> VolcLikeAuth:
        # authorization_token 里封装了访问 OpenAPI 所需的临时凭证。
        # 这里先解包，再转成签名认证器对象。
        auth_info = decode_authorization_token(session.authorization_token)
        access_key = auth_info["access_key"]
        secret_key = auth_info["secret_key"]
        if not access_key or not secret_key:
            raise RuntimeError("session authorization token does not contain access credentials")
        return VolcLikeAuth(
            access_key,
            secret_key,
            self.region,
            self.service,
            session_token=auth_info["session_token"],
        )

    def request_json(
        self,
        action: str,
        payload: dict[str, Any],
        *,
        session: MobileUseSession,
    ) -> dict[str, Any]:
        # 所有 OpenAPI 请求都经过这一层：
        # 统一负责拼 URL、附加签名、检查 HTTP 状态码，以及解析业务错误码。
        response = self.session.post(
            f"{self.host}?Action={action}&Version={self.version}",
            json=payload,
            headers=self.build_common_headers(),
            auth=self._auth(session),
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        data = response.json()
        error = ((data.get("ResponseMetadata") or {}).get("Error")) or {}
        if error and error.get("CodeN", 0) != 0:
            raise RuntimeError(
                f"{action} failed: {error.get('Code') or error.get('CodeN')} {error.get('Message') or data}"
            )
        return data

    def run_sync_command(
        self,
        session: MobileUseSession,
        *,
        command: str,
        permission_type: str,
    ) -> str:
        # RunSyncCommand 更像一条“通用逃生通道”：
        # 只要设备允许执行 shell/root 命令，就能借它完成一些基础动作。
        payload = {
            "ProductId": session.product_id,
            "PodIdList": [session.pod_id],
            "Command": command,
            "PermissionType": permission_type,
        }
        data = self.request_json("RunSyncCommand", payload, session=session)
        return normalize_run_sync_result(data, expected_pod_id=session.pod_id)

    def launch_app(self, session: MobileUseSession, package_name: str) -> dict[str, Any]:
        # 高级动作优先走语义化 API，而不是手搓 shell 命令，这样可读性更好，也更稳定。
        payload = {
            "ProductId": session.product_id,
            "PodIdList": [session.pod_id],
            "PackageName": package_name,
        }
        return self.request_json("LaunchApp", payload, session=session)

    def close_app(self, session: MobileUseSession, package_name: str) -> dict[str, Any]:
        payload = {
            "ProductId": session.product_id,
            "PodIdList": [session.pod_id],
            "PackageName": package_name,
        }
        return self.request_json("CloseApp", payload, session=session)

    def list_apps(self, session: MobileUseSession) -> dict[str, Any]:
        payload = {
            "ProductId": session.product_id,
            "PodId": session.pod_id,
        }
        return self.request_json("GetPodAppList", payload, session=session)
