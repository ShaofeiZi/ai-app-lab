from fastapi import FastAPI

from .mobile_use import router as mobile_use_router


def register_routers(app: FastAPI) -> None:
    app.include_router(mobile_use_router)


__all__ = ["register_routers"]
