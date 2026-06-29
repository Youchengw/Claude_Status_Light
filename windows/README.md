# ClaudeLight for Windows

Floating pixel-art desktop pet + system tray icon for Claude Code status.

## Quick Start

### 1. Install dependencies

```cmd
pip install -r requirements.txt
```

### 2. Run

```cmd
python main.py
```

A floating pixel pet window and a system tray icon will appear.

### 3. Build standalone .exe

```cmd
build.bat
```

Output: `dist/ClaudeLight.exe` — single file, no Python needed.

## How It Works

The app watches `status.json` (written by the Claude Code plugin) via watchdog.  Same status file format as the macOS version — the plugin (`claude-status-light-plugin/`) works on both platforms without changes.

Default status file location: `%APPDATA%/ClaudeLight/status.json`

Override with env var: `CLAUDE_STATUS_LIGHT_FILE`
