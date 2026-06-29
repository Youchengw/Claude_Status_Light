#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RM_BIN="/bin/rm"
MKDIR_BIN="/bin/mkdir"
DITTO_BIN="/usr/bin/ditto"
TMPDIR_ROOT="${TMPDIR:-/tmp}"
BUILD_STAGE_DIR="${CLAUDE_STATUS_LIGHT_PACKAGE_STAGE_DIR:-$TMPDIR_ROOT/claude-status-light-package}"
DERIVED_DATA_DIR="${CLAUDE_STATUS_LIGHT_PACKAGE_DERIVED_DATA:-$TMPDIR_ROOT/claude-status-light-package-derived}"
DIST_DIR="$ROOT_DIR/dist"
ZIP_PATH="$DIST_DIR/ClaudeLight-macOS.zip"

cd "$ROOT_DIR"
"$MKDIR_BIN" -p "$DIST_DIR"
"$RM_BIN" -rf "$BUILD_STAGE_DIR"

CLAUDE_STATUS_LIGHT_OUTPUT_DIR="$BUILD_STAGE_DIR" \
CLAUDE_STATUS_LIGHT_DERIVED_DATA="$DERIVED_DATA_DIR" \
./scripts/build-release-app.sh

"$RM_BIN" -f "$ZIP_PATH"
"$DITTO_BIN" -c -k --sequesterRsrc --keepParent "$BUILD_STAGE_DIR/ClaudeLight.app" "$ZIP_PATH"

echo "Packaged zip:"
echo "$ZIP_PATH"
