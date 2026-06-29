#!/bin/zsh
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "Uninstalling ClaudeLight plugin..."
python3 "$ROOT_DIR/scripts/manage-global-plugin.py" uninstall

echo ""
echo "✅ Plugin uninstalled."
