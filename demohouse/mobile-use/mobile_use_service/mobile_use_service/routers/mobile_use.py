from fastapi import APIRouter
from pydantic import BaseModel, Field

from mobile_use_service.models.session import MobileUseSession
from mobile_use_service.service.mobile_use_service import MobileUseService

router = APIRouter(prefix="/mobile-use/api/v1/tools")
service = MobileUseService()


class ToolArgsRequest(BaseModel):
    # 通用动作请求：
    # - session: 当前云手机会话身份
    # - args: 具体动作参数，例如点击坐标、输入文本
    session: MobileUseSession
    args: dict = Field(default_factory=dict)


class SessionOnlyRequest(BaseModel):
    # 某些动作不需要额外参数，例如截图、back、home。
    session: MobileUseSession


@router.post("/tap")
def tap(req: ToolArgsRequest):
    # 路由层保持尽量薄，只负责解析请求并转给 service。
    return service.tap(req.session, **req.args).model_dump()


@router.post("/take_screenshot")
def take_screenshot(req: SessionOnlyRequest):
    return service.take_screenshot(req.session).model_dump()


@router.post("/swipe")
def swipe(req: ToolArgsRequest):
    return service.swipe(req.session, **req.args).model_dump()


@router.post("/text_input")
def text_input(req: ToolArgsRequest):
    return service.text_input(req.session, **req.args).model_dump()


@router.post("/launch_app")
def launch_app(req: ToolArgsRequest):
    return service.launch_app(req.session, **req.args).model_dump()


@router.post("/close_app")
def close_app(req: ToolArgsRequest):
    return service.close_app(req.session, **req.args).model_dump()


@router.post("/list_apps")
def list_apps(req: SessionOnlyRequest):
    return service.list_apps(req.session).model_dump()


@router.post("/back")
def back(req: SessionOnlyRequest):
    return service.back(req.session).model_dump()


@router.post("/home")
def home(req: SessionOnlyRequest):
    return service.home(req.session).model_dump()


@router.post("/menu")
def menu(req: SessionOnlyRequest):
    return service.menu(req.session).model_dump()


@router.post("/terminate")
def terminate(req: ToolArgsRequest):
    return service.terminate(req.session, **req.args).model_dump()
