# 迁移指南: Skill-driven Agent 架构

为了提升系统的可扩展性和稳定性，我们将后端的动态 MCP 架构替换为基于 Skill 的静态注册架构。

## 主要变更点

1. **移动能力剥离 (`mobile_use_service`)**:
   将原有直接与手机终端交互的代码抽取为独立的 `mobile_use_service`（默认运行在 `8001` 端口）。
2. **Skill Agent (`mobile_agent_skill`)**:
   将原有 `mobile_agent` 的 MCP 动态发现替换为本地静态注册的 `SkillRegistry`（默认运行在 `8002` 端口）。所有执行请求会路由至 `mobile_use_service`。
3. **前端切换**:
   前端可以通过 `web/.env` 中的 `CLOUD_AGENT_BASE_URL` 配置选择不同的后端。

## 回退策略 (Fallback)

如果在联调或测试过程中发现问题，系统允许无缝回退到旧版 Agent 架构：

1. 使用 `START_LEGACY_STACK=1 ./start.sh` 显式启动旧版 `mobile_agent` 与 `mobile_use_mcp`。
2. 修改 `web/.env`，将 `CLOUD_AGENT_BASE_URL` 改回 `http://localhost:8000/mobile-use/`。
3. 重启前端 Web 服务即可恢复。

## 验证与测试

在合并代码前，确保运行所有单元测试：
```bash
# 验证 service
cd mobile_use_service && PYTHONPATH=. pytest -q

# 验证 skill agent
cd mobile_agent_skill && PYTHONPATH=. pytest -c /dev/null tests -q
```
