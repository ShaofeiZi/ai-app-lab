# Mobile Use - 面向移动端 AI Agent 的基础设施到应用一体化方案

[English](README.md) | 简体中文

## 🚀 项目概览

[Mobile Use 产品方案文档](https://www.volcengine.com/docs/6394/1583515)

**Mobile Use** 基于 **火山引擎云手机** 与 **豆包视觉大模型** 能力构建，目标是让开发者能够通过自然语言指令驱动移动端自动化任务。它不仅提供模型理解能力，还提供可执行的移动端操作链路，因此更适合落地为真实业务中的 Agent 系统，而不只是一个演示级别的脚本工具。

目前，Mobile Use 已在火山引擎 [veFaaS 应用中心](https://console.volcengine.com/vefaas/region:vefaas+cn-beijing/market) 提供在线体验。你可以直接访问 Demo 观察完整交互链路；如果你希望把它接入自己的业务流程，也可以通过 [一键部署](https://console.volcengine.com/vefaas/region:vefaas+cn-beijing/application/create) 快速拉起一套可运行的服务，并在此基础上继续二次开发。

## ✨ 核心能力

- **AI 驱动的移动自动化**：依赖视觉大模型识别页面内容、理解操作目标，并输出可执行的移动端动作。
- **云手机运行环境**：自动化流程运行在隔离的云手机环境中，适合需要稳定性、并发性和环境一致性的场景。
- **Skill 驱动后端**：默认后端已切换为“Skill Agent + 独立移动执行 service”的方案，旧版 MCP 链路仅保留用于兼容排查或回退。
- **Web 可视化界面**：前端提供任务输入、流式反馈和实时监控能力，方便调试和展示。
- **流式结果输出**：依赖 SSE 将中间思考、工具调用和任务进度逐步返回给前端。
- **模块化架构**：移动执行 service、Skill Agent 与 Web Frontend 分层清晰，旧版 MCP 链路也仍可独立保留作为兼容路径。

## 🏗️ 架构组成

仓库当前默认由三个主要模块构成，同时保留旧版 MCP 架构作为可选兼容链路：

```text
mobile-use/
├── mobile_use_service/   # 独立移动执行 service
├── mobile_agent_skill/   # 基于 Skill 的 Python Agent
├── web/                  # Next.js 编写的 Web 前端
├── mobile_agent/         # 旧版 Python Agent（可选回退）
└── mobile_use_mcp/       # 旧版 Go MCP Server（可选回退）
```

### 1. Mobile Use Service

`mobile_use_service/` 负责和云手机实际交互的执行能力，包括：

- 接收并执行点击、滑动、输入、截图、应用管理等移动端动作
- 对接火山引擎云手机底层能力
- 为上层 Agent 提供稳定、独立的 HTTP 能力层

### 2. Skill Agent

`mobile_agent_skill/` 负责 AI 推理与任务执行主流程，包括：

- 维护对话上下文和任务状态
- 将截图与用户输入组织为模型上下文
- 调用视觉模型产出动作决策
- 通过本地静态注册的 Skill 调用 `mobile_use_service`
- 将思考过程、工具输入输出以 SSE 形式回传

### 3. Web Frontend

`web/` 提供面向用户或开发者的交互界面，主要负责：

- 接收自然语言任务输入
- 展示 Agent 的思考和执行过程
- 管理会话、实时流和结果呈现
- 作为演示或业务接入时的基础控制台

### 4. 旧版 MCP 链路（可选）

`mobile_agent/` 与 `mobile_use_mcp/` 仍保留在仓库中，但默认不会通过 `start.sh` 启动，仅在兼容排查或回退时按需启用。

## 🛠️ 可用工具

下表是当前系统中可直接调用的移动端工具：

| Tool | 说明 |
| --- | --- |
| `take_screenshot` | 获取云手机当前屏幕截图 |
| `tap` | 在指定坐标执行点击 |
| `swipe` | 执行滑动手势 |
| `text_input` | 在屏幕中输入文本 |
| `home` | 返回主屏幕 |
| `back` | 返回上一层页面 |
| `menu` | 打开菜单界面 |
| `autoinstall_app` | 自动下载安装应用 |
| `launch_app` | 启动应用 |
| `close_app` | 关闭应用 |
| `list_apps` | 列出已安装应用 |

这些工具现在默认由 `mobile_use_service` 提供，`mobile_agent_skill` 负责决定何时、以什么参数调用它们。

## 🚦 快速开始

### 环境前置要求

在开始之前，请先确认本地具备以下运行环境：

- **Node.js** >= 20
  建议使用 [nvm](https://github.com/nvm-sh/nvm) 管理版本，便于与前端项目保持一致。
- **Python** >= 3.11
  建议使用 [uv](https://docs.astral.sh/uv/) 管理虚拟环境和依赖。
- **Go** >= 1.23
  仅当你需要显式启用旧版 `mobile_use_mcp` 链路时才需要。

> [!NOTE]
> `mobile_use_mcp` 已不再属于默认启动路径。只有在你使用 `START_LEGACY_STACK=1` 启用旧版链路时，才需要处理它的构建与运行。

### 安装步骤

1. **克隆仓库**

```bash
git clone https://github.com/volcengine/ai-app-lab.git
cd demohouse/mobile-use
```

2. **安装依赖**

```bash
sh setup.sh
```

这一步通常会同时准备 Python、Node.js 以及项目所需的基础依赖。

3. **配置环境变量**

```bash
# Copy and edit configuration files
cp mobile_agent_skill/.env.example mobile_agent_skill/.env
cp web/.env.example web/.env
# Edit configuration with your API keys and endpoints
```

执行完成后，需要根据你的环境补齐 API Key、服务地址和云资源配置。

### Skill Agent 配置

```bash
TOS_BUCKET= # 火山引擎对象存储 Bucket
TOS_REGION= # 火山引擎对象存储 Region
TOS_ENDPOINT= # 火山引擎对象存储 Endpoint

ARK_API_KEY= # 火山引擎 API Key
ARK_MODEL_ID= # 火山引擎模型 ID

ACEP_AK= # 火山引擎云手机 AK
ACEP_SK= # 火山引擎云手机 SK
ACEP_ACCOUNT_ID= # 火山引擎账号 ID
```

`mobile_agent_skill/.env.example` 中仍保留了 `MOBILE_USE_MCP_URL` 字段，用于兼容旧版链路；但默认 Skill Agent 方案并不依赖旧版 MCP Server。

这些配置决定 Agent 是否能够正确访问视觉模型、对象存储和云手机底层能力。

### Web 配置

```bash
CLOUD_AGENT_BASE_URL= # 后端服务地址，例如 http://localhost:8002/mobile-use/
```

前端通过该地址访问后端 Agent API，因此它必须指向一个可被浏览器访问到的服务入口。

4. **启动服务**

直接启动默认新版链路：

```bash
./start.sh
```

默认会启动：
- `mobile_use_service`：`8001`
- `mobile_agent_skill`：`8002`
- `web`：`8080`

如果你需要显式启用旧版 MCP/Agent 兼容链路，请使用：

```bash
START_LEGACY_STACK=1 ./start.sh
```

停止服务：

```bash
./stop.sh
```

5. **访问页面**

在浏览器中打开：

```text
http://localhost:8080?token=123
```

`token` 参数是当前示例前端中用于访问控制的简化令牌，占位值可根据你的部署实现调整。

## 📌 使用建议

- 如果你只是想理解当前默认方案，优先阅读根目录 README 与 `MIGRATION.md`。
- 如果你准备改造新版推理流程，应重点查看 `mobile_agent_skill/`。
- 如果你准备接入自己的 UI 或演示页面，应重点查看 `web/`。
- 如果你准备增加新的移动端操作能力，应从 `mobile_use_service/` 中新增或扩展执行能力。

## 🔗 相关目录

- `mobile_agent_skill/`：新版 Skill Agent 运行时与任务编排逻辑
- `mobile_use_service/`：新版移动执行能力封装
- `mobile_agent/`：旧版 Agent 运行时（兼容）
- `mobile_use_mcp/`：旧版云手机 MCP 能力封装（兼容）
- `web/`：交互式前端页面

如果你要做二次开发，建议优先从 `mobile_agent_skill/`、`mobile_use_service/` 和 `web/` 三个目录切入；旧版目录仅在兼容需求下再看。

## 新旧后端切换

本项目目前支持两套后端运行，但默认启动的是新版：
- **新版 Skill Agent（默认启动，8002 端口）**：基于静态 Skill 注册和独立 service 执行的代理。
- **旧版 Agent（可选回退，8000 端口）**：基于动态 MCP 工具的代理，仅在 `START_LEGACY_STACK=1` 时通过 `start.sh` 一并启动。

要切换 Web 前端请求的后端目标，请在 `web/.env` 文件中修改 `CLOUD_AGENT_BASE_URL`：

```env
# 使用新版 Skill Agent
CLOUD_AGENT_BASE_URL=http://localhost:8002/mobile-use/

# 如果需要回退到旧版 Agent，请改回：
# CLOUD_AGENT_BASE_URL=http://localhost:8000/mobile-use/
```
