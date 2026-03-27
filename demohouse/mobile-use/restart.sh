#!/bin/bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

bash "$ROOT_DIR/stop.sh"
sleep 1
bash "$ROOT_DIR/start.sh"
