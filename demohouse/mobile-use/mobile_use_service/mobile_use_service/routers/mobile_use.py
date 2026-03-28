from fastapi import APIRouter, Response, status
from pydantic import BaseModel, Field

from mobile_use_service.models.session import MobileUseSession
from mobile_use_service.models.result import ActionResult, ScreenshotResult
from mobile_use_service.service.mobile_use_service import MobileUseService

router = APIRouter(prefix="/mobile-use/api/v1/tools")
service = MobileUseService()


class ToolArgsRequest(BaseModel):
    """
    通用动作请求模型。

    用于需要额外参数的API动作，如点击坐标、滑动路径、应用包名等。
    """
    session: MobileUseSession = Field(
        ...,
        description="云手机会话信息，包含身份认证和云手机资源标识",
        examples=[{
            "pod_id": "pod-12345",
            "product_id": "product-abc",
            "authorization_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "tos_bucket": "screenshot-bucket",
            "tos_region": "cn-beijing",
            "tos_endpoint": "tos-cn-beijing.volces.com",
            "tos_session_token": "session-token-xxx",
            "acep_host": "acep.example.com"
        }]
    )
    args: dict = Field(
        default_factory=dict,
        description="动作执行参数，键值对形式。不同动作需要不同的参数组合",
        examples=[{"x": 100, "y": 200}, {"from_x": 100, "from_y": 200, "to_x": 300, "to_y": 400}, {"text": "Hello World"}, {"package_name": "com.example.app"}]
    )


class SessionOnlyRequest(BaseModel):
    """
    仅会话请求模型。

    用于不需要额外参数的API动作，如截图、返回、主页等系统操作。
    """
    session: MobileUseSession = Field(
        ...,
        description="云手机会话信息，包含身份认证和云手机资源标识",
        examples=[{
            "pod_id": "pod-12345",
            "product_id": "product-abc",
            "authorization_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "tos_bucket": "screenshot-bucket",
            "tos_region": "cn-beijing",
            "tos_endpoint": "tos-cn-beijing.volces.com",
            "tos_session_token": "session-token-xxx",
            "acep_host": "acep.example.com"
        }]
    )


@router.post(
    "/tap",
    response_model=ActionResult,
    summary="点击屏幕指定坐标",
    description="在云手机屏幕上指定坐标位置执行点击操作。常用于按钮点击、菜单选择、输入框聚焦等场景。坐标系统以屏幕左上角为原点(0,0)，向右向下为正方向。",
    tags=["基础交互操作"],
    responses={
        200: {
            "description": "点击操作执行成功",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "action_name": {"type": "string", "example": "tap"},
                            "success": {"type": "boolean", "example": True},
                            "payload": {
                                "type": "object",
                                "properties": {
                                    "x": {"type": "integer", "description": "点击X坐标"},
                                    "y": {"type": "integer", "description": "点击Y坐标"}
                                }
                            }
                        }
                    }
                }
            }
        },
        400: {"description": "请求参数错误 - 坐标值无效或超出屏幕范围"},
        401: {"description": "认证失败 - 会话Token无效或已过期"},
        500: {"description": "服务端执行错误 - 云手机通信异常"}
    }
)
def tap(req: ToolArgsRequest):
    """
    在云手机屏幕上指定坐标执行点击操作。

    ## 参数说明
    - **x**: 点击位置的X坐标（从屏幕左边缘计算）
    - **y**: 点击位置的Y坐标（从屏幕上边缘计算）

    ## 使用场景
    - UI按钮点击
    - 菜单项选择
    - 输入框聚焦
    - 图标启动应用

    ## 注意事项
    - 坐标值应为正整数
    - 坐标值不能超过屏幕分辨率范围
    - 建议先调用截图接口确认元素位置
    """
    return service.tap(req.session, **req.args).model_dump()


@router.post(
    "/take_screenshot",
    response_model=ScreenshotResult,
    summary="获取云手机屏幕截图",
    description="截取云手机当前屏幕画面并上传到对象存储，返回可访问的截图URL及分辨率信息。这是Agent决策的核心输入，每轮交互前都会执行此操作获取最新屏幕状态。",
    tags=["基础交互操作"],
    responses={
        200: {
            "description": "截图获取成功",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "screenshot_url": {"type": "string", "description": "截图访问URL"},
                            "width": {"type": "integer", "description": "屏幕宽度像素"},
                            "height": {"type": "integer", "description": "屏幕高度像素"}
                        }
                    }
                }
            }
        },
        401: {"description": "认证失败 - 会话Token无效或已过期"},
        500: {"description": "截图获取失败 - 云手机通信异常或存储服务不可用"}
    }
)
def take_screenshot(req: SessionOnlyRequest):
    """
    获取云手机当前屏幕的截图。

    ## 功能说明
    返回当前云手机屏幕的截图URL、宽度和高度信息。
    截图以PNG格式存储，支持PNG、JPEG等常见图片格式访问。

    ## 返回值
    - **screenshot_url**: 可直接访问的截图URL，有效期通常为1小时
    - **width**: 屏幕宽度像素值（如720、1080等）
    - **height**: 屏幕高度像素值（如1520、1920等）

    ## 使用建议
    - 每次执行动作前建议先截图确认当前状态
    - Agent每轮决策前都会先获取截图作为输入
    - 截图URL存在有效期，及时使用或刷新
    """
    return service.take_screenshot(req.session).model_dump()


@router.post(
    "/swipe",
    response_model=ActionResult,
    summary="在屏幕上执行滑动操作",
    description="在云手机屏幕上从起点坐标滑动到终点坐标。用于页面滚动、列表浏览、手势操作等场景。滑动路径为直线，速度固定。",
    tags=["基础交互操作"],
    responses={
        200: {
            "description": "滑动操作执行成功",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "action_name": {"type": "string", "example": "swipe"},
                            "success": {"type": "boolean", "example": True},
                            "payload": {
                                "type": "object",
                                "properties": {
                                    "from_x": {"type": "integer"},
                                    "from_y": {"type": "integer"},
                                    "to_x": {"type": "integer"},
                                    "to_y": {"type": "integer"}
                                }
                            }
                        }
                    }
                }
            }
        },
        400: {"description": "请求参数错误 - 坐标值无效或超出屏幕范围"},
        401: {"description": "认证失败 - 会话Token无效或已过期"},
        500: {"description": "服务端执行错误 - 云手机通信异常"}
    }
)
def swipe(req: ToolArgsRequest):
    """
    在云手机屏幕上执行滑动操作。

    ## 参数说明
    - **from_x**: 滑动起点X坐标
    - **from_y**: 滑动起点Y坐标
    - **to_x**: 滑动终点X坐标
    - **to_y**: 滑动终点Y坐标

    ## 使用场景
    - 上下滚动页面浏览内容
    - 左右滑动切换页面/标签
    - 下滑下拉刷新
    - 上滑加载更多

    ## 注意事项
    - 滑动时长固定（约300ms）
    - 坐标值应为正整数
    - 起止点不能相同
    """
    return service.swipe(req.session, **req.args).model_dump()


@router.post(
    "/text_input",
    response_model=ActionResult,
    summary="向当前焦点元素输入文本",
    description="向当前获得焦点的输入框或文本控件输入文本内容。执行前会自动切换输入法并清空原有内容，支持中英文输入。",
    tags=["基础交互操作"],
    responses={
        200: {
            "description": "文本输入执行成功",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "action_name": {"type": "string", "example": "text_input"},
                            "success": {"type": "boolean", "example": True},
                            "payload": {
                                "type": "object",
                                "properties": {
                                    "text": {"type": "string", "description": "输入的文本内容"}
                                }
                            }
                        }
                    }
                }
            }
        },
        400: {"description": "请求参数错误 - 文本内容为空或包含非法字符"},
        401: {"description": "认证失败 - 会话Token无效或已过期"},
        500: {"description": "服务端执行错误 - 输入法切换或文本输入失败"}
    }
)
def text_input(req: ToolArgsRequest):
    """
    向当前焦点元素输入文本。

    ## 参数说明
    - **text**: 要输入的文本内容，支持UTF-8编码的任意字符

    ## 执行流程
    1. 切换到专用输入法
    2. 清空当前输入框内容
    3. 通过Base64编码发送文本到云手机
    4. 输入法将文本注入到焦点元素

    ## 使用场景
    - 搜索框输入关键词
    - 表单字段填写
    - 聊天消息发送
    - 验证码输入

    ## 注意事项
    - 需要先点击或聚焦到输入框
    - 超长文本可能需要分多次输入
    - 特殊字符可能被过滤
    """
    return service.text_input(req.session, **req.args).model_dump()


@router.post(
    "/launch_app",
    response_model=ActionResult,
    summary="启动指定应用",
    description="根据应用包名启动云手机上已安装的应用。应用必须在设备上已安装，否则会返回错误。",
    tags=["应用管理"],
    responses={
        200: {
            "description": "应用启动成功",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "action_name": {"type": "string", "example": "launch_app"},
                            "success": {"type": "boolean", "example": True},
                            "payload": {
                                "type": "object",
                                "properties": {
                                    "package_name": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            }
        },
        400: {"description": "请求参数错误 - 包名格式无效或为空"},
        401: {"description": "认证失败 - 会话Token无效或已过期"},
        404: {"description": "应用未找到 - 包名对应的应用未安装"},
        500: {"description": "服务端执行错误 - 应用启动失败"}
    }
)
def launch_app(req: ToolArgsRequest):
    """
    启动指定包名的应用。

    ## 参数说明
    - **package_name**: 目标应用的包名（格式如 com.example.app）

    ## 使用场景
    - 启动特定应用进行操作
    - 切换到不同应用完成任务
    - 打开系统设置等

    ## 常见包名示例
    - 微信: com.tencent.mm
    - 淘宝: com.taobao.taobao
    - 抖音: com.ss.android.ugc.aweme

    ## 注意事项
    - 应用必须已安装在云手机上
    - 可先使用list_apps接口获取已安装应用列表
    - 启动需要一定时间，可配合截图确认启动成功
    """
    return service.launch_app(req.session, **req.args).model_dump()


@router.post(
    "/close_app",
    response_model=ActionResult,
    summary="关闭指定应用",
    description="根据应用包名关闭云手机上正在运行的应用。只会结束目标应用进程，不会影响其他应用。",
    tags=["应用管理"],
    responses={
        200: {
            "description": "应用关闭成功",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "action_name": {"type": "string", "example": "close_app"},
                            "success": {"type": "boolean", "example": True},
                            "payload": {
                                "type": "object",
                                "properties": {
                                    "package_name": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            }
        },
        400: {"description": "请求参数错误 - 包名格式无效或为空"},
        401: {"description": "认证失败 - 会话Token无效或已过期"},
        404: {"description": "应用未找到或未运行"},
        500: {"description": "服务端执行错误 - 应用关闭失败"}
    }
)
def close_app(req: ToolArgsRequest):
    """
    关闭指定包名的应用。

    ## 参数说明
    - **package_name**: 要关闭的应用包名

    ## 使用场景
    - 清理后台应用释放资源
    - 结束卡死的应用进程
    - 切换到干净的应用环境

    ## 注意事项
    - 如果应用未运行，不会返回错误
    - 系统关键应用可能无法被关闭
    - 强制关闭可能导致数据未保存
    """
    return service.close_app(req.session, **req.args).model_dump()


@router.post(
    "/list_apps",
    response_model=ActionResult,
    summary="获取已安装应用列表",
    description="获取云手机上所有已安装应用的列表信息，包括应用ID、名称、包名和安装状态。",
    tags=["应用管理"],
    responses={
        200: {
            "description": "获取应用列表成功",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "action_name": {"type": "string", "example": "list_apps"},
                            "success": {"type": "boolean", "example": True},
                            "payload": {
                                "type": "object",
                                "properties": {
                                    "apps": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "app_id": {"type": "string"},
                                                "app_name": {"type": "string"},
                                                "package_name": {"type": "string"},
                                                "install_status": {"type": "string"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        401: {"description": "认证失败 - 会话Token无效或已过期"},
        500: {"description": "服务端执行错误 - 获取应用列表失败"}
    }
)
def list_apps(req: SessionOnlyRequest):
    """
    获取云手机上已安装的应用列表。

    ## 返回应用信息
    每个应用包含以下字段：
    - **app_id**: 应用ID
    - **app_name**: 应用显示名称
    - **package_name**: 应用包名（唯一标识）
    - **install_status**: 安装状态

    ## 使用场景
    - 查询特定应用是否已安装
    - 启动前确认目标应用存在
    - 设备状态检查

    ## 注意事项
    - 返回列表可能较长，包含系统应用
    - 安装状态值可能为: installed, uninstalled, update_available等
    """
    return service.list_apps(req.session).model_dump()


@router.post(
    "/back",
    response_model=ActionResult,
    summary="执行返回操作",
    description="模拟按下Android返回键，执行返回上一级菜单或页面的操作。",
    tags=["系统操作"],
    responses={
        200: {
            "description": "返回操作执行成功",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "action_name": {"type": "string", "example": "back"},
                            "success": {"type": "boolean", "example": True},
                            "payload": {"type": "object", "description": "空 payload"}
                        }
                    }
                }
            }
        },
        401: {"description": "认证失败 - 会话Token无效或已过期"},
        500: {"description": "服务端执行错误 - 返回键操作失败"}
    }
)
def back(req: SessionOnlyRequest):
    """
    执行Android返回键操作。

    ## 功能说明
    模拟用户按下手机上的返回键，
    通常用于退出当前页面、关闭弹窗、返回上一级等场景。

    ## 使用场景
    - 关闭当前页面返回上级
    - 关闭弹窗或对话框
    - 取消输入返回
    - 退出应用确认框

    ## 注意事项
    - 如果在桌面按返回键通常无效果
    - 某些应用可能拦截返回键有自己的处理逻辑
    """
    return service.back(req.session).model_dump()


@router.post(
    "/home",
    response_model=ActionResult,
    summary="返回桌面主页",
    description="模拟按下Android Home键，返回设备桌面主屏幕。",
    tags=["系统操作"],
    responses={
        200: {
            "description": "返回桌面操作执行成功",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "action_name": {"type": "string", "example": "home"},
                            "success": {"type": "boolean", "example": True},
                            "payload": {"type": "object", "description": "空 payload"}
                        }
                    }
                }
            }
        },
        401: {"description": "认证失败 - 会话Token无效或已过期"},
        500: {"description": "服务端执行错误 - Home键操作失败"}
    }
)
def home(req: SessionOnlyRequest):
    """
    执行Android Home键操作。

    ## 功能说明
    模拟用户按下手机上的Home键，
    立即返回设备桌面主屏幕，同时最小化当前应用。

    ## 使用场景
    - 中断当前操作返回桌面
    - 切换到桌面查看通知
    - 结束当前应用回到桌面
    - 任何需要快速回到主屏幕的场景

    ## 注意事项
    - 这是最安全的打断当前操作的方式
    - 不会退出应用，只是最小化
    - 某些Launcher可能行为略有差异
    """
    return service.home(req.session).model_dump()


@router.post(
    "/menu",
    response_model=ActionResult,
    summary="打开菜单选项",
    description="模拟按下Android菜单键，打开当前页面的选项菜单。",
    tags=["系统操作"],
    responses={
        200: {
            "description": "菜单操作执行成功",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "action_name": {"type": "string", "example": "menu"},
                            "success": {"type": "boolean", "example": True},
                            "payload": {"type": "object", "description": "空 payload"}
                        }
                    }
                }
            }
        },
        401: {"description": "认证失败 - 会话Token无效或已过期"},
        500: {"description": "服务端执行错误 - 菜单键操作失败"}
    }
)
def menu(req: SessionOnlyRequest):
    """
    执行Android菜单键操作。

    ## 功能说明
    模拟用户按下手机上的菜单键，
    尝试打开当前页面的选项菜单（Options Menu）。

    ## 使用场景
    - 打开应用附加选项
    - 访问设置、搜索等选项
    - 某些老应用的标准操作入口

    ## 注意事项
    - 很多现代应用已不使用物理菜单键
    - 部分应用使用Toolbar或右上角图标代替
    - 如果当前页面没有菜单，按下后可能无效果
    """
    return service.menu(req.session).model_dump()


@router.post(
    "/terminate",
    response_model=ActionResult,
    summary="终止当前任务会话",
    description="发送终止信号，通知上游Agent当前任务链应该结束。这是一个语义化信号，不会真正销毁云手机资源。",
    tags=["系统操作"],
    responses={
        200: {
            "description": "终止信号发送成功",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "action_name": {"type": "string", "example": "terminate"},
                            "success": {"type": "boolean", "example": True},
                            "payload": {
                                "type": "object",
                                "properties": {
                                    "reason": {"type": "string", "description": "终止原因"}
                                }
                            }
                        }
                    }
                }
            }
        },
        400: {"description": "请求参数错误 - 终止原因未提供"},
        401: {"description": "认证失败 - 会话Token无效或已过期"}
    }
)
def terminate(req: ToolArgsRequest):
    """
    发送任务终止信号。

    ## 参数说明
    - **reason**: 终止原因描述，用于日志和调试

    ## 功能说明
    这是一个语义化的终止信号，告诉上层Agent系统：
    当前任务链已完成或应该中止，可以进行结果汇总或开始新任务。

    ## 使用场景
    - 任务目标已达成，正常结束
    - 遇到无法完成的任务，主动终止
    - 超时或资源限制需要结束
    - 错误后安全终止流程

    ## 注意事项
    - 不会真正关闭或销毁云手机
    - 不会中断当前运行的任何应用
    - 仅作为上层工作流的控制信号
    - 云手机资源会继续保留计费
    """
    return service.terminate(req.session, **req.args).model_dump()
