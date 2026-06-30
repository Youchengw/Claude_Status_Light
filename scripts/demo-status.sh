#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
STATUS="${1:-idle}"
DETAIL="${2:-Manual demo status}"
STATUS_FILE="$ROOT_DIR/.runtime/status.json"

# Find a usable Python 3 interpreter.
if command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
elif command -v python >/dev/null 2>&1; then
    PYTHON=python
else
    echo "Error: Python 3 not found. Please install Python and try again." >&2
    exit 1
fi

mkdir -p "$ROOT_DIR/.runtime"

CLAUDE_STATUS_LIGHT_FILE="$STATUS_FILE" \
"$PYTHON" "$ROOT_DIR/claude-status-light-plugin/hooks/write_status.py" "$STATUS" "demo-script" "$DETAIL" < /dev/null
