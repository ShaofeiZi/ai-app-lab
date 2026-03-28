import uvicorn

from mobile_use_service.config.settings import get_settings


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "app:app",
        host=settings.server.host,
        port=settings.server.port,
    )
