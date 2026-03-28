# Mobile Agent - 移动端 AI 自动化核心服务

[English](README.md) | 简体中文

## 🏗️ 模块定位

`mobile_agent/` 是整个 Mobile Use 方案中的 Agent 核心。它负责组织对话上下文、调用视觉模型、决定下一步动作，并通过 MCP 工具把模型决策变成真实的移动端操作。

如果把整个系统拆开理解：

- `mobile_use_mcp/` 负责“能做什么”
- `mobile_agent/` 负责“下一步该做什么”
- `web/` 负责“如何把过程展示给用户”

因此，这个模块更接近任务编排和执行引擎，而不是单纯的 HTTP 服务壳子。

## 📁 目录结构

```text
mobile_agent/
├── mobile_agent/
│   ├── agent/              # Agent 主逻辑
│   │   ├── mobile_use_agent.py    # 主代理类
│   │   ├── graph/          # LangGraph 工作流定义
│   │   ├── tools/          # 工具管理与执行适配
│   │   ├── prompt/         # 提示词模板
│   │   ├── memory/         # 上下文与记忆管理
│   │   ├── mobile/         # 移动设备交互封装
│   │   ├── llm/            # 大模型调用与流式输出封装
│   │   ├── cost/           # 计费与步数统计
│   │   ├── infra/          # 基础设施与通用模型
│   │   └── utils/          # 工具函数
│   ├── config/             # 配置管理
│   ├── routers/            # API 路由
│   ├── service/            # 业务服务
│   ├── middleware/         # 中间件
│   └── exception/          # 异常定义
├── config.toml             # 配置文件
├── requirements.txt        # 依赖声明
├── pyproject.toml          # Python 项目配置
└── main.py                 # 应用入口
```

## 🚀 快速开始

### 环境要求

启动该模块前，至少需要准备以下条件：

- **Python** >= 3.11
- **uv**
  推荐使用它来统一虚拟环境和依赖管理流程。
- **Doubao 模型 API Key**
  Agent 需要访问视觉模型完成理解与决策。
- **云手机服务访问权限**
  包括访问云手机及其配套资源所需的鉴权配置。

### 安装步骤

1. **安装依赖**

```bash
cd mobile_agent
uv sync
```

`uv sync` 会按照项目配置同步虚拟环境中的依赖，适合本地开发和 CI。

2. **配置环境**

```bash
# Edit configuration file, fill in your API keys and service endpoints
cp .env.example .env
```

复制完成后，请补齐真实的 API Key、对象存储信息和 MCP 地址。

3. **启动服务**

```bash
# Development mode
uv run main.py
```

这会以开发模式启动 Agent 服务。若后续需要以容器或函数服务方式运行，应根据部署目标再补充对应的启动方式。

## ⚙️ 配置项说明

```bash
MOBILE_USE_MCP_URL= # MCP_SSE 服务地址，例如 http://xxxx.com/sse

TOS_BUCKET= # 火山引擎对象存储 Bucket
TOS_REGION= # 火山引擎对象存储 Region
TOS_ENDPOINT= # 火山引擎对象存储 Endpoint

ARK_API_KEY= # 火山引擎 API Key
ARK_MODEL_ID= # 火山引擎模型 ID

ACEP_AK= # 火山引擎 AK
ACEP_SK= # 火山引擎 SK
ACEP_ACCOUNT_ID= # 火山引擎账号 ID
```

补充说明：

- `MOBILE_USE_MCP_URL` 决定 Agent 把工具调用发往哪个 MCP 服务实例。
- `TOS_*` 配置通常用于截图等对象数据的存储与访问。
- `ARK_*` 配置决定模型调用的鉴权与目标模型。
- `ACEP_*` 配置则与云手机实例能力相关。

## 🛠️ 通过 MCP 暴露的核心工具

Mobile Agent 会通过 Mobile Use MCP 调用以下移动端操作能力：

| Tool Name | 作用 | 参数 |
| --- | --- | --- |
| `mobile:screenshot` | 获取设备屏幕截图 | - |
| `mobile:tap` | 点击指定屏幕坐标 | `x, y` |
| `mobile:swipe` | 执行滑动手势 | `from_x, from_y, to_x, to_y` |
| `mobile:type` | 输入文本 | `text` |
| `mobile:home` | 返回桌面 | - |
| `mobile:back` | 返回上一层 | - |
| `mobile:close_app` | 关闭应用 | `package_name` |
| `mobile:launch_app` | 启动应用 | `package_name` |
| `mobile:list_apps` | 列出已安装应用 | - |

## 📌 开发阅读建议

- 如果你要理解 Agent 如何循环执行，优先查看 `mobile_agent/agent/graph/`。
- 如果你要改提示词或模型接入，重点看 `mobile_agent/agent/prompt/` 与 `mobile_agent/agent/llm/`。
- 如果你要增加工具或改变调用映射，重点看 `mobile_agent/agent/tools/`。
- 如果你要改 API 出入口，重点看 `routers/` 和 `app.py`。

## ✅ 适合在哪些场景使用

这个模块适合以下工作：

- 构建移动端任务型 Agent
- 接入多步推理和工具调用工作流
- 把视觉理解与移动操作串联为统一执行链路
- 为 Web 前端或其他上层系统提供可流式消费的 Agent 服务
