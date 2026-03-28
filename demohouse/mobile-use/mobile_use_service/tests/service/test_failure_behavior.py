from mobile_use_service.config.settings import get_settings
from mobile_use_service.models.session import MobileUseSession
from mobile_use_service.service.mobile_use_service import MobileUseService


class FailingCommandClient:
    def run_sync_command(self, session, command, permission_type):
        raise RuntimeError("device command failed")


def build_session() -> MobileUseSession:
    return MobileUseSession(
        pod_id="pod-1",
        product_id="product-1",
        authorization_token="token",
        tos_bucket="bucket",
        tos_region="cn-beijing",
        tos_endpoint="tos-cn-beijing.volces.com",
    )


def test_mock_fallback_is_disabled_by_default(monkeypatch):
    monkeypatch.delenv("MOBILE_USE_ALLOW_MOCK_FALLBACK", raising=False)
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.allow_mock_fallback is False


def test_action_fallback_is_marked_failed_when_enabled(monkeypatch):
    monkeypatch.setenv("MOBILE_USE_ALLOW_MOCK_FALLBACK", "true")
    get_settings.cache_clear()

    service = MobileUseService(client=FailingCommandClient())
    result = service.tap(build_session(), x=10, y=20)

    assert result.success is False
    assert result.payload["fallback_used"] is True
    assert "device command failed" in result.payload["error"]
