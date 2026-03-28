from mobile_use_service.models.result import ScreenshotResult, ActionResult
from mobile_use_service.models.session import MobileUseSession


def test_screenshot_result_keeps_dimensions():
    result = ScreenshotResult(
        screenshot_url="https://example.com/a.png",
        width=720,
        height=1520,
    )
    assert result.width == 720
    assert result.height == 1520


def test_session_model_keeps_required_context():
    session = MobileUseSession(
        pod_id="pod-1",
        product_id="product-1",
        authorization_token="token",
        tos_bucket="bucket",
        tos_region="cn-beijing",
        tos_endpoint="tos-cn-beijing.volces.com",
    )
    assert session.pod_id == "pod-1"
    assert session.tos_session_token == ""
