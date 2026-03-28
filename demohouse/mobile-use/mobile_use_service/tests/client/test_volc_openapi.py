from mobile_use_service.client.volc_openapi import VolcMobileUseClient
from mobile_use_service.models.session import MobileUseSession


def test_build_common_headers_contains_json_content_type():
    client = VolcMobileUseClient(host="http://open.volcengineapi.com")
    headers = client.build_common_headers()
    assert headers["Content-Type"] == "application/json;charset=UTF-8"


def test_build_runtime_request_contains_session_fields():
    client = VolcMobileUseClient(host="http://open.volcengineapi.com")
    session = MobileUseSession(
        pod_id="pod-1",
        product_id="product-1",
        authorization_token="token",
        tos_bucket="bucket",
        tos_region="cn-beijing",
        tos_endpoint="tos-cn-beijing.volces.com",
    )
    payload = client.build_runtime_payload(session)
    assert payload["PodId"] == "pod-1"
    assert payload["ProductId"] == "product-1"


def test_build_runtime_request_accepts_optional_host_override():
    client = VolcMobileUseClient(host="http://open.volcengineapi.com")
    session = MobileUseSession(
        pod_id="pod-1",
        product_id="product-1",
        authorization_token="token",
        tos_bucket="bucket",
        tos_region="cn-beijing",
        tos_endpoint="tos-cn-beijing.volces.com",
        acep_host="https://open.volcengineapi.com",
    )
    payload = client.build_runtime_payload(session)
    assert payload == {"PodId": "pod-1", "ProductId": "product-1"}
