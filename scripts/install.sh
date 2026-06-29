#!/bin/zsh
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "Installing ClaudeLight plugin..."
python3 "$ROOT_DIR/scripts/manage-global-plugin.py" install

echo ""
echo "✅ Plugin installed. The floating light now follows Claude Code automatically."
echo "   Open ClaudeLight.app and run 'claude' to try it out."
