#!/bin/bash
set -euo pipefail

echo "Installing dependencies..."
pip install -r "$(dirname "$0")/requirements.txt"

echo "Building ClaudeLight binary..."
pyinstaller --onefile --name ClaudeLight "$(dirname "$0")/main.py"

echo "Done. Output: dist/ClaudeLight"
