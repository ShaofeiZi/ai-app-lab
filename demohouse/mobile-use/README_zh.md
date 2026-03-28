# Mobile Use - 面向AI时代的移动端 Infra 到 Agent 全链路解决方案

[English](README.md) | 简体中文


## 🚀 产品概述

[Mobile Use 解决方案介绍文档](https://www.volcengine.com/docs/6394/1583515)

**Mobile Use** 是基于 **火山引擎云手机** 与 **豆包视觉大模型** 能力，通过自然语言指令完成面向移动端场景自动化任务的 AI Agent 解决方案。


目前，Mobile Use 已正式上线火山引擎 [函数服务 veFaaS 应用广场](https://console.volcengine.com/vefaas/region:vefaas+cn-beijing/market)，可点击跳转在线体验 Mobile Use Agent Demo；同时，如果您想要开发一款属于您自己的 Mobile Use Agent 应用，可以通过 [一键部署](https://console.volcengine.com/vefaas/region:vefaas+cn-beijing/application/create)，快速完成服务部署搭建，开启您将 Mobile Use Agent 集成在您业务流中的开发之旅。

## ✨ 核心特性

- **AI自动化**：基于豆包视觉大模型进行移动端应用与复杂场景精确识别理解与点击
- **云手机**：安全、稳定、低延时的云手机隔离环境中执行自动化任务
- **Skill驱动后端**：默认后端已切换为 Skill Agent + 独立移动执行 service，旧版 MCP 链路仅作为兼容回退保留
- **Web界面**：现代化React/Next.js网页界面用于交互和监控
- **实时流式处理**：基于SSE的实时通信和反馈
- **可扩展架构**：模块化设计，易于扩展和集成进业务实际流程

## 🏗️ 系统架构

项目当前默认由三个主要组件构成，同时保留旧版 MCP 链路作为可选兼容路径：

```
mobile-use/
├── mobile_use_service/   # 独立移动执行 service
├── mobile_agent_skill/   # Skill 驱动 Python Agent
├── web/                  # Next.js Web 前端
├── mobile_agent/         # 旧版 Python Agent（可选回退）
└── mobile_use_mcp/       # 旧版 Go MCP 服务（可选回退）
```

### 核心组件

1. **Mobile Use Service** (Python)
   - 云手机交互层
   - 移动自动化工具和 API
   - 点击、输入、截图、应用管理等能力执行

2. **Skill Agent** (Python)
   - AI推理和决策制定
   - 视觉模型集成
   - 静态 Skill 注册
   - 调用 `mobile_use_service`

3. **Web Frontend** (Next.js)
   - 用户界面和交互
   - 实时监控和反馈
   - 任务管理和可视化

4. **旧版 MCP 链路**（可选）
   - `mobile_agent/` 与 `mobile_use_mcp/` 仅在兼容排查或回退时按需启用

## 🛠️ 可用工具

| 工具 | 描述 |
|------|------|
| `take_screenshot` | 截取云手机屏幕 |
| `tap` | 在指定坐标点击 |
| `swipe` | 执行滑动手势 |
| `text_input` | 在屏幕输入文本 |
| `home` | 回到主屏幕 |
| `back` | 返回到上一页 |
| `menu` | 打开菜单 |
| `autoinstall_app` | 自动下载和安装应用 |
| `launch_app` | 启动应用 |
| `close_app` | 关闭应用 |
| `list_apps` | 列出所有已安装应用 |

## 🚦 快速开始

### 环境要求

- **Node.js** >= 20 (推荐使用 [nvm](https://github.com/nvm-sh/nvm) 进行版本管理)
- **Python** >= 3.11 (推荐使用 [uv](https://docs.astral.sh/uv/) 进行依赖管理)
- **Go** >= 1.23（仅在你显式启用旧版 MCP 服务时需要）
- **火山引擎云手机**访问权限和凭证
> [!WARNING]
> **操作系统要求：** `mobile_use_mcp` 已不再属于默认启动路径，只有在 `START_LEGACY_STACK=1` 时才需要处理它，且它仍然只支持 Linux 构建


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

3. **配置环境**
```bash
# 复制并编辑配置文件
cp mobile_agent_skill/.env.example mobile_agent_skill/.env
cp web/.env.example web/.env
# 使用你的API密钥和端点编辑配置
```

* **Skill Agent 配置说明**
```bash
TOS_BUCKET= # 火山引擎对象存储桶
TOS_REGION= # 火山引擎对象存储区域
TOS_ENDPOINT= # 火山引擎对象存储终端

ARK_API_KEY= # 火山引擎方舟平台API密钥
ARK_MODEL_ID= # 火山引擎方舟平台模型ID

ACEP_AK= # 火山引擎云手机 AK
ACEP_SK= # 火山引擎云手机 SK
ACEP_ACCOUNT_ID= # 火山引擎账号ID
```

`mobile_agent_skill/.env.example` 中仍保留 `MOBILE_USE_MCP_URL` 字段用于兼容旧版链路；默认 Skill Agent 方案并不依赖旧版 MCP Server。

* **web config**

```bash
CLOUD_AGENT_BASE_URL= # 后端服务地址，例如 http://localhost:8002/mobile-use/
```

4. **启动服务**

启动默认新版链路：
```bash
./start.sh
```

默认会启动：
- `mobile_use_service`：`8001`
- `mobile_agent_skill`：`8002`
- `web`：`8080`

如需启用旧版兼容链路：
```bash
START_LEGACY_STACK=1 ./start.sh
```

停止服务：
```bash
./stop.sh
```


5. **访问应用**

在浏览器中访问 `http://localhost:8080?token=123`
