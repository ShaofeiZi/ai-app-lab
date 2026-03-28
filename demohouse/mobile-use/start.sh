#!/bin/bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
RUN_DIR="$ROOT_DIR/.run"
LOG_DIR="$RUN_DIR/logs"

MCP_PORT="${MCP_PORT:-8888}"
AGENT_PORT="${AGENT_PORT:-8000}"
MOBILE_USE_SERVICE_PORT="${MOBILE_USE_SERVICE_PORT:-8001}"
SKILL_AGENT_PORT="${SKILL_AGENT_PORT:-8002}"
WEB_PORT="${WEB_PORT:-8080}"

# 默认只启动新链路，旧 MCP/Agent 仅在需要兼容排查时显式开启。
START_LEGACY_STACK="${START_LEGACY_STACK:-0}"

mkdir -p "$RUN_DIR" "$LOG_DIR"

healthcheck_url_for() {
  local name="$1"
  local port="$2"

  case "$name" in
    mobile_use_service|mobile_agent_skill)
      echo "http://127.0.0.1:${port}/health"
      ;;
    *)
      echo ""
      ;;
  esac
}

process_matches() {
  local pid="$1"
  local expected="$2"
  local cmdline=""

  cmdline="$(ps -p "$pid" -o command= 2>/dev/null || true)"
  [[ -n "$cmdline" && "$cmdline" == *"$expected"* ]]
}

wait_for_healthcheck() {
  local name="$1"
  local url="$2"
  local attempts="${3:-30}"

  if [[ -z "$url" ]]; then
    return 0
  fi

  for ((i=1; i<=attempts; i++)); do
    if curl -fsS "$url" >/dev/null 2>&1; then
      echo "[$name] health check passed: $url"
      return 0
    fi
    sleep 1
  done

  echo "[$name] health check failed: $url" >&2
  return 1
}

ensure_python_runtime() {
  local workdir="$1"

  if [[ -x "$workdir/.venv/bin/python" ]]; then
    return 0
  fi

  echo "[runtime] missing virtualenv in $workdir, recreating..."

  if command -v uv >/dev/null 2>&1 && [[ -f "$workdir/pyproject.toml" ]]; then
    if [[ -f "$workdir/uv.lock" ]]; then
      (cd "$workdir" && uv sync --frozen)
    else
      (cd "$workdir" && uv sync)
    fi
    return 0
  fi

  python3 -m venv "$workdir/.venv"
  "$workdir/.venv/bin/pip" install --upgrade pip

  if [[ -f "$workdir/requirements.txt" ]]; then
    "$workdir/.venv/bin/pip" install -r "$workdir/requirements.txt"
  fi
}

python_cmd_for() {
  local workdir="$1"
  ensure_python_runtime "$workdir"
  if [[ -x "$workdir/.venv/bin/python" ]]; then
    echo "./.venv/bin/python"
  else
    echo "python3"
  fi
}

port_pid() {
  local port="$1"
  lsof -tiTCP:"$port" -sTCP:LISTEN -n -P 2>/dev/null | head -n 1
}

wait_for_port() {
  local name="$1"
  local port="$2"
  local attempts="${3:-30}"

  for ((i=1; i<=attempts; i++)); do
    if lsof -iTCP:"$port" -sTCP:LISTEN -n -P >/dev/null 2>&1; then
      echo "[$name] listening on port $port"
      return 0
    fi
    sleep 1
  done

  echo "[$name] did not become ready on port $port" >&2
  return 1
}

start_if_needed() {
  local name="$1"
  local workdir="$2"
  local command="$3"
  local port="$4"
  local pid_file="$RUN_DIR/${name}.pid"
  local log_file="$LOG_DIR/${name}.log"
  local healthcheck_url=""

  local existing_pid=""
  existing_pid="$(port_pid "$port" || true)"
  if [[ -n "$existing_pid" ]]; then
    if process_matches "$existing_pid" "$workdir"; then
      healthcheck_url="$(healthcheck_url_for "$name" "$port")"
      if wait_for_healthcheck "$name" "$healthcheck_url" 3; then
        echo "[$name] already listening on port $port (pid=$existing_pid)"
        echo "$existing_pid" >"$pid_file"
        return 0
      fi
      echo "[$name] existing process on port $port failed health check" >&2
      exit 1
    fi
    echo "[$name] port $port is occupied by another process (pid=$existing_pid)" >&2
    exit 1
  fi

  if [[ -f "$pid_file" ]]; then
    rm -f "$pid_file"
  fi

  python3 - "$workdir" "$command" "$log_file" "$pid_file" <<'PY'
import os
import subprocess
import sys

workdir, command, log_file, pid_file = sys.argv[1:]
env = os.environ.copy()
env.setdefault("PYENV_ROOT", os.path.join(os.environ["HOME"], ".pyenv"))
env.setdefault("TERM", "xterm-256color")

with open(log_file, "ab") as log:
    proc = subprocess.Popen(
        ["/bin/zsh", "-dfc", command],
        cwd=workdir,
        stdin=subprocess.DEVNULL,
        stdout=log,
        stderr=log,
        env=env,
        start_new_session=True,
        close_fds=True,
    )

with open(pid_file, "w", encoding="utf-8") as f:
    f.write(str(proc.pid))
PY

  sleep 1

  if ! wait_for_port "$name" "$port"; then
    echo "[$name] failed to bind port $port. check log: $log_file" >&2
    exit 1
  fi

  healthcheck_url="$(healthcheck_url_for "$name" "$port")"
  if ! wait_for_healthcheck "$name" "$healthcheck_url"; then
    echo "[$name] failed health check after startup. check log: $log_file" >&2
    exit 1
  fi

  local bound_pid=""
  bound_pid="$(port_pid "$port" || true)"
  if [[ -n "$bound_pid" ]]; then
    echo "$bound_pid" >"$pid_file"
    echo "[$name] started (pid=$bound_pid, log=$log_file)"
  else
    echo "[$name] port $port became ready but pid could not be resolved" >&2
    exit 1
  fi
}

if [[ "$START_LEGACY_STACK" == "1" ]]; then
  start_if_needed \
    "mcp" \
    "$ROOT_DIR/mobile_use_mcp" \
    "go run cmd/mobile_use_mcp/main.go -t streamable-http -p $MCP_PORT" \
    "$MCP_PORT"

  start_if_needed \
    "agent" \
    "$ROOT_DIR/mobile_agent" \
    "UVICORN_SERVER_PORT=$AGENT_PORT uv run python main.py" \
    "$AGENT_PORT"
fi

start_if_needed \
  "mobile_use_service" \
  "$ROOT_DIR/mobile_use_service" \
  "UVICORN_SERVER_PORT=$MOBILE_USE_SERVICE_PORT $(python_cmd_for "$ROOT_DIR/mobile_use_service") main.py" \
  "$MOBILE_USE_SERVICE_PORT"

start_if_needed \
  "mobile_agent_skill" \
  "$ROOT_DIR/mobile_agent_skill" \
  "UVICORN_SERVER_PORT=$SKILL_AGENT_PORT $(python_cmd_for "$ROOT_DIR/mobile_agent_skill") main.py" \
  "$SKILL_AGENT_PORT"

start_if_needed \
  "web" \
  "$ROOT_DIR/web" \
  "npm run dev -- --port $WEB_PORT" \
  "$WEB_PORT"

echo ""
echo "Services expected at:"
if [[ "$START_LEGACY_STACK" == "1" ]]; then
  echo "  MCP:   http://127.0.0.1:${MCP_PORT}/mcp"
  echo "  Agent: http://127.0.0.1:${AGENT_PORT}"
fi
echo "  Skill Agent: http://127.0.0.1:${SKILL_AGENT_PORT}/mobile-use/api/v1"
echo "  Mobile Use Service: http://127.0.0.1:${MOBILE_USE_SERVICE_PORT}"
echo "  Web:   http://127.0.0.1:${WEB_PORT}/?token=123"
