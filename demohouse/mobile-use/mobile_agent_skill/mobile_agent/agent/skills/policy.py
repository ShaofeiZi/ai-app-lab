from typing import Dict, List, Set, Any
from .definitions import SkillDefinition


class SkillPolicyResolver:
    def __init__(self, allowlist: Set[str] = None, denylist: Set[str] = None):
        # allowlist / denylist 组合在一起，能覆盖绝大多数“能力管控”场景：
        # - allowlist: 只允许明确列出的技能
        # - denylist: 在允许集合里再额外剔除一些能力
        self.allowlist = allowlist
        self.denylist = denylist or set()

    def filter(self, skills: List[SkillDefinition], context: Dict[str, Any]) -> List[SkillDefinition]:
        """
        按策略过滤技能列表。

        `context` 当前还没有深入使用，但这里提前把它保留下来，
        是为了以后支持更细粒度的动态判断，例如：
        - 某个 pod 只能使用只读能力
        - 某种用户身份不能调用高风险技能
        - 某个场景下临时禁用输入类动作
        """
        filtered = []
        for skill in skills:
            # 如果配置了 allowlist，那么“没在白名单里”就直接跳过。
            if self.allowlist is not None and skill.name not in self.allowlist:
                continue
            # denylist 的优先级更像是“最后再拦一次”，用于快速封禁个别技能。
            if skill.name in self.denylist:
                continue
            filtered.append(skill)
        return filtered
