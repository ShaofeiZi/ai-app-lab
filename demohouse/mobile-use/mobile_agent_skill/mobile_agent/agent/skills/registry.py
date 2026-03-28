from typing import List
from .definitions import SkillDefinition


class SkillRegistry:
    def __init__(self, auto_register: bool = True):
        # 注册表本质上就是“当前 agent 允许看到的技能清单”。
        # 初始化时可以选择自动灌入一组核心技能，也可以传 `auto_register=False`
        # 来构造一个空注册表，方便测试或做二次裁剪。
        self._skills: List[SkillDefinition] = []
        if auto_register:
            self._register_core_skills()

    @classmethod
    def from_skills(cls, skills: List[SkillDefinition]) -> "SkillRegistry":
        # 这个工厂方法常用于“先过滤，再重新组装”：
        # 例如策略层筛掉一部分技能后，把剩下的技能重新包成一个新的注册表。
        registry = cls(auto_register=False)
        registry._skills = list(skills)
        return registry

    def _register_core_skills(self):
        # 这里注册的是新版默认链路的核心手机能力。
        # 它们不会直接连旧的 MCP 服务，而是最终由 SkillExecutor 转发到新的
        # `mobile_use_service` HTTP 服务。
        self.register(
            SkillDefinition(
                name="mobile:tap",
                description="Tap at the given x, y coordinates",
                parameters_schema={"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}}},
            )
        )
        self.register(
            SkillDefinition(
                name="mobile:take_screenshot",
                description="Take a screenshot of the current screen",
                parameters_schema={"type": "object", "properties": {}},
            )
        )
        self.register(
            SkillDefinition(
                name="mobile:swipe",
                description="Swipe from one point to another",
                parameters_schema={
                    "type": "object",
                    "properties": {
                        "from_x": {"type": "integer"},
                        "from_y": {"type": "integer"},
                        "to_x": {"type": "integer"},
                        "to_y": {"type": "integer"},
                    },
                },
            )
        )
        self.register(
            SkillDefinition(
                name="mobile:text_input",
                description="Input text on the screen",
                parameters_schema={"type": "object", "properties": {"text": {"type": "string"}}},
            )
        )
        self.register(
            SkillDefinition(
                name="mobile:launch_app",
                description="Launch an app by package name",
                parameters_schema={"type": "object", "properties": {"package_name": {"type": "string"}}},
            )
        )
        self.register(
            SkillDefinition(
                name="mobile:close_app",
                description="Close an app by package name",
                parameters_schema={"type": "object", "properties": {"package_name": {"type": "string"}}},
            )
        )
        self.register(
            SkillDefinition(
                name="mobile:list_apps",
                description="List installed apps",
                parameters_schema={"type": "object", "properties": {}},
            )
        )
        self.register(
            SkillDefinition(
                name="mobile:back",
                description="Go back one page",
                parameters_schema={"type": "object", "properties": {}},
            )
        )
        self.register(
            SkillDefinition(
                name="mobile:home",
                description="Go to home screen",
                parameters_schema={"type": "object", "properties": {}},
            )
        )
        self.register(
            SkillDefinition(
                name="mobile:menu",
                description="Open menu",
                parameters_schema={"type": "object", "properties": {}},
            )
        )

    def register(self, skill: SkillDefinition):
        # 当前实现比较朴素，直接追加。
        # 如果以后要支持覆盖、去重或版本管理，可以在这里扩展规则。
        self._skills.append(skill)

    def list_all(self) -> List[SkillDefinition]:
        # 返回当前注册表中的全部技能定义，供策略层或工具装配层消费。
        return self._skills
