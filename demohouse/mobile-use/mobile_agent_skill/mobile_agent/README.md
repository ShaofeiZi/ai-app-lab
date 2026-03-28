# Mobile Agent - AI Mobile Device Automation Core

English | [简体中文](README_zh.md)


## 🏗️ Architecture Design

```
mobile_agent/
├── mobile_agent/
│   ├── agent/              # Core agent logic
│   │   ├── mobile_use_agent.py    # Main agent class
│   │   ├── graph/          # LangGraph workflows
│   │   ├── tools/          # Tool management
│   │   ├── prompt/         # Prompt templates
│   │   ├── memory/         # Memory management
│   │   ├── mobile/         # Mobile device interaction
│   │   ├── llm/           # Large language model interface
│   │   ├── cost/          # Cost calculation
│   │   ├── infra/         # Infrastructure
│   │   └── utils/         # Utility functions
│   ├── config/            # Configuration management
│   ├── routers/           # API routes
│   ├── service/           # Business services
│   ├── middleware/        # Middleware
│   └── exception/         # Exception handling
├── config.toml           # Configuration file
├── requirements.txt      # Dependency management
├── pyproject.toml       # Project configuration
└── main.py             # Application entry point
```

## 🚀 Quick Start

### Requirements

- **Python** >= 3.11
- **uv** (Recommended Python package manager)
- Doubao Model API key
- Cloud phone service access permissions

### Installation Steps

1. **Install dependencies**
```bash
cd mobile_agent
uv sync
```

2. **Configure environment**
```bash
# Edit configuration file, fill in your API keys and service endpoints
cp .env.example .env
```

3. **Start service**
```bash
# Development mode
uv run main.py
```

### Configuration

```bash
MOBILE_USE_MCP_URL= # MCP_SSE service URL http://xxxx.com/sse

TOS_BUCKET= # Volcengine Object Storage bucket
TOS_REGION= # Volcengine Object Storage region
TOS_ENDPOINT= # Volcengine Object Storage endpoint

ARK_API_KEY= # Volcengine API key
ARK_MODEL_ID= # Volcengine model ID

ACEP_AK= # Volcengine  AK
ACEP_SK= # Volcengine  SK
ACEP_ACCOUNT_ID= # Volcengine  account ID
```

## 🛠️ Core Components

Mobile device operations supported through Mobile Use MCP:

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `mobile:screenshot` | Capture device screen | - |
| `mobile:tap` | Tap screen coordinates | `x, y` |
| `mobile:swipe` | Swipe gesture | `from_x, from_y, to_x, to_y` |
| `mobile:type` | Text input | `text` |
| `mobile:home` | Return to home screen | - |
| `mobile:back` | Go back | - |
| `mobile:close_app` | Close application | `package_name` |
| `mobile:launch_app` | Launch application | `package_name` |
| `mobile:list_apps` | List installed applications | - |

