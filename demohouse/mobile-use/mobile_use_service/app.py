from fastapi import FastAPI

from mobile_use_service.config.settings import get_settings
from mobile_use_service.routers.mobile_use import router as mobile_use_router

settings = get_settings()

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.include_router(mobile_use_router)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": settings.app_name, "env": settings.env}
