# Teaching Comment Plan

> 标注模式：Serial annotation
>
> 本轮教学注释聚焦“默认启用的新链路”：
> `web -> mobile_agent_skill -> mobile_use_service`
>
> 以下内容不纳入本轮逐文件教学注释范围：
> - `mobile_agent/`：旧版兼容 Agent，当前不是默认启动链路
> - `mobile_use_mcp/`：旧版 Go MCP 服务，当前不是默认启动链路
> - `node_modules/`、`.next/`、`.venv/`、`.run/`、`__pycache__/`、`.pytest_cache/`：依赖、构建或运行产物

| source_path | target_path | language | category | status | notes |
| --- | --- | --- | --- | --- | --- |
| mobile_agent_skill/mobile_agent/agent/skills/definitions.py | mobile_agent_skill/mobile_agent/agent/skills/definitions.py | py | code-comment | done | 已补充技能定义、权限口子和风险字段的教学说明 |
| mobile_agent_skill/mobile_agent/agent/skills/registry.py | mobile_agent_skill/mobile_agent/agent/skills/registry.py | py | code-comment | done | 已解释默认技能注册表与新服务能力映射 |
| mobile_agent_skill/mobile_agent/agent/skills/policy.py | mobile_agent_skill/mobile_agent/agent/skills/policy.py | py | code-comment | done | 已解释 allowlist/denylist 和后续动态权限扩展 |
| mobile_agent_skill/mobile_agent/agent/skills/executor.py | mobile_agent_skill/mobile_agent/agent/skills/executor.py | py | code-comment | done | 已解释 skill 名到服务 tool 名的桥接 |
| mobile_agent_skill/mobile_agent/agent/skills/service_client.py | mobile_agent_skill/mobile_agent/agent/skills/service_client.py | py | code-comment | done | 已解释 HTTP 客户端职责、payload 和连接复用 |
| mobile_agent_skill/mobile_agent/agent/llm/stream_pipe.py | mobile_agent_skill/mobile_agent/agent/llm/stream_pipe.py | py | code-comment | done | 已解释流式缓冲桶、complete 收尾和最近修复点 |
| mobile_agent_skill/mobile_agent/agent/llm/doubao.py | mobile_agent_skill/mobile_agent/agent/llm/doubao.py | py | code-comment | done | 已解释模型调用返回值、流式收口和同步分支差异 |
| mobile_agent_skill/mobile_agent/agent/graph/nodes.py | mobile_agent_skill/mobile_agent/agent/graph/nodes.py | py | code-comment | done | 已解释 prepare/model/tool_valid/tool 主循环和条件边 |
| mobile_agent_skill/mobile_agent/agent/graph/sse_output.py | mobile_agent_skill/mobile_agent/agent/graph/sse_output.py | py | code-comment | done | 已解释 LangGraph 事件到前端 SSE 的协议转换 |
| mobile_agent_skill/mobile_agent/agent/mobile/doubao_action_parser.py | mobile_agent_skill/mobile_agent/agent/mobile/doubao_action_parser.py | py | code-comment | done | 已解释动作文本到 skill/tool 调用的翻译过程 |
| mobile_agent_skill/mobile_agent/agent/mobile_use_agent.py | mobile_agent_skill/mobile_agent/agent/mobile_use_agent.py | py | code-comment | done | 已解释新版 Agent 的 skill 装配和运行上下文 |
| mobile_agent_skill/mobile_agent/routers/agent.py | mobile_agent_skill/mobile_agent/routers/agent.py | py | code-comment | done | 已解释 SSE 路由、异常分支和取消机制 |
| mobile_agent_skill/mobile_agent/routers/session.py | mobile_agent_skill/mobile_agent/routers/session.py | py | code-comment | done | 已解释会话创建、复用与 reset 返回结构 |
| mobile_use_service/mobile_use_service/service/mobile_use_service.py | mobile_use_service/mobile_use_service/service/mobile_use_service.py | py | code-comment | done | 已解释 service 层职责、fallback 策略和各动作封装 |
| mobile_use_service/mobile_use_service/routers/mobile_use.py | mobile_use_service/mobile_use_service/routers/mobile_use.py | py | code-comment | done | 已解释新版服务路由和请求模型 |
| mobile_use_service/mobile_use_service/client/commands.py | mobile_use_service/mobile_use_service/client/commands.py | py | code-comment | done | 已解释兼容命令常量和 key code 映射 |
| mobile_use_service/mobile_use_service/client/volc_openapi.py | mobile_use_service/mobile_use_service/client/volc_openapi.py | py | code-comment | done | 已解释签名、统一请求层和高级动作接口 |
| web/src/app/chat/page.tsx | web/src/app/chat/page.tsx | tsx | code-comment | done | 已补充聊天页恢复会话与初始化云手机的教学说明 |
| web/src/hooks/useCreateSession.ts | web/src/hooks/useCreateSession.ts | ts | code-comment | done | 已补充创建会话与同步前端状态的教学说明 |
| web/src/lib/cloudAgent.ts | web/src/lib/cloudAgent.ts | ts | code-comment | done | 已补充 CloudAgent 状态持久化与 SSE 解析说明 |
| web/src/app/api/agent/stream/route.ts | web/src/app/api/agent/stream/route.ts | ts | code-comment | done | 已补充浏览器代理流式请求的教学说明 |
| web/src/app/api/session/create/route.ts | web/src/app/api/session/create/route.ts | ts | code-comment | done | 已补充浏览器代理创建会话请求的教学说明 |
| PROJECT_EXPLAINED.zh-CN.md | PROJECT_EXPLAINED.zh-CN.md | md | project-guide | done | 已重写为新版默认架构导读，聚焦 web -> mobile_agent_skill -> mobile_use_service |
