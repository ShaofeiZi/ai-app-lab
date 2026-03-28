# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# Licensed under the 【火山方舟】原型应用软件自用许可协议
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at 
#     https://www.volcengine.com/docs/82379/1433703
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
from typing import Optional
from mobile_agent.config.settings import MOBILE_USE_MCP_NAME
from mobile_agent.agent.infra.model import ToolCall
from mobile_agent.agent.utils.bbox import regular_bbox_for_ui_tars


"""
豆包模型输出的是“给人读的动作字符串”，系统真正执行时需要的是结构化工具调用。

这个文件做的事情就是把两者接起来：
- 输入：模型产出的动作文本，例如 `click(...)`、`wait(...)`
- 输出：内部统一的工具调用结构，例如 `mobile_use:tap`、`wait`

因此它本质上是一个“动作翻译层”。
"""


class DoubaoActionSpaceParser:
    """
    将豆包动作文本解析成 MCP 或本地工具调用。

    这里之所以需要专门的 parser，而不是让模型直接吐最终 JSON，
    是因为自然语言模型更容易稳定输出“类似函数调用”的文本格式。
    然后由本类负责做最后一步严谨的结构化映射。
    """

    layout_pattern = r"Summary:(?P<summary>[\s\S]*?)Action:(?P<action>.*)"
    action_pattern = r"(?P<action>\w+)\(\s*(?P<args>.*)\)"
    args_pattern = r"""
    click: start_box=\s*[\'"]<bbox>(?P<left>\d+)\s+(?P<top>\d+)\s+(?P<bottom>\d+)\s+(?P<right>\d+)</bbox>[\'"]
    drag: start_box=\s*[\'"]<bbox>(?P<start_left>\d+)\s+(?P<start_top>\d+)\s+(?P<start_right>\d+)\s+(?P<start_bottom>\d+)</bbox>[\'"],\s+end_box=\s*[\'"]<bbox>(?P<end_left>\d+)\s+(?P<end_top>\d+)\s+(?P<end_right>\d+)\s+(?P<end_bottom>\d+)</bbox>[\'"]
    type: content=[\'"](?P<content>.*)[\'"]
    wait: t=[\'"](?P<t>\d+)[\'"]
    call_user: content=[\'"](?P<content>.*)[\'"]
    finished: content=[\'"](?P<content>.*)[\'"]
    close_app: package_name=[\'"](?P<package_name>.*)[\'"]
    launch_app: package_name=[\'"](?P<package_name>.*)[\'"]
    """

    def __init__(
        self,
        phone_width: int,
        phone_height: int,
    ):
        # 手机尺寸会影响 bbox 坐标如何映射到真实点击点，
        # 所以 parser 在初始化时就要拿到当前屏幕宽高。
        self.phone_width = phone_width
        self.phone_height = phone_height
        self.layout_pattern = re.compile(DoubaoActionSpaceParser.layout_pattern)
        self.action_pattern = re.compile(DoubaoActionSpaceParser.action_pattern)
        # 这里把每种动作对应的参数解析规则预编译好，
        # 方便后续按动作名快速查表，而不是每次都临时构造正则。
        action_args_pattern = [
            line.split(":", 1)
            for line in DoubaoActionSpaceParser.args_pattern.strip().splitlines()
        ]
        self.args_pattern_map = {
            action.strip(): re.compile(pattern.strip())
            for (action, pattern) in action_args_pattern
        }

    def change_phone_dimensions(self, width: int, height: int):
        # 当设备横竖屏切换后，调用方可以通过这里同步新的尺寸信息。
        if width != 0:
            self.phone_width = width
        if height != 0:
            self.phone_height = height

    def error_action(self, action_call: Optional[str] = None):
        # 无法识别动作时，统一退回 error_action，方便上层走统一错误处理分支。
        return {"name": "error_action", "arguments": {"content": action_call}}

    def to_mcp_tool_call(self, action_call: str) -> ToolCall:
        """
        将模型返回的动作字符串转换为可执行的工具调用结构。

        整个流程分三步：
        1. 判断输入是否为空
        2. 拆出动作名和参数字符串
        3. 按动作类型进入不同的专用解析分支
        """
        if not action_call:
            return self.error_action("action_call is empty")

        # 先把 `click(...)` 这类格式拆成“动作名 + 参数文本”。
        action_match = self.action_pattern.match(action_call)
        if not action_match:
            return self.error_action(action_call)

        action_type = action_match.group("action").lower()
        args_str = action_match.group("args").strip()
        args_pattern = self.args_pattern_map.get(action_type)

        # 不同动作的参数格式完全不同，所以这里按类型分发，而不是强行一套规则通吃。
        if action_type == "click":
            return self.__call_tap(args_pattern, args_str)
        elif action_type == "type":
            return self.__call_type(args_pattern, args_str)
        elif action_type == "drag":
            return self.__call_swipe(args_pattern, args_str)
        elif action_type == "press_back":
            # 这类无参动作可以直接映射成固定工具名。
            return {"name": f"{MOBILE_USE_MCP_NAME}:back", "arguments": {}}
        elif action_type == "press_home":
            return {"name": f"{MOBILE_USE_MCP_NAME}:home", "arguments": {}}
        elif action_type == "close_app":
            # 这里兼容两种情况：
            # 1. 模型按约定输出 package_name="..."
            # 2. 模型只给出一个裸字符串
            args_match = args_pattern.search(args_str)
            if args_match:
                package_name = args_match.group(1)
                return {
                    "name": f"{MOBILE_USE_MCP_NAME}:close_app",
                    "arguments": {"package_name": package_name},
                }
            return {
                "name": f"{MOBILE_USE_MCP_NAME}:close_app",
                "arguments": {"package_name": args_str},
            }
        elif action_type == "launch_app":
            # 启动应用。
            # 这里最后映射到 skill 名，再由 SkillExecutor 转到新服务的 HTTP 接口。
            args_match = args_pattern.search(args_str)
            if args_match:
                package_name = args_match.group(1)
                return {
                    "name": f"{MOBILE_USE_MCP_NAME}:launch_app",
                    "arguments": {"package_name": package_name},
                }
            return {
                "name": f"{MOBILE_USE_MCP_NAME}:launch_app",
                "arguments": {"package_name": args_str},
            }
        elif action_type == "list_apps":
            return {"name": f"{MOBILE_USE_MCP_NAME}:list_apps", "arguments": {}}
        elif action_type == "wait":
            # 等待时间被钳制在 1 到 10 秒之间，
            # 防止模型给出离谱的等待时长，把整条链路卡住。
            args_match = args_pattern.search(args_str)
            if args_match:
                time = int(args_match.group(1))
                return {"name": "wait", "arguments": {"t": max(1, min(10, time))}}
            return {"name": "wait", "arguments": {"t": 1}}
        elif action_type == "call_user":
            # call_user 表示当前任务需要用户参与，而不是继续自动执行。
            args_match = args_pattern.search(args_str)
            if args_match:
                content = args_match.group(1)
                return {"name": "call_user", "arguments": {"content": content}}
            return {"name": "call_user", "arguments": {"content": args_str}}
        elif action_type == "finish" or action_type == "finished":
            # 兼容 finish / finished 两种写法，减少格式波动带来的失败。
            args_match = args_pattern.search(args_str)
            if args_match:
                content = args_match.group(1)
                return {"name": "finished", "arguments": {"content": content}}
            return {"name": "finished", "arguments": {"content": args_str}}

        # 动作名不在支持列表里时，统一返回 error_action。
        return self.error_action(action_call)

    def __call_tap(self, args_pattern: re.Pattern, args_str: str):
        # click 先解析出 bbox，再换算成矩形中心点。
        # 因为真正的 tap 接口接收的是 x、y 单点坐标，而不是一个框。
        try:
            args_match = args_pattern.search(args_str)
            if args_match:
                left, top, right, bottom = [
                    int(args_match.group(i)) for i in range(1, 5)
                ]

                left, top, right, bottom = regular_bbox_for_ui_tars(
                    left,
                    top,
                    right,
                    bottom,
                    width=self.phone_width,
                    height=self.phone_height,
                )

                return {
                    "name": f"{MOBILE_USE_MCP_NAME}:tap",
                    "arguments": {
                        # 点击中心点比直接用左上角更稳定，也更符合“点中目标”的语义。
                        "x": (left + right) // 2,
                        "y": (top + bottom) // 2,
                    },
                }
        except Exception as e:
            print(f"解析点击坐标失败")
        return self.error_action(f"click({args_str})")

    def __call_swipe(self, args_pattern: re.Pattern, args_str: str):
        # drag 需要起点和终点，所以要对两个 bbox 分别做规整与取中心点。
        try:
            args_match = args_pattern.search(args_str)
            if args_match:
                (
                    start_left,
                    start_top,
                    start_right,
                    start_bottom,
                    end_left,
                    end_top,
                    end_right,
                    end_bottom,
                ) = [int(args_match.group(i)) for i in range(1, 9)]

                start_left, start_top, start_right, start_bottom = (
                    regular_bbox_for_ui_tars(
                        start_left,
                        start_top,
                        start_right,
                        start_bottom,
                        width=self.phone_width,
                        height=self.phone_height,
                    )
                )

                end_left, end_top, end_right, end_bottom = regular_bbox_for_ui_tars(
                    end_left,
                    end_top,
                    end_right,
                    end_bottom,
                    width=self.phone_width,
                    height=self.phone_height,
                )

                return {
                    "name": f"{MOBILE_USE_MCP_NAME}:swipe",
                    "arguments": {
                        "from_x": ((start_left + start_right) // 2),
                        "from_y": ((start_top + start_bottom) // 2),
                        "to_x": ((end_left + end_right) // 2),
                        "to_y": ((end_top + end_bottom) // 2),
                    },
                }
        except Exception as e:
            print(f"解析点击坐标失败")
        return self.error_action(f"drag({args_str})")

    def __call_type(self, args_pattern: re.Pattern, args_str: str):
        # 输入文字是最直接的映射：取出 content 后交给 text_input 工具。
        try:
            args_match = args_pattern.search(args_str)
            if args_match:
                content = args_match.group(1)
                return {
                    "name": f"{MOBILE_USE_MCP_NAME}:text_input",
                    "arguments": {"text": content},
                }
        except Exception as e:
            print(f"解析失败")
        return self.error_action(f"type({args_str})")
