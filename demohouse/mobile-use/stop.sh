#!/bin/bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
RUN_DIR="$ROOT_DIR/.run"

stop_by_pid_file() {
  local name="$1"
  local pid_file="$RUN_DIR/${name}.pid"

  if [[ ! -f "$pid_file" ]]; then
    echo "[$name] pid file not found, skip"
    return 0
  fi

  local pid
  pid="$(cat "$pid_file" 2>/dev/null || true)"

  if [[ -z "${pid}" ]]; then
    rm -f "$pid_file"
    echo "[$name] empty pid file removed"
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

  rm -f "$pid_file"
}

stop_by_pid_file "web"
stop_by_pid_file "agent"
stop_by_pid_file "mcp"

# 双保险，处理 pid 文件丢失但进程仍在的情况。
pkill -f 'next dev -p 8080' 2>/dev/null || true
pkill -f 'uv run python main.py' 2>/dev/null || true
pkill -f 'go run cmd/mobile_use_mcp/main.go -t streamable-http -p 8888' 2>/dev/null || true

echo "All stop commands have been issued."
