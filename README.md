# Claude Status Light

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A macOS companion app for Claude Code that shows Claude's current status via a floating pixel-art desktop pet with a traffic light, plus a matching menu bar icon.

- Green: `Idle`
- Yellow: `Working`
- Red: `Awaiting you`

The desktop pet is a pixel-art Claude-like character with a horizontal traffic light on its head, idle floating animation, and a head-pat animation on mouse hover.

This repo contains three parts:

1. `ClaudeStatusLight` — native SwiftUI menu bar + floating window app
2. `claude-status-light-plugin` — Claude Code plugin that writes session state to a local `status.json`
3. `ClaudeStatusLight.xcodeproj` — Xcode project ready to open and run

## Features

- Menu bar icon: pixel pet silhouette that adapts to light/dark mode
- Floating desktop pet always on top with traffic light indicator
- Idle floating animation when Claude isn't active
- Head-pat animation on mouse hover
- Draggable panel with position memory
- Hide / show / reset position from menu bar
- Launch at Login support
- Status preview from menu (idle / working / approval)

## Quick Start

### 1. Launch the pet app

```bash
./scripts/launch-light-app.sh
```

Or run directly:

```bash
swift run ClaudeLight
```

### 2. Start Claude Code with the plugin

```bash
./scripts/run-claude-with-light.sh
```

Equivalent to:

```bash
claude --plugin-dir ./claude-status-light-plugin
```

### 3. (Optional) Install plugin globally

```bash
./scripts/install-global-plugin.sh
```

After global install, just run `claude` normally and the light will follow.

Check status:

```bash
python3 ./scripts/manage-global-plugin.py status
```

Uninstall:

```bash
./scripts/uninstall-global-plugin.sh
```

## Build Release App

```bash
./scripts/build-release-app.sh
open ~/Applications/ClaudeStatusLight.app
```

Custom output:

```bash
CLAUDE_STATUS_LIGHT_OUTPUT_DIR="/your/path" ./scripts/build-release-app.sh
```

Package as zip:

```bash
./scripts/package-release-zip.sh
# → ./dist/ClaudeStatusLight-macOS.zip
```

## Hook Mapping

| Hook | Status |
|------|--------|
| `SessionStart` | Idle |
| `UserPromptSubmit` | Working |
| `PreToolUse` | Working |
| `PostToolUse` | Working |
| `Notification.permission_prompt` | Awaiting you |
| `Notification.elicitation_dialog` | Awaiting you |
| `Notification.idle_prompt` | Idle |
| `Stop` | Idle |
| `SessionEnd` | Idle |

## Status File

Default location shared by the app and plugin:

`~/Library/Application Support/ClaudeStatusLight/status.json`

Override with env var: `CLAUDE_STATUS_LIGHT_FILE`

## Requirements

- macOS 14+
- Xcode 16+ (for building from source)
- Claude Code (for the plugin)

## License

MIT © Youcheng Wang

---

[中文文档](README_CN.md)
