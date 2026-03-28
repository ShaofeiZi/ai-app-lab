from fastapi.testclient import TestClient

from app import app
from mobile_use_service.routers import mobile_use as mobile_use_router


class FakeRouterService:
    def tap(self, session, x, y):
        return type(
            "Result",
            (),
            {"model_dump": lambda self: {"action_name": "tap", "success": True, "payload": {"x": x, "y": y}}},
        )()

    def take_screenshot(self, session):
        return type(
            "Result",
            (),
            {
                "model_dump": lambda self: {
                    "screenshot_url": "https://example.com/screenshot.png",
                    "width": 720,
                    "height": 1520,
                }
            },
        )()

    def swipe(self, session, from_x, from_y, to_x, to_y):
        return type(
            "Result",
            (),
            {
                "model_dump": lambda self: {
                    "action_name": "swipe",
                    "success": True,
                    "payload": {
                        "from_x": from_x,
                        "from_y": from_y,
                        "to_x": to_x,
                        "to_y": to_y,
                    },
                }
            },
        )()


def test_health_route_returns_ok():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_tap_route_returns_wrapped_action_result(monkeypatch):
    monkeypatch.setattr(mobile_use_router, "service", FakeRouterService())
    client = TestClient(app)
    response = client.post(
        "/mobile-use/api/v1/tools/tap",
        json={
            "session": {
                "pod_id": "pod-1",
                "product_id": "product-1",
                "authorization_token": "token",
                "tos_bucket": "bucket",
                "tos_region": "cn-beijing",
                "tos_endpoint": "tos-cn-beijing.volces.com",
            },
            "args": {"x": 1, "y": 2},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["action_name"] == "tap"
    assert body["payload"] == {"x": 1, "y": 2}


def test_take_screenshot_route_returns_structured_result(monkeypatch):
    monkeypatch.setattr(mobile_use_router, "service", FakeRouterService())
    client = TestClient(app)
    response = client.post(
        "/mobile-use/api/v1/tools/take_screenshot",
        json={
            "session": {
                "pod_id": "pod-1",
                "product_id": "product-1",
                "authorization_token": "token",
                "tos_bucket": "bucket",
                "tos_region": "cn-beijing",
                "tos_endpoint": "tos-cn-beijing.volces.com",
            }
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["width"] == 720
    assert body["height"] == 1520
    assert body["screenshot_url"].endswith(".png")


def test_swipe_route_returns_structured_action_result(monkeypatch):
    monkeypatch.setattr(mobile_use_router, "service", FakeRouterService())
    client = TestClient(app)
    response = client.post(
        "/mobile-use/api/v1/tools/swipe",
        json={
            "session": {
                "pod_id": "pod-1",
                "product_id": "product-1",
                "authorization_token": "token",
                "tos_bucket": "bucket",
                "tos_region": "cn-beijing",
                "tos_endpoint": "tos-cn-beijing.volces.com",
            },
            "args": {"from_x": 1, "from_y": 2, "to_x": 3, "to_y": 4},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["action_name"] == "swipe"
    assert body["payload"]["to_y"] == 4
