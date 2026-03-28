import pytest

from mobile_agent.agent.mobile.client import Mobile


class FakeServiceClient:
    async def take_screenshot(self, session):
        assert session["pod_id"] == "pod-1"
        return {
            "result": {
                "screenshot_url": "https://example.com/shot.png",
                "width": 720,
                "height": 1520,
            }
        }


@pytest.mark.asyncio
async def test_take_screenshot_updates_dimensions():
    mobile = Mobile(service_client=FakeServiceClient())
    await mobile.initialize(
        pod_id="pod-1",
        product_id="product-1",
        tos_bucket="bucket",
        tos_region="cn-beijing",
        tos_endpoint="https://tos-cn-beijing.volces.com",
        auth_token="token",
    )
    result = await mobile.take_screenshot()
    assert result["screenshot_dimensions"] == (720, 1520)
