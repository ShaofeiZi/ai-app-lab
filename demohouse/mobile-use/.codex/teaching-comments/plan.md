# Teaching Comment Plan

| source_path | target_path | language | category | status | notes |
| --- | --- | --- | --- | --- | --- |
| mobile_agent/app.py | mobile_agent/app.py | py | code-comment | done | explain FastAPI app assembly and middleware registration flow |
| mobile_agent/main.py | mobile_agent/main.py | py | code-comment | done | explain process startup and uvicorn boot flow |
| mobile_agent/mobile_agent/__init__.py | mobile_agent/mobile_agent/__init__.py | py | code-comment | skipped | package marker with almost no logic |
| mobile_agent/mobile_agent/agent/__init__.py | mobile_agent/mobile_agent/agent/__init__.py | py | code-comment | skipped | package marker with almost no logic |
| mobile_agent/mobile_agent/agent/cost/__init__.py | mobile_agent/mobile_agent/agent/cost/__init__.py | py | code-comment | skipped | package marker with almost no logic |
| mobile_agent/mobile_agent/agent/cost/calculator.py | mobile_agent/mobile_agent/agent/cost/calculator.py | py | code-comment | skipped | utility logic is peripheral to first-pass beginner reading path |
| mobile_agent/mobile_agent/agent/graph/__init__.py | mobile_agent/mobile_agent/agent/graph/__init__.py | py | code-comment | skipped | package marker with almost no logic |
| mobile_agent/mobile_agent/agent/graph/builder.py | mobile_agent/mobile_agent/agent/graph/builder.py | py | code-comment | done | explain how LangGraph nodes and edges form the agent loop |
| mobile_agent/mobile_agent/agent/graph/context.py | mobile_agent/mobile_agent/agent/graph/context.py | py | code-comment | done | explain thread scoped object storage for graph execution |
| mobile_agent/mobile_agent/agent/graph/nodes.py | mobile_agent/mobile_agent/agent/graph/nodes.py | py | code-comment | done | explain prepare/model/tool validation/tool execution flow in detail |
| mobile_agent/mobile_agent/agent/graph/sse_output.py | mobile_agent/mobile_agent/agent/graph/sse_output.py | py | code-comment | done | explain how backend events are shaped for the frontend |
| mobile_agent/mobile_agent/agent/graph/state.py | mobile_agent/mobile_agent/agent/graph/state.py | py | code-comment | done | explain graph state fields and why they exist |
| mobile_agent/mobile_agent/agent/infra/__init__.py | mobile_agent/mobile_agent/agent/infra/__init__.py | py | code-comment | skipped | package marker with almost no logic |
| mobile_agent/mobile_agent/agent/infra/logger.py | mobile_agent/mobile_agent/agent/infra/logger.py | py | code-comment | skipped | helper wrapper is small and not central to runtime understanding |
| mobile_agent/mobile_agent/agent/infra/message_web.py | mobile_agent/mobile_agent/agent/infra/message_web.py | py | code-comment | done | explain SSE/web message model fields and how frontend event types map to backend output |
| mobile_agent/mobile_agent/agent/infra/model.py | mobile_agent/mobile_agent/agent/infra/model.py | py | code-comment | skipped | thin data model helper with low standalone teaching value |
| mobile_agent/mobile_agent/agent/llm/__init__.py | mobile_agent/mobile_agent/agent/llm/__init__.py | py | code-comment | skipped | package marker with almost no logic |
| mobile_agent/mobile_agent/agent/llm/doubao.py | mobile_agent/mobile_agent/agent/llm/doubao.py | py | code-comment | done | explain LLM request and streamed/non-streamed output handling |
| mobile_agent/mobile_agent/agent/llm/stream_pipe.py | mobile_agent/mobile_agent/agent/llm/stream_pipe.py | py | code-comment | done | explain streamed summary/action parsing and why incremental parsing is needed |
| mobile_agent/mobile_agent/agent/memory/__init__.py | mobile_agent/mobile_agent/agent/memory/__init__.py | py | code-comment | skipped | package marker with almost no logic |
| mobile_agent/mobile_agent/agent/memory/context_manager.py | mobile_agent/mobile_agent/agent/memory/context_manager.py | py | code-comment | done | explain how conversation history is built and trimmed |
| mobile_agent/mobile_agent/agent/memory/messages.py | mobile_agent/mobile_agent/agent/memory/messages.py | py | code-comment | done | explain conversation message containers and why history is wrapped in typed models |
| mobile_agent/mobile_agent/agent/memory/saver.py | mobile_agent/mobile_agent/agent/memory/saver.py | py | code-comment | skipped | tiny checkpointer glue file |
| mobile_agent/mobile_agent/agent/mobile/__init__.py | mobile_agent/mobile_agent/agent/mobile/__init__.py | py | code-comment | skipped | package marker with almost no logic |
| mobile_agent/mobile_agent/agent/mobile/client.py | mobile_agent/mobile_agent/agent/mobile/client.py | py | code-comment | done | explain MCP mobile client lifecycle, retries, and screenshot or size helper flow |
| mobile_agent/mobile_agent/agent/mobile/doubao_action_parser.py | mobile_agent/mobile_agent/agent/mobile/doubao_action_parser.py | py | code-comment | done | explain how model action text is parsed into tool calls and screen coordinates |
| mobile_agent/mobile_agent/agent/mobile_use_agent.py | mobile_agent/mobile_agent/agent/mobile_use_agent.py | py | code-comment | done | explain the top-level agent lifecycle from init to run |
| mobile_agent/mobile_agent/agent/prompt/__init__.py | mobile_agent/mobile_agent/agent/prompt/__init__.py | py | code-comment | skipped | package marker with almost no logic |
| mobile_agent/mobile_agent/agent/prompt/doubao_vision_pro.py | mobile_agent/mobile_agent/agent/prompt/doubao_vision_pro.py | py | code-comment | skipped | prompt text is large reference data, not ideal for inline beginner comments |
| mobile_agent/mobile_agent/agent/tools/__init__.py | mobile_agent/mobile_agent/agent/tools/__init__.py | py | code-comment | skipped | package marker with almost no logic |
| mobile_agent/mobile_agent/agent/tools/mcp.py | mobile_agent/mobile_agent/agent/tools/mcp.py | py | code-comment | done | explain MCP hub connection lifecycle |
| mobile_agent/mobile_agent/agent/tools/model.py | mobile_agent/mobile_agent/agent/tools/model.py | py | code-comment | done | explain tool call data models and why typed wrappers help later execution stages |
| mobile_agent/mobile_agent/agent/tools/tool/__init__.py | mobile_agent/mobile_agent/agent/tools/tool/__init__.py | py | code-comment | skipped | package marker with almost no logic |
| mobile_agent/mobile_agent/agent/tools/tool/abc.py | mobile_agent/mobile_agent/agent/tools/tool/abc.py | py | code-comment | done | explain the abstract base contract shared by all tools |
| mobile_agent/mobile_agent/agent/tools/tool/call_user.py | mobile_agent/mobile_agent/agent/tools/tool/call_user.py | py | code-comment | skipped | specialized edge tool not part of the main happy-path demo flow |
| mobile_agent/mobile_agent/agent/tools/tool/error.py | mobile_agent/mobile_agent/agent/tools/tool/error.py | py | code-comment | skipped | specialized error helper with narrow purpose |
| mobile_agent/mobile_agent/agent/tools/tool/finished.py | mobile_agent/mobile_agent/agent/tools/tool/finished.py | py | code-comment | done | explain the terminal finished tool and how it signals agent completion |
| mobile_agent/mobile_agent/agent/tools/tool/mcp_tool.py | mobile_agent/mobile_agent/agent/tools/tool/mcp_tool.py | py | code-comment | done | explain how remote MCP tools are adapted into local executable tool objects |
| mobile_agent/mobile_agent/agent/tools/tool/wait.py | mobile_agent/mobile_agent/agent/tools/tool/wait.py | py | code-comment | done | explain the local wait tool and why a deliberate pause can be a valid agent action |
| mobile_agent/mobile_agent/agent/tools/tools.py | mobile_agent/mobile_agent/agent/tools/tools.py | py | code-comment | done | explain tool registry construction and execution dispatch |
| mobile_agent/mobile_agent/agent/utils/__init__.py | mobile_agent/mobile_agent/agent/utils/__init__.py | py | code-comment | skipped | package marker with almost no logic |
| mobile_agent/mobile_agent/agent/utils/bbox.py | mobile_agent/mobile_agent/agent/utils/bbox.py | py | code-comment | skipped | geometry helper is peripheral to first-pass reading |
| mobile_agent/mobile_agent/agent/utils/image.py | mobile_agent/mobile_agent/agent/utils/image.py | py | code-comment | skipped | image helper is peripheral to first-pass reading |
| mobile_agent/mobile_agent/config/__init__.py | mobile_agent/mobile_agent/config/__init__.py | py | code-comment | skipped | package marker with almost no logic |
| mobile_agent/mobile_agent/config/settings.py | mobile_agent/mobile_agent/config/settings.py | py | code-comment | done | explain how environment config is loaded into typed settings |
| mobile_agent/mobile_agent/exception/__init__.py | mobile_agent/mobile_agent/exception/__init__.py | py | code-comment | skipped | package marker with almost no logic |
| mobile_agent/mobile_agent/exception/api.py | mobile_agent/mobile_agent/exception/api.py | py | code-comment | skipped | tiny exception definition with self-explanatory behavior |
| mobile_agent/mobile_agent/exception/sse.py | mobile_agent/mobile_agent/exception/sse.py | py | code-comment | skipped | tiny marker exception |
| mobile_agent/mobile_agent/middleware/__init__.py | mobile_agent/mobile_agent/middleware/__init__.py | py | code-comment | skipped | package marker with almost no logic |
| mobile_agent/mobile_agent/middleware/middleware.py | mobile_agent/mobile_agent/middleware/middleware.py | py | code-comment | done | explain auth and response wrapping middleware behavior |
| mobile_agent/mobile_agent/routers/__init__.py | mobile_agent/mobile_agent/routers/__init__.py | py | code-comment | skipped | package marker with almost no logic |
| mobile_agent/mobile_agent/routers/agent.py | mobile_agent/mobile_agent/routers/agent.py | py | code-comment | done | explain streaming endpoint lifecycle and cancellation handling |
| mobile_agent/mobile_agent/routers/base.py | mobile_agent/mobile_agent/routers/base.py | py | code-comment | done | explain central route registration |
| mobile_agent/mobile_agent/routers/session.py | mobile_agent/mobile_agent/routers/session.py | py | code-comment | done | explain session create/reset APIs and their role in the demo |
| mobile_agent/mobile_agent/service/pod/__init__.py | mobile_agent/mobile_agent/service/pod/__init__.py | py | code-comment | skipped | package marker with almost no logic |
| mobile_agent/mobile_agent/service/pod/manager.py | mobile_agent/mobile_agent/service/pod/manager.py | py | code-comment | done | explain pod auth token fetching and vePhone resource assembly flow |
| mobile_agent/mobile_agent/service/session/__init__.py | mobile_agent/mobile_agent/service/session/__init__.py | py | code-comment | skipped | package marker with almost no logic |
| mobile_agent/mobile_agent/service/session/manager.py | mobile_agent/mobile_agent/service/session/manager.py | py | code-comment | done | explain thread session lifecycle, expiry, and pod metadata updates |
| mobile_agent/script/ci.py | mobile_agent/script/ci.py | py | code-comment | skipped | CI helper script is outside the main runtime learning path |
| mobile_use_mcp/client/mobile_use_client/client.go | mobile_use_mcp/client/mobile_use_client/client.go | go | code-comment | done | explain MCP client construction for local stdio, HTTP, and SSE transports |
| mobile_use_mcp/client/mobile_use_client/client_test.go | mobile_use_mcp/client/mobile_use_client/client_test.go | go | code-comment | skipped | test file is secondary to runtime architecture |
| mobile_use_mcp/cmd/mobile_use_mcp/main.go | mobile_use_mcp/cmd/mobile_use_mcp/main.go | go | code-comment | done | explain process boot, flags, and graceful shutdown |
| mobile_use_mcp/internal/mobile_use/config/config.go | mobile_use_mcp/internal/mobile_use/config/config.go | go | code-comment | done | explain core configuration structs passed through the server |
| mobile_use_mcp/internal/mobile_use/consts/consts.go | mobile_use_mcp/internal/mobile_use/consts/consts.go | go | code-comment | skipped | constant table is reference data, not a good beginner comment target |
| mobile_use_mcp/internal/mobile_use/server/server.go | mobile_use_mcp/internal/mobile_use/server/server.go | go | code-comment | done | explain tool registration, transports, and auth context assembly |
| mobile_use_mcp/internal/mobile_use/service/acpe_model.go | mobile_use_mcp/internal/mobile_use/service/acpe_model.go | go | code-comment | skipped | mostly plain data definitions |
| mobile_use_mcp/internal/mobile_use/service/option.go | mobile_use_mcp/internal/mobile_use/service/option.go | go | code-comment | done | explain option pattern used to build the provider |
| mobile_use_mcp/internal/mobile_use/service/provider.go | mobile_use_mcp/internal/mobile_use/service/provider.go | go | code-comment | done | explain how MCP tool calls become ACEP API or shell commands |
| mobile_use_mcp/internal/mobile_use/tool/autoinstall_app.go | mobile_use_mcp/internal/mobile_use/tool/autoinstall_app.go | go | code-comment | done | explain tool registration, parameters, and handler flow for auto-install app |
| mobile_use_mcp/internal/mobile_use/tool/base.go | mobile_use_mcp/internal/mobile_use/tool/base.go | go | code-comment | done | explain common helper logic shared by all tools |
| mobile_use_mcp/internal/mobile_use/tool/close_app.go | mobile_use_mcp/internal/mobile_use/tool/close_app.go | go | code-comment | done | explain tool registration and handler flow for closing an app |
| mobile_use_mcp/internal/mobile_use/tool/key_event_back.go | mobile_use_mcp/internal/mobile_use/tool/key_event_back.go | go | code-comment | skipped | very small single-purpose wrapper; similar pattern already covered elsewhere |
| mobile_use_mcp/internal/mobile_use/tool/key_event_home.go | mobile_use_mcp/internal/mobile_use/tool/key_event_home.go | go | code-comment | skipped | very small single-purpose wrapper; similar pattern already covered elsewhere |
| mobile_use_mcp/internal/mobile_use/tool/key_event_menu.go | mobile_use_mcp/internal/mobile_use/tool/key_event_menu.go | go | code-comment | skipped | very small single-purpose wrapper; similar pattern already covered elsewhere |
| mobile_use_mcp/internal/mobile_use/tool/launch_app.go | mobile_use_mcp/internal/mobile_use/tool/launch_app.go | go | code-comment | done | explain tool registration and handler flow for launching an app |
| mobile_use_mcp/internal/mobile_use/tool/list_app.go | mobile_use_mcp/internal/mobile_use/tool/list_app.go | go | code-comment | done | explain app listing tool flow and result serialization for the model |
| mobile_use_mcp/internal/mobile_use/tool/screen_swipe.go | mobile_use_mcp/internal/mobile_use/tool/screen_swipe.go | go | code-comment | done | explain swipe tool parameters, validation, and service dispatch |
| mobile_use_mcp/internal/mobile_use/tool/screen_tap.go | mobile_use_mcp/internal/mobile_use/tool/screen_tap.go | go | code-comment | done | explain tap tool parameters, validation, and service dispatch |
| mobile_use_mcp/internal/mobile_use/tool/take_screenshot.go | mobile_use_mcp/internal/mobile_use/tool/take_screenshot.go | go | code-comment | done | explain screenshot tool request and response conversion |
| mobile_use_mcp/internal/mobile_use/tool/terminate.go | mobile_use_mcp/internal/mobile_use/tool/terminate.go | go | code-comment | done | explain the terminate intent tool and its current confirmation-style behavior |
| mobile_use_mcp/internal/mobile_use/tool/text_input.go | mobile_use_mcp/internal/mobile_use/tool/text_input.go | go | code-comment | done | explain text input tool flow and encoding concerns |
| web/next.config.ts | web/next.config.ts | ts | code-comment | skipped | framework config with little project-specific runtime logic |
| web/public/vephone-sdk.js | web/public/vephone-sdk.js | js | code-comment | skipped | bundled external SDK, avoid editing vendor-like asset |
| web/src/app/api/_utils/fetch.ts | web/src/app/api/_utils/fetch.ts | ts | code-comment | done | explain the shared API proxy helper for JSON and SSE backend responses |
| web/src/app/api/_utils/middleware.ts | web/src/app/api/_utils/middleware.ts | ts | code-comment | done | explain request validation and response normalization in API routes |
| web/src/app/api/_utils/vefaas.ts | web/src/app/api/_utils/vefaas.ts | ts | code-comment | done | explain VE FaaS specific error translation into UI-facing API errors |
| web/src/app/api/agent/cancel/route.ts | web/src/app/api/agent/cancel/route.ts | ts | code-comment | done | explain cancel route input handling and proxying to the backend agent service |
| web/src/app/api/agent/stream/route.ts | web/src/app/api/agent/stream/route.ts | ts | code-comment | done | explain stream proxy from browser-facing route to agent backend |
| web/src/app/api/session/create/route.ts | web/src/app/api/session/create/route.ts | ts | code-comment | done | explain session creation proxy and response handling |
| web/src/app/api/session/reset/route.ts | web/src/app/api/session/reset/route.ts | ts | code-comment | done | explain reset route input handling, user info passthrough, and new thread creation |
| web/src/app/atom.ts | web/src/app/atom.ts | ts | code-comment | done | explain shared frontend state atoms and persistence |
| web/src/app/chat/page.tsx | web/src/app/chat/page.tsx | tsx | code-comment | done | explain chat page setup, session recovery, and layout decisions |
| web/src/app/layout.tsx | web/src/app/layout.tsx | tsx | code-comment | skipped | root layout is thin shell code |
| web/src/app/page.tsx | web/src/app/page.tsx | tsx | code-comment | done | explain entry form, session bootstrap, and navigation flow |
| web/src/components/chat/ChatMessage.tsx | web/src/components/chat/ChatMessage.tsx | tsx | code-comment | done | explain user message rendering, fallback username logic, and avatar letter generation |
| web/src/components/chat/ChatPanel.tsx | web/src/components/chat/ChatPanel.tsx | tsx | code-comment | done | explain how the main chat workspace is assembled |
| web/src/components/chat/ChatView.tsx | web/src/components/chat/ChatView.tsx | tsx | code-comment | done | explain message area rendering flow |
| web/src/components/chat/InputArea.tsx | web/src/components/chat/InputArea.tsx | tsx | code-comment | done | explain user input, send, and cancel interactions |
| web/src/components/chat/MessageList.tsx | web/src/components/chat/MessageList.tsx | tsx | code-comment | done | explain how heterogeneous message types are iterated and rendered |
| web/src/components/chat/ResetChat.tsx | web/src/components/chat/ResetChat.tsx | tsx | code-comment | done | explain session reset flow, cancel-before-reset behavior, and button state guarding |
| web/src/components/chat/ThinkingMessage.tsx | web/src/components/chat/ThinkingMessage.tsx | tsx | code-comment | done | explain how streamed thinking steps and tool calls are shown |
| web/src/components/chat/TimeoutPanel.tsx | web/src/components/chat/TimeoutPanel.tsx | tsx | code-comment | done | explain timeout UI configuration and callback separation for retry and outbound links |
| web/src/components/chat/TimeoutView.tsx | web/src/components/chat/TimeoutView.tsx | tsx | code-comment | skipped | small presentational branch already covered by timeout panel flow |
| web/src/components/chat/WelcomeView.tsx | web/src/components/chat/WelcomeView.tsx | tsx | code-comment | skipped | unused or secondary presentation layer for current flow |
| web/src/components/common/VePhonePreloader.tsx | web/src/components/common/VePhonePreloader.tsx | tsx | code-comment | done | explain eager SDK preloading and why a no-UI side-effect component is useful |
| web/src/components/phone/OperatorButton.tsx | web/src/components/phone/OperatorButton.tsx | tsx | code-comment | done | explain reusable async operator button behavior and loading guard |
| web/src/components/phone/index.tsx | web/src/components/phone/index.tsx | tsx | code-comment | done | explain vePhone lifecycle state, rotation handling, and render container sizing |
| web/src/components/resize/index.tsx | web/src/components/resize/index.tsx | tsx | code-comment | skipped | very small presentational component |
| web/src/components/ui/alert-dialog.tsx | web/src/components/ui/alert-dialog.tsx | tsx | code-comment | skipped | shared UI wrapper or library-style component; low teaching value for current project flow |
| web/src/components/ui/button.tsx | web/src/components/ui/button.tsx | tsx | code-comment | skipped | shared UI wrapper or library-style component; low teaching value for current project flow |
| web/src/components/ui/dialog.tsx | web/src/components/ui/dialog.tsx | tsx | code-comment | skipped | shared UI wrapper or library-style component; low teaching value for current project flow |
| web/src/components/ui/form.tsx | web/src/components/ui/form.tsx | tsx | code-comment | skipped | shared UI wrapper or library-style component; low teaching value for current project flow |
| web/src/components/ui/input.tsx | web/src/components/ui/input.tsx | tsx | code-comment | skipped | shared UI wrapper or library-style component; low teaching value for current project flow |
| web/src/components/ui/label.tsx | web/src/components/ui/label.tsx | tsx | code-comment | skipped | shared UI wrapper or library-style component; low teaching value for current project flow |
| web/src/components/ui/sonner.tsx | web/src/components/ui/sonner.tsx | tsx | code-comment | skipped | shared UI wrapper or library-style component; low teaching value for current project flow |
| web/src/components/ui/textarea.tsx | web/src/components/ui/textarea.tsx | tsx | code-comment | skipped | shared UI wrapper or library-style component; low teaching value for current project flow |
| web/src/components/ui/tooltip.tsx | web/src/components/ui/tooltip.tsx | tsx | code-comment | skipped | shared UI wrapper or library-style component; low teaching value for current project flow |
| web/src/hooks/useCloudAgent.ts | web/src/hooks/useCloudAgent.ts | ts | code-comment | done | explain how SSE messages are merged into UI state |
| web/src/hooks/useCreateSession.ts | web/src/hooks/useCreateSession.ts | ts | code-comment | done | explain session creation helper and side effects |
| web/src/hooks/useResize.ts | web/src/hooks/useResize.ts | ts | code-comment | skipped | small layout helper with limited teaching value |
| web/src/hooks/useTimeoutPhone.ts | web/src/hooks/useTimeoutPhone.ts | ts | code-comment | done | explain timeout countdown state and UI branching |
| web/src/lib/cloudAgent.ts | web/src/lib/cloudAgent.ts | ts | code-comment | done | explain browser-side agent client, SSE parsing, and persistence |
| web/src/lib/exception/apiError.ts | web/src/lib/exception/apiError.ts | ts | code-comment | skipped | tiny error type helper |
| web/src/lib/fetch/index.ts | web/src/lib/fetch/index.ts | ts | code-comment | done | explain common fetch wrappers used by the frontend |
| web/src/lib/fetch/redirect.tsx | web/src/lib/fetch/redirect.tsx | tsx | code-comment | skipped | thin redirect helper |
| web/src/lib/fetch/session.ts | web/src/lib/fetch/session.ts | ts | code-comment | done | explain browser-side session affinity storage for sticking to one FaaS instance |
| web/src/lib/socket/abc.ts | web/src/lib/socket/abc.ts | ts | code-comment | done | explain event and message types shared by SSE handling |
| web/src/lib/time/format.ts | web/src/lib/time/format.ts | ts | code-comment | skipped | simple formatting helper |
| web/src/lib/utils/css.ts | web/src/lib/utils/css.ts | ts | code-comment | skipped | generic utility helper |
| web/src/lib/utils/delay.ts | web/src/lib/utils/delay.ts | ts | code-comment | skipped | generic utility helper |
| web/src/lib/utils/index.ts | web/src/lib/utils/index.ts | ts | code-comment | done | explain shared utility exports, cn helper, and token-preserving URL helpers |
| web/src/lib/utils/safeJSONParse.ts | web/src/lib/utils/safeJSONParse.ts | ts | code-comment | skipped | tiny utility with self-evident behavior |
| web/src/lib/utils/time.ts | web/src/lib/utils/time.ts | ts | code-comment | skipped | small helper with limited teaching value |
| web/src/lib/vePhone/index.ts | web/src/lib/vePhone/index.ts | ts | code-comment | skipped | re-export file with no logic |
| web/src/lib/vePhone/loader.ts | web/src/lib/vePhone/loader.ts | ts | code-comment | done | explain singleton SDK loader behavior, script deduplication, and browser-only guards |
| web/src/lib/vePhone/log.ts | web/src/lib/vePhone/log.ts | ts | code-comment | skipped | tiny logging helper |
| web/src/lib/vePhone/type.ts | web/src/lib/vePhone/type.ts | ts | code-comment | done | explain vePhone token, startup config, enums, and SDK interface contracts |
| web/src/lib/vePhone/web/camera.ts | web/src/lib/vePhone/web/camera.ts | ts | code-comment | done | explain browser-side camera and microphone stream coordination with the vePhone SDK |
| web/src/lib/vePhone/web/config.ts | web/src/lib/vePhone/web/config.ts | ts | code-comment | skipped | tiny config constant holder |
| web/src/lib/vePhone/web/core.ts | web/src/lib/vePhone/web/core.ts | ts | code-comment | done | explain the main browser-side cloud phone integration class |
| web/src/lib/vePhone/web/decorator.ts | web/src/lib/vePhone/web/decorator.ts | ts | code-comment | skipped | small helper around SDK callbacks |
| web/src/lib/vePhone/web/error.ts | web/src/lib/vePhone/web/error.ts | ts | code-comment | skipped | tiny error helper |
| web/src/lib/vePhone/web/tool.ts | web/src/lib/vePhone/web/tool.ts | ts | code-comment | done | explain browser-side phone actions such as home back tap swipe and screenshot |
| web/src/styles/fonts.ts | web/src/styles/fonts.ts | ts | code-comment | skipped | mostly static font registration |
| web/src/types/index.ts | web/src/types/index.ts | ts | code-comment | done | explain backend response types used in the UI |
| web/tailwind.config.js | web/tailwind.config.js | js | code-comment | skipped | framework config with little project-specific runtime logic |
| PROJECT_EXPLAINED.zh-CN.md | PROJECT_EXPLAINED.zh-CN.md | md | project-guide | done | explain overall architecture with beginner-friendly diagrams |
