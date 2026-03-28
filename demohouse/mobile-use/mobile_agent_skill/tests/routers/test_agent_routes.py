from fastapi.testclient import TestClient

from app import app


def test_health_route_returns_ok():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_stream_route_exists():
    client = TestClient(app)
    response = client.post(
        "/mobile-use/api/v1/agent/stream",
        json={"message": "hello", "thread_id": "t-1", "is_stream": True},
    )
    # Even if it returns 422 or 500 due to missing session, it shouldn't be 404
    assert response.status_code != 404
