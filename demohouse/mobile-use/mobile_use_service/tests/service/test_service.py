import os

from mobile_use_service.models.result import ScreenshotResult
from mobile_use_service.config.settings import get_settings
from mobile_use_service.models.session import MobileUseSession
from mobile_use_service.service.mobile_use_service import MobileUseService


class FakeScreenshotClient:
    def get_screenshot(self, session):
        return {
            "screenshot_url": "https://example.com/screenshot.png",
            "width": 720,
            "height": 1520,
        }


class FakeCommandClient:
    def run_sync_command(self, session, command, permission_type):
        return "ok"


def test_take_screenshot_returns_compatible_result():
    os.environ["MOBILE_USE_ALLOW_MOCK_FALLBACK"] = "true"
    get_settings.cache_clear()
    service = MobileUseService(client=FakeScreenshotClient())
    session = MobileUseSession(
        pod_id="pod-1",
        product_id="product-1",
        authorization_token="token",
        tos_bucket="bucket",
        tos_region="cn-beijing",
        tos_endpoint="tos-cn-beijing.volces.com",
    )

    result = service.take_screenshot(session)

    assert isinstance(result, ScreenshotResult)
    assert result.width == 720
    assert result.height == 1520


def test_tap_returns_successful_action_result():
    get_settings.cache_clear()
    service = MobileUseService(client=FakeCommandClient())
    session = MobileUseSession(
        pod_id="pod-1",
        product_id="product-1",
        authorization_token="token",
        tos_bucket="bucket",
        tos_region="cn-beijing",
        tos_endpoint="tos-cn-beijing.volces.com",
    )

    result = service.tap(session, x=10, y=20)

    assert result.success is True
    assert result.action_name == "tap"
    assert result.payload == {"x": 10, "y": 20}
