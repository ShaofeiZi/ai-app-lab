#!/bin/bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
RUN_DIR="$ROOT_DIR/.run"
MCP_PORT="${MCP_PORT:-8888}"
AGENT_PORT="${AGENT_PORT:-8000}"
MOBILE_USE_SERVICE_PORT="${MOBILE_USE_SERVICE_PORT:-8001}"
SKILL_AGENT_PORT="${SKILL_AGENT_PORT:-8002}"
WEB_PORT="${WEB_PORT:-8080}"

stop_pid() {
  local name="$1"
  local pid="$2"

  if [[ -z "$pid" ]]; then
    return 0
  fi

  if kill -0 "$pid" 2>/dev/null; then
    kill "$pid" 2>/dev/null || true
    sleep 1
    if kill -0 "$pid" 2>/dev/null; then
      kill -9 "$pid" 2>/dev/null || true
    fi
    echo "[$name] stopped (pid=$pid)"
  else
    echo "[$name] process not running (pid=$pid)"
  fi
}

stop_by_pid_file() {
  local name="$1"
  local pid_file="$RUN_DIR/${name}.pid"

  if [[ ! -f "$pid_file" ]]; then
    echo "[$name] pid file not found, skip"
    return 0
  fi

  local pid
  pid="$(cat "$pid_file" 2>/dev/null || true)"

  if [[ -z "$pid" ]]; then
    rm -f "$pid_file"
    echo "[$name] empty pid file removed"
    return 0
  fi

  stop_pid "$name" "$pid"
  rm -f "$pid_file"
}

stop_by_port() {
  local name="$1"
  local port="$2"
  local pids=""

  pids="$(lsof -tiTCP:"$port" -sTCP:LISTEN -n -P 2>/dev/null || true)"
  if [[ -z "$pids" ]]; then
    echo "[$name] no listener on port $port"
    return 0
  fi

  local pid
  for pid in $pids; do
    stop_pid "$name" "$pid"
  done
}

stop_by_pid_file "web"
stop_by_pid_file "agent"
stop_by_pid_file "mobile_use_service"
stop_by_pid_file "mobile_agent_skill"
stop_by_pid_file "mcp"

# 双保险，处理 pid 文件缺失、历史手工启动或旧脚本遗留的进程。
stop_by_port "web" "$WEB_PORT"
stop_by_port "agent" "$AGENT_PORT"
stop_by_port "mobile_use_service" "$MOBILE_USE_SERVICE_PORT"
stop_by_port "mobile_agent_skill" "$SKILL_AGENT_PORT"
stop_by_port "mcp" "$MCP_PORT"

pkill -f "next dev -p ${WEB_PORT}" 2>/dev/null || true
pkill -f "next dev -p 8080 --port ${WEB_PORT}" 2>/dev/null || true
pkill -f "go run cmd/mobile_use_mcp/main.go -t streamable-http -p ${MCP_PORT}" 2>/dev/null || true

echo "All stop commands have been issued."
