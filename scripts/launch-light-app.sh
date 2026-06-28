#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_FILE="${TMPDIR:-/tmp}/claude-status-light.log"
STATUS_FILE="$ROOT_DIR/.runtime/status.json"
BUILD_HOME="$ROOT_DIR/.runtime/swift-home"
CLANG_CACHE="$ROOT_DIR/.runtime/clang-module-cache"
SWIFTPM_CACHE="$ROOT_DIR/.runtime/swiftpm-cache"

cd "$ROOT_DIR"
mkdir -p "$ROOT_DIR/.runtime"
mkdir -p "$BUILD_HOME" "$CLANG_CACHE" "$SWIFTPM_CACHE"
HOME="$BUILD_HOME" \
CLANG_MODULE_CACHE_PATH="$CLANG_CACHE" \
SWIFTPM_MODULECACHE_OVERRIDE="$SWIFTPM_CACHE" \
swift build -c release
nohup env CLAUDE_STATUS_LIGHT_FILE="$STATUS_FILE" "$ROOT_DIR/.build/release/ClaudeStatusLight" > "$LOG_FILE" 2>&1 &

echo "ClaudeStatusLight launched in background."
echo "Log: $LOG_FILE"
echo "Status file: $STATUS_FILE"
