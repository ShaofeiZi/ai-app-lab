# Mobile Use Skill Service Design

**Date:** 2026-03-28

**Status:** Approved

**Goal**

在不改动前端交互与接口协议的前提下，用一个新的后端技术方案替换 `mobile_use_mcp` 在执行链路中的职责。新方案需要：

- 复制一个新的 `mobile_agent`，专门改造成通过静态 skill 定义调用新服务。
- 新建一个 `mobile_use_service`，封装火山 OpenAPI、截图访问和动作执行能力。
- 保持 `web` 前端无感，仍使用原有请求与 SSE 协议。
- 通过 `demohouse/mobile-use/web/.env` 切换前端代理到新的 agent 后端服务。
- 为后续“agent 可加载哪些能力”的权限管控预留扩展点。

## Current State

当前项目链路如下：

`web -> mobile_agent -> MCPHub -> mobile_use_mcp`

现有实现中：

- `web` 通过 `/api/v1/agent/stream` 发起流式请求。
- `mobile_agent` 使用 `MCPHub` 动态连接 `mobile_use_mcp`。
- `Tools.from_mcp()` 通过 MCP 动态发现工具。
- `DoubaoActionSpaceParser` 将模型输出映射成 `mobile:tap`、`mobile:swipe` 这类 MCP 工具调用。
- `Mobile` 类通过 MCP 获取截图并执行基础动作。
- `mobile_use_mcp` 是 Go 服务，负责封装云手机动作与截图能力。

这个结构的主要问题是：工具暴露与执行都强绑定 MCP，无法自然演进到“静态 skill 定义 + 能力授权 + 新服务协议”这条路线。

## Constraints

- 前端页面、前端请求格式、SSE 消息格式尽量不变。
- 联调期间需要保留旧链路，避免一次性替换导致无法回退。
- 新 agent 需要复制为独立目录，而不是在原 `mobile_agent` 上直接大改。
- 前端通过 `web/.env` 切换后端目标地址，不要求页面增加模式开关。
- skill 定义必须预留授权过滤口子，便于后续做账号、环境、灰度、能力风险等维度的控制。

## Options Considered

### Option 1: Recommended

新增 `mobile_use_service`，复制 `mobile_agent` 为新目录，改造成静态 skill 调用新服务；前端保持无感，只通过 `web/.env` 切换代理到新的 agent 服务。

**Pros**

- 风险最可控，老链路完整保留。
- 新旧实现边界清晰，联调期方便回退和对比。
- 最符合“skill 定义 + 新服务”目标形态。
- 便于逐步引入能力授权，而不污染旧链路。

**Cons**

- 会短期维护两套 agent 代码。
- 启动脚本、构建脚本、文档需要补双服务说明。

### Option 2

在现有 `mobile_agent` 中抽象执行器，同时兼容 MCP 和 Skill Service 两种模式。

**Pros**

- 长期代码重复较少。

**Cons**

- 改动面太大，容易把现有可用链路一起带坏。
- 在方案尚未跑通前，抽象成本高于收益。

### Option 3

让新服务继续模拟 MCP 协议，尽量少改 agent。

**Pros**

- agent 改动最小。

**Cons**

- 不符合“通过 skill 定义调用新服务”的目标。
- 新服务背负不必要的协议兼容成本。

## Chosen Approach

采用 **Option 1**：

- 新建 `mobile_use_service/`
- 复制 `mobile_agent/` 为新的 agent 目录
- 新 agent 使用静态 skill 注册和执行，不再依赖 MCP 动态发现
- `web` 仍使用当前 API 形状，通过 `.env` 指向新的 agent 服务地址
- 联调完成前保留旧 `mobile_agent` 与 `mobile_use_mcp`

## Proposed Architecture

目标链路如下：

`web -> new mobile_agent service -> SkillRegistry/SkillExecutor -> mobile_use_service -> Volc OpenAPI/TOS`

### 1. New Agent Copy

复制现有 `mobile_agent` 为新的目录，例如：

- `mobile_agent_skill/`

新目录保留以下成熟能力：

- LangGraph 执行框架
- SSE 流式输出
- 会话管理
- 消息与记忆结构
- 成本统计
- 提示词与动作解析主流程

新目录替换以下 MCP 相关实现：

- `MCPHub`
- `Tools.from_mcp()`
- `McpTool`
- `Mobile.initialize()` 中的 MCP 会话初始化
- `Mobile._take_screenshot()` 中的 MCP 调用

### 2. Skill Layer

新 agent 引入静态 skill 层，建议结构如下：

- `agent/skills/definitions.py`
- `agent/skills/registry.py`
- `agent/skills/policy.py`
- `agent/skills/executor.py`
- `agent/skills/handlers/*.py`

职责划分：

- `definitions.py`：定义所有候选 skill 的名称、描述、参数 schema、handler、标签、scope、风险等级。
- `registry.py`：加载系统支持的全部候选 skill。
- `policy.py`：根据上下文筛选当前允许暴露给模型的 skill。
- `executor.py`：按名字执行 skill，并做二次授权校验。
- `handlers/*.py`：每个 skill 调用 `mobile_use_service` 中对应业务接口。

### 3. Permission Control Extension Point

skill 设计必须支持后续管控。建议每个 skill 至少包含：

- `name`
- `description`
- `parameters_schema`
- `handler`
- `tags`
- `scopes`
- `enabled_by_default`
- `risk_level`

建议引入两层控制：

- 暴露层控制：模型只看到被允许的 skill。
- 执行层控制：即使模型构造未授权 skill，也会在执行前被拒绝。

第一版不接复杂权限平台，只预留接口与配置能力：

- 配置 allowlist / denylist
- 基于环境或 agent 名称过滤
- 后续可扩展到账号、租户、灰度规则

### 4. New Service

新增 `mobile_use_service/`，第一版优先做成 Python 服务模块，可先同进程复用，后续再决定是否独立部署。

服务分为两层：

- `VolcMobileUseClient`
  - 负责火山 OpenAPI 请求、鉴权、签名、错误解析
  - 负责 TOS 预签名截图 URL 生成
- `MobileUseService`
  - 负责向 agent 提供统一业务接口
  - 负责把动作型调用映射到具体 OpenAPI 或编排逻辑

建议第一版对外暴露与旧工具名尽量一致的接口：

- `take_screenshot`
- `tap`
- `swipe`
- `text_input`
- `launch_app`
- `close_app`
- `list_apps`
- `back`
- `home`
- `menu`
- `terminate`

### 5. Compatibility Boundary

为满足“前端无感”要求：

- `web` 页面与请求体结构不改。
- `web` 通过 `.env` 中的后端地址切换请求目标。
- 新 agent 对 `/stream` 与 `/cancel` 保持兼容。
- SSE 输出结构与消息类型保持兼容。
- 截图结果仍优先返回旧链路可直接消费的 JSON 文本结构。

## Data Flow

新链路的数据流如下：

1. `web` 调用现有流式接口。
2. 新 agent 初始化会话上下文：
   - `pod_id`
   - `product_id`
   - `authorization_token`
   - `tos_bucket`
   - `tos_region`
   - `tos_endpoint`
3. `SkillRegistry` 加载全部候选 skill。
4. `SkillPolicyResolver` 根据上下文筛选可用 skill。
5. 模型只看到当前允许的 skill schema。
6. 动作解析器把模型输出转换为内部 `ToolCall`。
7. `SkillExecutor` 调用对应 handler。
8. handler 调用 `mobile_use_service`。
9. `mobile_use_service` 访问火山 OpenAPI / TOS 并返回结果。
10. agent 沿用现有 SSE 逻辑将过程消息推送给前端。

## Error Handling

建议将错误分为四层：

### Volc API Error

- 鉴权失败
- 参数不合法
- 请求超时
- 远端接口返回错误码

### Service Mapping Error

- 返回字段解析失败
- 动作请求映射错误
- TOS URL 生成失败

### Skill Execution Error

- skill 不存在
- 参数校验失败
- skill 未授权

### Agent Runtime Error

- 动作解析失败
- LangGraph 执行异常
- SSE 中断

日志建议统一带上：

- `thread_id`
- `task_id`
- `pod_id`
- `skill_name`
- `action_name`
- `request_id` 或远端运行标识

## Testing Strategy

按四层验证：

1. `mobile_use_service` 单元测试
   - 请求参数拼装
   - 返回结构解析
   - 截图 URL 生成
   - 错误映射
2. 新 agent 集成测试
   - skill 注册
   - skill 过滤
   - handler 调用
   - 截图兼容解析
3. 路由级测试
   - `/stream`
   - `/cancel`
   - SSE 兼容性
4. Web 联调测试
   - 创建会话
   - 流式输出
   - 截图展示
   - 动作执行
   - 取消任务
   - 异常收尾

## File and Module Plan

建议新增目录与核心模块如下：

- `mobile_use_service/`
  - `app.py`
  - `main.py`
  - `config.toml`
  - `mobile_use_service/client/volc_openapi.py`
  - `mobile_use_service/service/mobile_use_service.py`
  - `mobile_use_service/models/session.py`
  - `mobile_use_service/models/result.py`
  - `mobile_use_service/exception/*.py`
  - `mobile_use_service/routers/*.py`

- `mobile_agent_skill/`
  - 从 `mobile_agent/` 复制得到
  - 新增 `mobile_agent/agent/skills/*`
  - 用静态 skill 执行替代 MCP 相关实现

- `web/.env`
  - 调整后端服务地址，切换到新的 agent 服务

- 启动脚本与构建脚本
  - 新增或扩展新 agent / 新服务启动逻辑
  - 保留旧服务的启动能力，便于回退

## Rollout Plan

建议按以下顺序推进：

1. 新建 `mobile_use_service`，先完成底层 client 与截图/动作接口封装。
2. 复制 `mobile_agent` 为新目录，并保留原有运行链路。
3. 在新 agent 中落 skill 注册、过滤、执行框架。
4. 用新 service 替换截图与动作执行。
5. 保持与现有 SSE 协议兼容。
6. 通过 `web/.env` 将前端代理切到新 agent 服务。
7. 做 Web 全链路联调。
8. 联调稳定后，再决定是否进一步收敛老代码。

## Out of Scope

以下内容不在本次设计第一阶段范围内：

- 删除 `mobile_use_mcp`
- 合并新旧 agent 目录
- 接入完整 RBAC 或权限平台
- 重写前端页面或协议
- 在第一版中强制把 `mobile_use_service` 独立成远程部署服务

## Risks

- 火山 OpenAPI 是否完整覆盖当前 MCP 工具动作，需要在实现前逐项确认。
- 新 agent 复制后，配置与依赖管理容易出现分叉，需要尽早标准化。
- skill 与提示词的契合度可能影响模型稳定性，需要联调中观察动作格式。
- 如果截图返回格式与旧链路不完全一致，可能影响坐标换算与前端展示。

## Decision Summary

最终确认：

- 新建 `mobile_use_service`
- 复制一个新的 `mobile_agent`
- 新 agent 使用静态 skill 定义调用新服务
- skill 层预留权限管控口子
- 前端无感，仍走现有 API 和 SSE
- 使用 `demohouse/mobile-use/web/.env` 切换前端后端服务地址
- 联调阶段保留旧链路，便于回退
