#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DEVELOPER_DIR="${DEVELOPER_DIR:-$(/usr/bin/xcode-select -p)}"
XCODEBUILD_BIN="$DEVELOPER_DIR/usr/bin/xcodebuild"
XATTR_BIN="/usr/bin/xattr"
DITTO_BIN="/usr/bin/ditto"
RM_BIN="/bin/rm"
DERIVED_DATA_DIR="${CLAUDE_STATUS_LIGHT_DERIVED_DATA:-${TMPDIR:-/tmp}/ClaudeStatusLightDerivedData}"
OUTPUT_DIR="${CLAUDE_STATUS_LIGHT_OUTPUT_DIR:-/Applications}"
BUILT_APP="$DERIVED_DATA_DIR/Build/Products/Release/ClaudeStatusLight.app"
APP_NAME="ClaudeLight.app"
STAGING_APP="${TMPDIR:-/tmp}/ClaudeLight.staging.app"
EXPORTED_APP="$OUTPUT_DIR/$APP_NAME"
SOURCE_PATHS=(
  "$ROOT_DIR/ClaudeStatusLight.xcodeproj"
  "$ROOT_DIR/ClaudeStatusLight"
  "$ROOT_DIR/Sources"
  "$ROOT_DIR/scripts"
  "$ROOT_DIR/README.md"
  "$ROOT_DIR/Package.swift"
)

cd "$ROOT_DIR"

for path in "${SOURCE_PATHS[@]}"; do
  "$XATTR_BIN" -cr "$path" 2>/dev/null || true
done

COPYFILE_DISABLE=1 "$XCODEBUILD_BIN" \
  -project ClaudeStatusLight.xcodeproj \
  -scheme ClaudeStatusLight \
  -configuration Release \
  -derivedDataPath "$DERIVED_DATA_DIR" \
  CODE_SIGNING_ALLOWED=NO \
  CODE_SIGNING_REQUIRED=NO \
  CODE_SIGN_IDENTITY="" \
  build

# Stage in temp directory so only the final install needs sudo.
"$RM_BIN" -rf "$STAGING_APP"
COPYFILE_DISABLE=1 "$DITTO_BIN" "$BUILT_APP" "$STAGING_APP"
"$XATTR_BIN" -cr "$STAGING_APP" 2>/dev/null || true
/usr/bin/codesign --force --deep --sign - --timestamp=none "$STAGING_APP"

# Kill running instance before replacing.
pkill -x ClaudeStatusLight 2>/dev/null || true

echo "Installing to $EXPORTED_APP (may prompt for sudo)..."
sudo "$RM_BIN" -rf "$EXPORTED_APP"
sudo COPYFILE_DISABLE=1 "$DITTO_BIN" "$STAGING_APP" "$EXPORTED_APP"
"$RM_BIN" -rf "$STAGING_APP"

echo "Exported app:"
echo "$EXPORTED_APP"
