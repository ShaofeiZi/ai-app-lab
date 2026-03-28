from mobile_use_service.service.mobile_use_service import MobileUseService


class FakeClient:
    def run_action(self, session, action_name, payload=None):
        return {"action_name": action_name, "payload": payload or {}, "success": True}


def test_tap_calls_action_client():
    service = MobileUseService(client=FakeClient())
    result = service.tap(session=object(), x=10, y=20)
    assert result.success is True
    assert result.payload["x"] == 10


def test_swipe_calls_action_client():
    service = MobileUseService(client=FakeClient())
    result = service.swipe(session=object(), from_x=1, from_y=2, to_x=3, to_y=4)
    assert result.payload["to_y"] == 4


def test_text_input_calls_action_client():
    service = MobileUseService(client=FakeClient())
    result = service.text_input(session=object(), text="hello")
    assert result.payload["text"] == "hello"


def test_list_apps_uses_action_client_shape():
    service = MobileUseService(client=FakeClient())
    result = service.list_apps(session=object())
    assert result.action_name == "list_apps"
