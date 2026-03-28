from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field


class SkillDefinition(BaseModel):
    """
    描述一个“可被 Agent 调用的能力”。

    这里故意把技能定义建模成一个独立的数据对象，而不是直接散落在执行代码里，
    是为了让系统后续更容易做三件事：
    1. 给模型展示“我现在有哪些能力可以用”
    2. 在注册阶段统一管理能力元数据
    3. 在策略层做权限过滤、灰度放量或风险控制
    """

    name: str
    # 技能的唯一名称。
    # 例如 `mobile:tap`，前半段通常表示能力域，后半段表示具体动作。
    description: str
    # 给模型和开发者看的解释，说明这个技能大概是做什么的。
    parameters_schema: Dict[str, Any]
    # 这里存的是 JSON Schema 风格的参数定义。
    # 好处是模型、校验器、调试工具都可以复用同一份结构描述。
    handler: Optional[Callable] = None
    # 可选的本地处理函数。
    # 当前新版链路主要走统一的 service 执行器，所以这里通常为空；
    # 但保留这个字段后，未来可以很方便地接入“本地直接执行”的技能。
    tags: List[str] = Field(default_factory=list)
    # tags 更像是“描述性标签”，便于后续做分类、检索或调试面板展示。
    scopes: List[str] = Field(default_factory=list)
    # scopes 是为权限控制预留的扩展口子：
    # 以后如果要限制“某类 agent 只能使用某些能力”，可以在这里挂能力范围。
    enabled_by_default: bool = True
    # 默认启用开关，用来支持“定义存在，但默认先不放给模型用”的场景。
    risk_level: str = "low"
    # 风险等级也是后续治理的预留字段。
    # 例如点击、输入通常是低风险，而支付、删除、外跳等动作可能会被标成更高风险。
