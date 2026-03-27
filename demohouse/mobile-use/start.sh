#!/bin/bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
RUN_DIR="$ROOT_DIR/.run"
LOG_DIR="$RUN_DIR/logs"

MCP_PORT="${MCP_PORT:-8888}"
AGENT_PORT="${AGENT_PORT:-8000}"
WEB_PORT="${WEB_PORT:-8080}"

mkdir -p "$RUN_DIR" "$LOG_DIR"

start_if_needed() {
  local name="$1"
  local workdir="$2"
  local command="$3"
  local pid_file="$RUN_DIR/${name}.pid"
  local log_file="$LOG_DIR/${name}.log"

  if [[ -f "$pid_file" ]]; then
    local old_pid
    old_pid="$(cat "$pid_file" 2>/dev/null || true)"
    if [[ -n "${old_pid}" ]] && kill -0 "$old_pid" 2>/dev/null; then
      echo "[$name] already running (pid=$old_pid)"
      return 0
    fi
    rm -f "$pid_file"
  fi

  (
    cd "$workdir"
    nohup bash -lc "$command" >>"$log_file" 2>&1 &
    echo $! >"$pid_file"
  )

  sleep 1

  local new_pid
  new_pid="$(cat "$pid_file")"
  if kill -0 "$new_pid" 2>/dev/null; then
    echo "[$name] started (pid=$new_pid, log=$log_file)"
  else
    echo "[$name] failed to start, check log: $log_file" >&2
    exit 1
  fi
}

start_if_needed \
  "mcp" \
  "$ROOT_DIR/mobile_use_mcp" \
  "go run cmd/mobile_use_mcp/main.go -t streamable-http -p $MCP_PORT"

start_if_needed \
  "agent" \
  "$ROOT_DIR/mobile_agent" \
  "uv run python main.py"

start_if_needed \
  "web" \
  "$ROOT_DIR/web" \
  "npm run dev"

echo ""
echo "Services expected at:"
echo "  MCP:   http://127.0.0.1:${MCP_PORT}/mcp"
echo "  Agent: http://127.0.0.1:${AGENT_PORT}"
echo "  Web:   http://127.0.0.1:${WEB_PORT}/?token=123"
