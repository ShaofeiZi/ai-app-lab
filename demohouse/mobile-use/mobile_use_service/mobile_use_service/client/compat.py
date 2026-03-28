import base64
import json
from typing import Any


def normalize_run_sync_result(raw: dict[str, Any], *, expected_pod_id: str) -> str:
    result = raw.get("Result") or {}
    status_list = result.get("Status") or []
    if not status_list:
        raise RuntimeError("RunSyncCommand failed: empty status list")

    for status in status_list:
        pod_id = status.get("PodID") or status.get("PodId")
        if pod_id and pod_id != expected_pod_id:
            continue
        success = status.get("Success")
        detail = status.get("Detail") or ""
        if success:
            return detail
        raise RuntimeError(f"RunSyncCommand failed: {detail}")

    raise RuntimeError(f"RunSyncCommand failed: status for pod {expected_pod_id} not found")


def build_tos_config_base64(
    *,
    access_key: str,
    secret_key: str,
    session_token: str,
    bucket: str,
    region: str,
    endpoint: str,
) -> str:
    payload = {
        "AccessKey": access_key,
        "SecretKey": secret_key,
        "SessionToken": session_token,
        "Bucket": bucket,
        "Region": region,
        "Endpoint": endpoint,
    }
    return base64.b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")


def decode_authorization_token(token: str) -> dict[str, Any]:
    if not token:
        raise RuntimeError("authorization_token is required")
    raw = base64.b64decode(token)
    parsed = json.loads(raw.decode("utf-8"))
    return {
        "access_key": parsed.get("AccessKeyId") or parsed.get("AccessKeyID") or "",
        "secret_key": parsed.get("SecretAccessKey") or "",
        "session_token": parsed.get("SessionToken") or "",
        "current_time": parsed.get("CurrentTime") or "",
        "expired_time": parsed.get("ExpiredTime") or "",
    }


def parse_screenshot_output(output: str) -> dict[str, Any]:
    if output.startswith("ScreenshotURL: "):
        return {
            "screenshot_url": output.removeprefix("ScreenshotURL: ").strip(),
            "width": 0,
            "height": 0,
        }

    parsed = json.loads(output)
    screenshot_url = parsed.get("screenshot_url")
    resolution = parsed.get("resolution") or ""
    width, height = 0, 0
    if "x" in resolution:
        raw_width, raw_height = resolution.split("x", 1)
        width = int(raw_width)
        height = int(raw_height)
    if not screenshot_url:
        raise RuntimeError("screenshot_url missing from screenshot response")
    return {
        "screenshot_url": screenshot_url,
        "width": width,
        "height": height,
    }
