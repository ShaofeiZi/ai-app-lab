# Mobile Use Skill Service Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a new `mobile_use_service` plus a copied `mobile_agent` variant that uses static skill definitions instead of MCP, while keeping the web frontend behavior unchanged and switching the frontend backend target through `web/.env`.

**Architecture:** Keep the current frontend and protocol stable, add a new Python service layer for Volc Mobile Use APIs, copy the existing agent into a new runtime, and replace MCP-driven dynamic tools with static skill registration, policy filtering, and service-backed handlers. Preserve the legacy path during migration so web end-to-end testing can switch by configuration instead of code changes.

**Tech Stack:** Python, FastAPI, Pydantic, existing LangGraph agent runtime, requests/http client, Volc OpenAPI integration, Next.js env-based backend proxying, pytest

---

### Task 1: Create planning directories and service scaffolding

**Files:**
- Create: `mobile_use_service/app.py`
- Create: `mobile_use_service/main.py`
- Create: `mobile_use_service/config.toml`
- Create: `mobile_use_service/pyproject.toml`
- Create: `mobile_use_service/requirements.txt`
- Create: `mobile_use_service/mobile_use_service/__init__.py`
- Create: `mobile_use_service/mobile_use_service/config/__init__.py`
- Create: `mobile_use_service/mobile_use_service/config/settings.py`
- Create: `mobile_use_service/mobile_use_service/routers/__init__.py`
- Create: `mobile_use_service/mobile_use_service/service/__init__.py`
- Create: `mobile_use_service/mobile_use_service/client/__init__.py`
- Create: `mobile_use_service/mobile_use_service/models/__init__.py`
- Create: `mobile_use_service/mobile_use_service/exception/__init__.py`

**Step 1: Write the failing smoke test**

Create `mobile_use_service/tests/test_imports.py` with:

```python
def test_service_package_imports():
    from mobile_use_service.config.settings import get_settings

    settings = get_settings()
    assert settings.app_name
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/bytedance/ai-app-lab/demohouse/mobile-use/mobile_use_service && pytest tests/test_imports.py -v`

Expected: FAIL because the package and settings module do not exist yet.

**Step 3: Write minimal scaffolding**

- Mirror the existing `mobile_agent` project layout where helpful.
- Add a minimal FastAPI app and settings loader.
- Keep configuration minimal and compatible with later expansion.

**Step 4: Run test to verify it passes**

Run: `cd /Users/bytedance/ai-app-lab/demohouse/mobile-use/mobile_use_service && pytest tests/test_imports.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add mobile_use_service
git commit -m "feat: scaffold mobile use service"
```

### Task 2: Add service-side session and result models

**Files:**
- Create: `mobile_use_service/mobile_use_service/models/session.py`
- Create: `mobile_use_service/mobile_use_service/models/result.py`
- Test: `mobile_use_service/tests/models/test_models.py`

**Step 1: Write the failing test**

Create `mobile_use_service/tests/models/test_models.py` with:

```python
from mobile_use_service.models.result import ScreenshotResult, ActionResult
from mobile_use_service.models.session import MobileUseSession


def test_screenshot_result_keeps_dimensions():
    result = ScreenshotResult(
        screenshot_url="https://example.com/a.png",
        width=720,
        height=1520,
    )
    assert result.width == 720
    assert result.height == 1520


def test_session_model_keeps_required_context():
    session = MobileUseSession(
        pod_id="pod-1",
        product_id="product-1",
        authorization_token="token",
        tos_bucket="bucket",
        tos_region="cn-beijing",
        tos_endpoint="tos-cn-beijing.volces.com",
    )
    assert session.pod_id == "pod-1"
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/bytedance/ai-app-lab/demohouse/mobile-use/mobile_use_service && pytest tests/models/test_models.py -v`

Expected: FAIL because the models do not exist yet.

**Step 3: Write minimal implementation**

- Add typed Pydantic models for session context and result payloads.
- Include result types needed by screenshot and generic actions first.
- Keep field names aligned with agent consumption.

**Step 4: Run test to verify it passes**

Run: `cd /Users/bytedance/ai-app-lab/demohouse/mobile-use/mobile_use_service && pytest tests/models/test_models.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add mobile_use_service/mobile_use_service/models mobile_use_service/tests/models/test_models.py
git commit -m "feat: add mobile use service models"
```

### Task 3: Implement Volc OpenAPI client shell

**Files:**
- Create: `mobile_use_service/mobile_use_service/client/volc_openapi.py`
- Create: `mobile_use_service/tests/client/test_volc_openapi.py`

**Step 1: Write the failing test**

Create `mobile_use_service/tests/client/test_volc_openapi.py` with:

```python
from mobile_use_service.client.volc_openapi import VolcMobileUseClient
from mobile_use_service.models.session import MobileUseSession


def test_build_common_headers_contains_json_content_type():
    client = VolcMobileUseClient(host="http://open.volcengineapi.com")
    headers = client.build_common_headers()
    assert headers["Content-Type"] == "application/json;charset=UTF-8"


def test_build_runtime_request_contains_session_fields():
    client = VolcMobileUseClient(host="http://open.volcengineapi.com")
    session = MobileUseSession(
        pod_id="pod-1",
        product_id="product-1",
        authorization_token="token",
        tos_bucket="bucket",
        tos_region="cn-beijing",
        tos_endpoint="tos-cn-beijing.volces.com",
    )
    payload = client.build_runtime_payload(session)
    assert payload["PodId"] == "pod-1"
    assert payload["ProductId"] == "product-1"
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/bytedance/ai-app-lab/demohouse/mobile-use/mobile_use_service && pytest tests/client/test_volc_openapi.py -v`

Expected: FAIL because the client is not implemented.

**Step 3: Write minimal implementation**

- Add a client class that owns host/config/header construction.
- Implement pure helper methods first, without real network requests.
- Keep transport logic injectable for later mocking.

**Step 4: Run test to verify it passes**

Run: `cd /Users/bytedance/ai-app-lab/demohouse/mobile-use/mobile_use_service && pytest tests/client/test_volc_openapi.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add mobile_use_service/mobile_use_service/client/volc_openapi.py mobile_use_service/tests/client/test_volc_openapi.py
git commit -m "feat: add volc mobile use client shell"
```

### Task 4: Implement screenshot result adaptation

**Files:**
- Modify: `mobile_use_service/mobile_use_service/client/volc_openapi.py`
- Create: `mobile_use_service/mobile_use_service/service/mobile_use_service.py`
- Create: `mobile_use_service/tests/service/test_screenshot_result.py`

**Step 1: Write the failing test**

Create `mobile_use_service/tests/service/test_screenshot_result.py` with:

```python
from mobile_use_service.models.result import ScreenshotResult
from mobile_use_service.service.mobile_use_service import MobileUseService


class FakeClient:
    def get_screenshot(self, session):
        return {
            "screenshot_url": "https://example.com/image.png",
            "width": 720,
            "height": 1520,
        }


def test_take_screenshot_returns_compatible_result():
    service = MobileUseService(client=FakeClient())
    result = service.take_screenshot(session=object())
    assert isinstance(result, ScreenshotResult)
    assert result.screenshot_url.endswith(".png")
    assert result.width == 720
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/bytedance/ai-app-lab/demohouse/mobile-use/mobile_use_service && pytest tests/service/test_screenshot_result.py -v`

Expected: FAIL because `MobileUseService.take_screenshot` does not exist yet.

**Step 3: Write minimal implementation**

- Add `MobileUseService`.
- Implement `take_screenshot(session)` as the first supported action.
- Return a typed result that can be converted into the legacy JSON string shape later.

**Step 4: Run test to verify it passes**

Run: `cd /Users/bytedance/ai-app-lab/demohouse/mobile-use/mobile_use_service && pytest tests/service/test_screenshot_result.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add mobile_use_service/mobile_use_service/service/mobile_use_service.py mobile_use_service/tests/service/test_screenshot_result.py
git commit -m "feat: add screenshot service adaptation"
```

### Task 5: Add action execution methods to the new service

**Files:**
- Modify: `mobile_use_service/mobile_use_service/service/mobile_use_service.py`
- Create: `mobile_use_service/tests/service/test_actions.py`

**Step 1: Write the failing test**

Create `mobile_use_service/tests/service/test_actions.py` with:

```python
from mobile_use_service.service.mobile_use_service import MobileUseService


class FakeClient:
    def run_action(self, session, action_name, payload):
        return {"action_name": action_name, "payload": payload, "success": True}


def test_tap_calls_action_client():
    service = MobileUseService(client=FakeClient())
    result = service.tap(session=object(), x=10, y=20)
    assert result.success is True
    assert result.payload["x"] == 10


def test_swipe_calls_action_client():
    service = MobileUseService(client=FakeClient())
    result = service.swipe(session=object(), from_x=1, from_y=2, to_x=3, to_y=4)
    assert result.payload["to_y"] == 4
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/bytedance/ai-app-lab/demohouse/mobile-use/mobile_use_service && pytest tests/service/test_actions.py -v`

Expected: FAIL because action methods are missing.

**Step 3: Write minimal implementation**

- Implement:
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
- Keep return objects consistent across methods.

**Step 4: Run test to verify it passes**

Run: `cd /Users/bytedance/ai-app-lab/demohouse/mobile-use/mobile_use_service && pytest tests/service/test_actions.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add mobile_use_service/mobile_use_service/service/mobile_use_service.py mobile_use_service/tests/service/test_actions.py
git commit -m "feat: add mobile use action methods"
```

### Task 6: Expose service HTTP routes for agent integration

**Files:**
- Create: `mobile_use_service/mobile_use_service/routers/mobile_use.py`
- Modify: `mobile_use_service/mobile_use_service/routers/__init__.py`
- Modify: `mobile_use_service/app.py`
- Test: `mobile_use_service/tests/routers/test_mobile_use_router.py`

**Step 1: Write the failing test**

Create `mobile_use_service/tests/routers/test_mobile_use_router.py` with:

```python
from fastapi.testclient import TestClient

from app import app


def test_health_or_basic_action_route_exists():
    client = TestClient(app)
    response = client.post("/mobile-use/api/v1/tools/tap", json={"x": 1, "y": 2})
    assert response.status_code != 404
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/bytedance/ai-app-lab/demohouse/mobile-use/mobile_use_service && pytest tests/routers/test_mobile_use_router.py -v`

Expected: FAIL because the route is not registered.

**Step 3: Write minimal implementation**

- Register a router with a stable prefix.
- Add typed request bodies for screenshot and action routes.
- Return predictable JSON payloads for agent-side consumption.

**Step 4: Run test to verify it passes**

Run: `cd /Users/bytedance/ai-app-lab/demohouse/mobile-use/mobile_use_service && pytest tests/routers/test_mobile_use_router.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add mobile_use_service/app.py mobile_use_service/mobile_use_service/routers mobile_use_service/tests/routers/test_mobile_use_router.py
git commit -m "feat: add mobile use service routes"
```

### Task 7: Copy `mobile_agent` into a new skill-driven runtime

**Files:**
- Create: `mobile_agent_skill/` by copying `/Users/bytedance/ai-app-lab/demohouse/mobile-use/mobile_agent/`
- Modify: `mobile_agent_skill/pyproject.toml`
- Modify: `mobile_agent_skill/requirements.txt`
- Modify: `mobile_agent_skill/config.toml`
- Test: `mobile_agent_skill/tests/test_imports.py`

**Step 1: Write the failing test**

Create `mobile_agent_skill/tests/test_imports.py` with:

```python
def test_skill_agent_package_imports():
    from mobile_agent.agent.mobile_use_agent import MobileUseAgent

    assert MobileUseAgent.name
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/bytedance/ai-app-lab/demohouse/mobile-use/mobile_agent_skill && pytest tests/test_imports.py -v`

Expected: FAIL because the copied package or imports are not adjusted yet.

**Step 3: Write minimal implementation**

- Copy the existing package.
- Adjust project metadata and config paths for the new runtime.
- Keep imports consistent so the new runtime can start independently.

**Step 4: Run test to verify it passes**

Run: `cd /Users/bytedance/ai-app-lab/demohouse/mobile-use/mobile_agent_skill && pytest tests/test_imports.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add mobile_agent_skill
git commit -m "feat: copy mobile agent into skill runtime"
```

### Task 8: Add static skill definitions and registry

**Files:**
- Create: `mobile_agent_skill/mobile_agent/agent/skills/definitions.py`
- Create: `mobile_agent_skill/mobile_agent/agent/skills/registry.py`
- Create: `mobile_agent_skill/mobile_agent/agent/skills/policy.py`
- Create: `mobile_agent_skill/tests/skills/test_registry.py`

**Step 1: Write the failing test**

Create `mobile_agent_skill/tests/skills/test_registry.py` with:

```python
from mobile_agent.agent.skills.registry import SkillRegistry


def test_registry_contains_core_mobile_skills():
    registry = SkillRegistry()
    skills = registry.list_all()
    names = {skill.name for skill in skills}
    assert "mobile:tap" in names
    assert "mobile:take_screenshot" in names
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/bytedance/ai-app-lab/demohouse/mobile-use/mobile_agent_skill && pytest tests/skills/test_registry.py -v`

Expected: FAIL because the skill registry does not exist.

**Step 3: Write minimal implementation**

- Define the static skill set mirroring the old MCP-exposed tools.
- Include fields for:
  - name
  - description
  - parameters schema
  - handler
  - scopes
  - enabled_by_default
  - risk_level
- Implement a registry that returns the candidate skill list.

**Step 4: Run test to verify it passes**

Run: `cd /Users/bytedance/ai-app-lab/demohouse/mobile-use/mobile_agent_skill && pytest tests/skills/test_registry.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add mobile_agent_skill/mobile_agent/agent/skills mobile_agent_skill/tests/skills/test_registry.py
git commit -m "feat: add static mobile skill registry"
```

### Task 9: Add skill policy filtering for future authorization control

**Files:**
- Modify: `mobile_agent_skill/mobile_agent/agent/skills/policy.py`
- Create: `mobile_agent_skill/tests/skills/test_policy.py`

**Step 1: Write the failing test**

Create `mobile_agent_skill/tests/skills/test_policy.py` with:

```python
from mobile_agent.agent.skills.policy import SkillPolicyResolver
from mobile_agent.agent.skills.registry import SkillRegistry


def test_policy_can_filter_by_allowlist():
    resolver = SkillPolicyResolver(allowlist={"mobile:tap"})
    skills = SkillRegistry().list_all()
    filtered = resolver.filter(skills, context={})
    assert [skill.name for skill in filtered] == ["mobile:tap"]
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/bytedance/ai-app-lab/demohouse/mobile-use/mobile_agent_skill && pytest tests/skills/test_policy.py -v`

Expected: FAIL because filtering behavior is not implemented.

**Step 3: Write minimal implementation**

- Add allowlist/denylist support.
- Keep the context argument even if first version uses only config.
- Return a filtered skill list without mutating the registry source.

**Step 4: Run test to verify it passes**

Run: `cd /Users/bytedance/ai-app-lab/demohouse/mobile-use/mobile_agent_skill && pytest tests/skills/test_policy.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add mobile_agent_skill/mobile_agent/agent/skills/policy.py mobile_agent_skill/tests/skills/test_policy.py
git commit -m "feat: add skill policy filtering"
```

### Task 10: Add skill executor and handlers backed by the new service

**Files:**
- Create: `mobile_agent_skill/mobile_agent/agent/skills/executor.py`
- Create: `mobile_agent_skill/mobile_agent/agent/skills/handlers/__init__.py`
- Create: `mobile_agent_skill/mobile_agent/agent/skills/handlers/mobile.py`
- Test: `mobile_agent_skill/tests/skills/test_executor.py`

**Step 1: Write the failing test**

Create `mobile_agent_skill/tests/skills/test_executor.py` with:

```python
from mobile_agent.agent.skills.executor import SkillExecutor


class FakeService:
    def tap(self, session, x, y):
        return {"success": True, "x": x, "y": y}


def test_executor_dispatches_to_handler():
    executor = SkillExecutor(service=FakeService())
    result = executor.execute("mobile:tap", {"x": 3, "y": 4}, context={"session": object()})
    assert result["success"] is True
    assert result["x"] == 3
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/bytedance/ai-app-lab/demohouse/mobile-use/mobile_agent_skill && pytest tests/skills/test_executor.py -v`

Expected: FAIL because the executor does not exist.

**Step 3: Write minimal implementation**

- Add a dispatcher that maps skill names to handlers.
- Pass session context through to the new service.
- Validate authorization again before execution.

**Step 4: Run test to verify it passes**

Run: `cd /Users/bytedance/ai-app-lab/demohouse/mobile-use/mobile_agent_skill && pytest tests/skills/test_executor.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add mobile_agent_skill/mobile_agent/agent/skills/executor.py mobile_agent_skill/mobile_agent/agent/skills/handlers mobile_agent_skill/tests/skills/test_executor.py
git commit -m "feat: add skill executor backed by mobile use service"
```

### Task 11: Replace MCP-driven tool loading in the new agent

**Files:**
- Modify: `mobile_agent_skill/mobile_agent/agent/mobile_use_agent.py`
- Modify: `mobile_agent_skill/mobile_agent/agent/tools/tools.py`
- Modify: `mobile_agent_skill/mobile_agent/agent/mobile/client.py`
- Create: `mobile_agent_skill/tests/agent/test_skill_agent_tools.py`

**Step 1: Write the failing test**

Create `mobile_agent_skill/tests/agent/test_skill_agent_tools.py` with:

```python
import pytest

from mobile_agent.agent.tools.tools import Tools


@pytest.mark.asyncio
async def test_tools_are_built_from_skill_registry_not_mcp():
    tools = await Tools.from_skill_registry()
    names = {tool.name for tool in tools.prompt_tools()}
    assert "mobile:tap" in names
    assert "finished" in names
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/bytedance/ai-app-lab/demohouse/mobile-use/mobile_agent_skill && pytest tests/agent/test_skill_agent_tools.py -v`

Expected: FAIL because `from_skill_registry()` does not exist.

**Step 3: Write minimal implementation**

- Add a `Tools.from_skill_registry(...)` constructor.
- Keep the special tools:
  - `finished`
  - `wait`
  - `call_user`
  - `error`
- Build runtime tools from static skill definitions instead of MCP sessions.

**Step 4: Run test to verify it passes**

Run: `cd /Users/bytedance/ai-app-lab/demohouse/mobile-use/mobile_agent_skill && pytest tests/agent/test_skill_agent_tools.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add mobile_agent_skill/mobile_agent/agent/mobile_use_agent.py mobile_agent_skill/mobile_agent/agent/tools/tools.py mobile_agent_skill/mobile_agent/agent/mobile/client.py mobile_agent_skill/tests/agent/test_skill_agent_tools.py
git commit -m "feat: replace mcp tool loading with skill registry"
```

### Task 12: Add a service-backed screenshot client in the new agent

**Files:**
- Modify: `mobile_agent_skill/mobile_agent/agent/mobile/client.py`
- Create: `mobile_agent_skill/tests/agent/test_mobile_client.py`

**Step 1: Write the failing test**

Create `mobile_agent_skill/tests/agent/test_mobile_client.py` with:

```python
import pytest

from mobile_agent.agent.mobile.client import Mobile


class FakeServiceClient:
    async def take_screenshot(self):
        return {
            "result": {
                "screenshot_url": "https://example.com/shot.png",
                "width": 720,
                "height": 1520,
            }
        }


@pytest.mark.asyncio
async def test_take_screenshot_updates_dimensions():
    mobile = Mobile(service_client=FakeServiceClient())
    result = await mobile.take_screenshot()
    assert result["screenshot_dimensions"] == (720, 1520)
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/bytedance/ai-app-lab/demohouse/mobile-use/mobile_agent_skill && pytest tests/agent/test_mobile_client.py -v`

Expected: FAIL because the mobile client still depends on MCP.

**Step 3: Write minimal implementation**

- Remove MCP session setup from the copied mobile client.
- Call the new service client for screenshots.
- Preserve the legacy result shape used by the rest of the graph.

**Step 4: Run test to verify it passes**

Run: `cd /Users/bytedance/ai-app-lab/demohouse/mobile-use/mobile_agent_skill && pytest tests/agent/test_mobile_client.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add mobile_agent_skill/mobile_agent/agent/mobile/client.py mobile_agent_skill/tests/agent/test_mobile_client.py
git commit -m "feat: add service-backed screenshot client"
```

### Task 13: Keep action parsing compatible with the new skill names

**Files:**
- Modify: `mobile_agent_skill/mobile_agent/agent/mobile/doubao_action_parser.py`
- Create: `mobile_agent_skill/tests/agent/test_action_parser.py`

**Step 1: Write the failing test**

Create `mobile_agent_skill/tests/agent/test_action_parser.py` with:

```python
from mobile_agent.agent.mobile.doubao_action_parser import DoubaoActionSpaceParser


def test_click_maps_to_skill_tap_name():
    parser = DoubaoActionSpaceParser(phone_width=720, phone_height=1520)
    result = parser.to_mcp_tool_call('click(start_box="<bbox>10 10 20 20</bbox>")')
    assert result["name"] == "mobile:tap"
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/bytedance/ai-app-lab/demohouse/mobile-use/mobile_agent_skill && pytest tests/agent/test_action_parser.py -v`

Expected: FAIL if copied code still points at old naming or import assumptions.

**Step 3: Write minimal implementation**

- Keep the parser API stable for the graph layer.
- Ensure returned names match the new static skill registry names.
- Preserve existing coordinate normalization logic.

**Step 4: Run test to verify it passes**

Run: `cd /Users/bytedance/ai-app-lab/demohouse/mobile-use/mobile_agent_skill && pytest tests/agent/test_action_parser.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add mobile_agent_skill/mobile_agent/agent/mobile/doubao_action_parser.py mobile_agent_skill/tests/agent/test_action_parser.py
git commit -m "feat: align action parser with static skills"
```

### Task 14: Expose compatible `/stream` and `/cancel` routes in the copied agent

**Files:**
- Modify: `mobile_agent_skill/mobile_agent/routers/agent.py`
- Modify: `mobile_agent_skill/mobile_agent/routers/base.py`
- Modify: `mobile_agent_skill/app.py`
- Test: `mobile_agent_skill/tests/routers/test_agent_routes.py`

**Step 1: Write the failing test**

Create `mobile_agent_skill/tests/routers/test_agent_routes.py` with:

```python
from fastapi.testclient import TestClient

from app import app


def test_stream_route_exists():
    client = TestClient(app)
    response = client.post(
        "/mobile-use/api/v1/agent/stream",
        json={"message": "hello", "thread_id": "t-1", "is_stream": True},
    )
    assert response.status_code != 404
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/bytedance/ai-app-lab/demohouse/mobile-use/mobile_agent_skill && pytest tests/routers/test_agent_routes.py -v`

Expected: FAIL if copied app is not wired correctly.

**Step 3: Write minimal implementation**

- Ensure the copied agent starts independently.
- Keep route shape compatible with the old backend.
- Internally instantiate the skill-driven agent implementation.

**Step 4: Run test to verify it passes**

Run: `cd /Users/bytedance/ai-app-lab/demohouse/mobile-use/mobile_agent_skill && pytest tests/routers/test_agent_routes.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add mobile_agent_skill/mobile_agent/routers mobile_agent_skill/app.py mobile_agent_skill/tests/routers/test_agent_routes.py
git commit -m "feat: add compatible routes for skill agent"
```

### Task 15: Update startup and build scripts to include the new runtime

**Files:**
- Modify: `start.sh`
- Modify: `stop.sh`
- Modify: `restart.sh`
- Modify: `build.sh`
- Test: `docs/plans/2026-03-28-mobile-use-skill-service.md`

**Step 1: Write the failing verification step**

Document the exact commands that should fail before implementation:

```bash
cd /Users/bytedance/ai-app-lab/demohouse/mobile-use
./start.sh
```

Expected: the new service/runtime are not started yet because the scripts do not know them.

**Step 2: Run the verification command**

Run: `cd /Users/bytedance/ai-app-lab/demohouse/mobile-use && ./start.sh`

Expected: the old runtime starts but the new service/runtime are absent.

**Step 3: Write minimal implementation**

- Add start/stop support for:
  - new `mobile_use_service`
  - new copied `mobile_agent`
- Preserve legacy commands.
- Keep ports configurable and explicit.

**Step 4: Run the verification command again**

Run: `cd /Users/bytedance/ai-app-lab/demohouse/mobile-use && ./start.sh`

Expected: both new backends start cleanly without breaking legacy start behavior.

**Step 5: Commit**

```bash
git add start.sh stop.sh restart.sh build.sh
git commit -m "feat: add startup support for skill service runtime"
```

### Task 16: Switch web backend target through `.env`

**Files:**
- Create or Modify: `web/.env`
- Modify: `web/README.md`
- Modify: `web/README.zh-CN.md`
- Modify: `README.md`
- Modify: `README.zh-CN.md`

**Step 1: Write the failing verification step**

Document the command that currently points to the old backend target:

```bash
cd /Users/bytedance/ai-app-lab/demohouse/mobile-use/web
rg -n "CLOUD_AGENT_BASE_URL|NEXT_PUBLIC" .env* src
```

Expected: the web target is still pointing to the current backend or no local `.env` exists.

**Step 2: Run the verification command**

Run: `cd /Users/bytedance/ai-app-lab/demohouse/mobile-use/web && rg -n "CLOUD_AGENT_BASE_URL|NEXT_PUBLIC" .env* src`

Expected: confirms the current target before modification.

**Step 3: Write minimal implementation**

- Add or update `web/.env` so the frontend proxy points to the copied new agent backend.
- Document how to switch back to legacy.

**Step 4: Run the verification command again**

Run: `cd /Users/bytedance/ai-app-lab/demohouse/mobile-use/web && rg -n "CLOUD_AGENT_BASE_URL|NEXT_PUBLIC" .env* README*`

Expected: the new target and switch instructions are visible.

**Step 5: Commit**

```bash
git add web/.env web/README.md web/README.zh-CN.md README.md README.zh-CN.md
git commit -m "docs: add web backend switching for skill runtime"
```

### Task 17: Run service and agent test suites

**Files:**
- Test: `mobile_use_service/tests/`
- Test: `mobile_agent_skill/tests/`

**Step 1: Write the verification command list**

```bash
cd /Users/bytedance/ai-app-lab/demohouse/mobile-use/mobile_use_service && pytest -v
cd /Users/bytedance/ai-app-lab/demohouse/mobile-use/mobile_agent_skill && pytest -v
```

**Step 2: Run tests and capture failures**

Run the exact commands above.

Expected: any missing imports, route errors, or schema mismatches are visible.

**Step 3: Write minimal fixes**

- Fix only the failing tests.
- Do not widen scope unless the failure blocks the migration.

**Step 4: Run tests again**

Run the same `pytest -v` commands.

Expected: PASS for both projects.

**Step 5: Commit**

```bash
git add mobile_use_service mobile_agent_skill
git commit -m "test: make skill runtime and service test suites pass"
```

### Task 18: Run web end-to-end联调 using the existing page

**Files:**
- Verify: `web/src/app/api/agent/stream/route.ts`
- Verify: `web/src/app/api/agent/cancel/route.ts`
- Verify: `web/src/hooks/useCloudAgent.ts`

**Step 1: Write the verification checklist**

Check:

- Session can be created.
- Stream starts successfully.
- Screenshot messages render.
- A simple action runs.
- Cancel works.
- Error states still surface in UI.

**Step 2: Run the backend services**

Run:

```bash
cd /Users/bytedance/ai-app-lab/demohouse/mobile-use
./start.sh
```

Expected: new service and new agent are both running.

**Step 3: Run the web app**

Run:

```bash
cd /Users/bytedance/ai-app-lab/demohouse/mobile-use/web
npm run dev
```

Expected: web app starts with the `.env` target pointing to the new backend.

**Step 4: Verify in browser**

- Open the existing web UI.
- Start a chat task.
- Confirm SSE messages continue to stream.
- Confirm screenshot and action steps appear.
- Confirm cancel stops execution.

**Step 5: Commit**

```bash
git add web
git commit -m "test: verify web integration with skill runtime"
```

### Task 19: Document fallback and migration notes

**Files:**
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `PROJECT_EXPLAINED.zh-CN.md`

**Step 1: Write the failing documentation checklist**

Missing items before the doc update:

- new service purpose
- new copied agent purpose
- web `.env` switch instructions
- rollback path to legacy runtime

**Step 2: Verify the docs are missing those items**

Run:

```bash
cd /Users/bytedance/ai-app-lab/demohouse/mobile-use
rg -n "mobile_use_service|mobile_agent_skill|web/.env|rollback|回退" README* PROJECT_EXPLAINED.zh-CN.md
```

Expected: little or no coverage of the new runtime.

**Step 3: Write minimal implementation**

- Document the new backend topology.
- Document how web switches between old and new backends.
- Document how to revert to the legacy service.

**Step 4: Verify the docs include the new items**

Run the same `rg` command again.

Expected: all new migration terms appear in the docs.

**Step 5: Commit**

```bash
git add README.md README.zh-CN.md PROJECT_EXPLAINED.zh-CN.md
git commit -m "docs: add skill runtime migration notes"
```
