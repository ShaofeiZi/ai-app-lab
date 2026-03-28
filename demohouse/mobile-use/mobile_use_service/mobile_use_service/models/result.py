from typing import Any

from pydantic import BaseModel, Field


class ScreenshotResult(BaseModel):
    screenshot_url: str
    width: int
    height: int


class ActionResult(BaseModel):
    action_name: str
    success: bool = True
    payload: dict[str, Any] = Field(default_factory=dict)
