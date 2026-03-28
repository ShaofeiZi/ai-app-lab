from pydantic import BaseModel


class MobileUseSession(BaseModel):
    pod_id: str
    product_id: str
    authorization_token: str
    tos_bucket: str
    tos_region: str
    tos_endpoint: str
    tos_session_token: str = ""
    acep_host: str = ""
