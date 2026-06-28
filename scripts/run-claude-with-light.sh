#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN_DIR="$ROOT_DIR/claude-status-light-plugin"
STATUS_FILE="$ROOT_DIR/.runtime/status.json"

mkdir -p "$ROOT_DIR/.runtime"
exec env CLAUDE_STATUS_LIGHT_FILE="$STATUS_FILE" claude --plugin-dir "$PLUGIN_DIR" "$@"
