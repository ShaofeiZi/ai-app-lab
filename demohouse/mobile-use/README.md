# Mobile Use - Solution for Mobile AI Infra to Agent 

English | [简体中文](README_zh.md)


## 🚀 Overview

[Mobile Use Product Documentation](https://www.volcengine.com/docs/6394/1583515)


**Mobile Use** is an AI Agent solution based on **Volcano Engine Cloud Phone** and **Doubao Visual Large Model** capabilities, which is able to complete automated tasks for mobile scenarios through natural language instructions.

Currently, Mobile Use has been officially launched on [veFaaS Application Center](https://console.volcengine.com/vefaas/region:vefaas+cn-beijing/market). Click to experience our Mobile Use Agent demo online through the link. If you want to develop your own Mobile Use Agent, go to [one-click deployment](https://console.volcengine.com/vefaas/region:vefaas+cn-beijing/application/create) to quickly complete the deployment process and start a journey of integrating Mobile Use Agent into your business flow.


## ✨ Features

- **AI-Powered Automation**: Accurately identify, understand and click on mobile applications and complex scenarios based on Doubao visual large model
- **Cloud Phone Integration**: Execute automated tasks in a secure, stable and low-latency Cloud Phone isolated environment
- **Skill-based Backend**: The default backend is now a skill-driven agent plus an independent mobile execution service, while the legacy MCP stack remains available for fallback debugging.
- **Web Interface**: Modern React/Next.js web interface for interaction and monitoring
- **Real-time Streaming**: SSE-based real-time communication and feedback
- **Extensible Architecture**: Modular design for easy extension and intregration into actual business flow

## 🏗️ Architecture

The project now consists of three default components, with the legacy MCP stack kept as an optional compatibility path:

```
mobile-use/
├── mobile_use_service/   # Mobile execution service
├── mobile_agent_skill/   # Skill-driven Python agent
├── web/                  # Next.js Web frontend
├── mobile_agent/         # Legacy Python agent (optional fallback)
└── mobile_use_mcp/       # Legacy Go MCP server (optional fallback)
```

### Core Components

1. **Mobile Use Service** (Python)
   - Cloud phone interaction layer
   - Mobile automation tools and APIs
   - Screenshot, tap, swipe, input, app-management and other execution abilities

2. **Skill Agent** (Python)
   - AI reasoning and decision making
   - Vision model integration
   - Static skill registry and policy control extension points
   - Task orchestration and SSE streaming output

3. **Web Frontend** (Next.js)
   - User interface and interaction
   - Real-time monitoring and feedback
   - Task management and visualization

4. **Legacy MCP Stack** (Optional)
   - `mobile_agent/` and `mobile_use_mcp/` are kept only for compatibility or fallback debugging

## 🛠️ Available Tools

| Tool | Description |
|------|-------------|
| `take_screenshot` | Capture cloud phone screen |
| `tap` | Tap at specified coordinates |
| `swipe` | Perform swipe gestures |
| `text_input` | Input text on screen |
| `home` | Go to home screen |
| `back` | Go back to previous screen |
| `menu` | Open menu |
| `autoinstall_app` | Auto-download and install apps |
| `launch_app` | Launch apps |
| `close_app` | Close apps |
| `list_apps` | List all installed apps |

## 🚦 Quick Start

### Prerequisites

- **Node.js** >= 20 (use [nvm](https://github.com/nvm-sh/nvm) for version management) 
- **Python** >= 3.11 (use [uv](https://docs.astral.sh/uv/) for dependency management)
- **Go** >= 1.23 (only needed when you explicitly enable the legacy MCP server) [install](https://go.dev/doc/install)
> [!NOTE]
> `mobile_use_mcp` is no longer part of the default startup path. It is only required when `START_LEGACY_STACK=1` is used.


### Installation

1. **Clone the repository**

```bash
git clone https://github.com/volcengine/ai-app-lab.git
cd demohouse/mobile-use
```

2. **Install dependencies**
```bash
sh setup.sh
```

3. **Configure environment**
```bash
# Copy and edit configuration files
cp mobile_agent_skill/.env.example mobile_agent_skill/.env
cp web/.env.example web/.env
# Edit configuration with your API keys and endpoints
```

### skill agent config
```bash
TOS_BUCKET= # Volcengine Object Storage bucket
TOS_REGION= # Volcengine Object Storage region
TOS_ENDPOINT= # Volcengine Object Storage endpoint

ARK_API_KEY= # Volcengine API key
ARK_MODEL_ID= # Volcengine model ID

ACEP_AK= # Volcengine cloud phone AK
ACEP_SK= # Volcengine cloud phone SK
ACEP_ACCOUNT_ID= # Volcengine accountID
```

`mobile_agent_skill/.env.example` still contains `MOBILE_USE_MCP_URL` for legacy compatibility, but the default skill-driven path does not depend on the legacy MCP server.

### web config

```bash
CLOUD_AGENT_BASE_URL= # backend service URL, e.g. http://localhost:8002/mobile-use/
```

4. **Start services**

Start the default stack:
```bash
./start.sh
```

This starts:
- `mobile_use_service` on `8001`
- `mobile_agent_skill` on `8002`
- `web` on `8080`

If you need the legacy MCP stack for fallback debugging, start it explicitly:
```bash
START_LEGACY_STACK=1 ./start.sh
```

The matching shutdown command is:
```bash
./stop.sh
```

5. **Access the application**

Open your browser and navigate to `http://localhost:8080?token=123`
