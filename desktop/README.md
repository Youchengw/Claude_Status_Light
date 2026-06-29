# ClaudeLight Desktop App (Cross-Platform)

Floating pixel-art desktop pet + system tray icon. Works on macOS, Windows, and Linux.

> **macOS users**: Use the native SwiftUI app in `Sources/` instead — it has a menu bar icon and tighter system integration. This Python app is the primary client for **Windows and Linux**.

## Quick Start

```bash
pip install -r requirements.txt
python main.py
```

## Platform Notes

| Platform | Status file location |
|----------|---------------------|
| macOS | `~/Library/Application Support/ClaudeStatusLight/status.json` |
| Windows | `%APPDATA%/ClaudeLight/status.json` |
| Linux | `~/.local/share/ClaudeLight/status.json` |

Override with env var `CLAUDE_STATUS_LIGHT_FILE`.

## Build Standalone Binary

```bash
# Windows
build_windows.bat          # → dist/ClaudeLight.exe

# Linux / macOS
./build_linux.sh           # → dist/ClaudeLight
```
