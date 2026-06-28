#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
STATUS="${1:-idle}"
DETAIL="${2:-Manual demo status}"
STATUS_FILE="$ROOT_DIR/.runtime/status.json"

mkdir -p "$ROOT_DIR/.runtime"

CLAUDE_STATUS_LIGHT_FILE="$STATUS_FILE" \
python3 "$ROOT_DIR/claude-status-light-plugin/hooks/write_status.py" "$STATUS" "demo-script" "$DETAIL" < /dev/null
