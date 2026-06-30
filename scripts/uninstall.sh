#!/bin/zsh
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Find a usable Python 3 interpreter.
if command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
elif command -v python >/dev/null 2>&1; then
    PYTHON=python
else
    echo "Error: Python 3 not found. Please install Python and try again." >&2
    exit 1
fi

echo "Uninstalling ClaudeLight plugin..."
"$PYTHON" "$ROOT_DIR/scripts/manage-global-plugin.py" uninstall

echo ""
echo "✅ Plugin uninstalled."
