import os
from functools import lru_cache

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class ServerSettings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8001


class OpenAPISettings(BaseModel):
    host: str = Field(
        default_factory=lambda: os.getenv(
            "MOBILE_USE_OPENAPI_HOST", "https://open.volcengineapi.com"
        )
    )
    region: str = Field(
        default_factory=lambda: os.getenv("MOBILE_USE_OPENAPI_REGION", "cn-north-1")
    )
    service: str = Field(
        default_factory=lambda: os.getenv("MOBILE_USE_OPENAPI_SERVICE", "ACEP")
    )
    version: str = Field(
        default_factory=lambda: os.getenv("MOBILE_USE_OPENAPI_VERSION", "2025-05-01")
    )
    timeout_seconds: float = Field(
        default_factory=lambda: float(os.getenv("MOBILE_USE_OPENAPI_TIMEOUT", "30"))
    )


class Settings(BaseSettings):
    app_name: str = "Mobile Use Service"
    app_version: str = "1.0.0"
    env: str = Field(default_factory=lambda: os.getenv("ENV", "production"))
    server: ServerSettings = Field(
        default_factory=lambda: ServerSettings(
            host=os.getenv("UVICORN_SERVER_HOST", "0.0.0.0"),
            port=int(os.getenv("UVICORN_SERVER_PORT", "8001")),
        )
    )
    openapi: OpenAPISettings = OpenAPISettings()
    allow_mock_fallback: bool = Field(
        default_factory=lambda: os.getenv(
            "MOBILE_USE_ALLOW_MOCK_FALLBACK", "false"
        ).lower()
        == "true"
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
