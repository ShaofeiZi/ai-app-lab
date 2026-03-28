from mobile_use_service.models.result import ScreenshotResult
from mobile_use_service.service.mobile_use_service import MobileUseService


class FakeClient:
    def get_screenshot(self, session):
        return {
            "screenshot_url": "https://example.com/image.png",
            "width": 720,
            "height": 1520,
        }


def test_take_screenshot_returns_compatible_result():
    service = MobileUseService(client=FakeClient())
    result = service.take_screenshot(session=object())
    assert isinstance(result, ScreenshotResult)
    assert result.screenshot_url.endswith(".png")
    assert result.width == 720
