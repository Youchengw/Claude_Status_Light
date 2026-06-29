# ClaudeLight

A floating pixel-art desktop pet + menu bar icon that shows [Claude Code](https://claude.ai/code)'s real-time status.

🟢 Idle  |  🟡 Working  |  🔴 Awaiting you

## Quick Start

### 1. Get the app

Download `ClaudeLight-macOS.zip` from [Releases](https://github.com/Youchengw/Claude_Status_Light/releases), unzip, and drag `ClaudeLight.app` to `/Applications`.

### 2. Install the plugin

```bash
git clone https://github.com/Youchengw/Claude_Status_Light.git
cd Claude_Status_Light
./scripts/install.sh
```

### 3. Use Claude Code

Open `ClaudeLight.app` and run `claude` as usual. The light follows automatically.

## Features

- Pixel-art desktop pet with traffic light — always on top, draggable, remembers position
- Menu bar icon that adapts to light/dark mode
- Idle floating animation + head-pat on mouse hover
- Launch at Login support

## Build from Source

Requires Xcode 16+, macOS 14+.

```bash
./scripts/build-release-app.sh            # Build & install to /Applications
swift run ClaudeLight                     # Run directly via Swift Package Manager
./scripts/package-release-zip.sh          # Package as .zip → ./dist/
```

## How It Works

```
Claude Code → plugin hooks → status.json ← DispatchSource file monitoring ← SwiftUI app
```

| Hook | Status |
|------|--------|
| `UserPromptSubmit` / `PreToolUse` / `PostToolUse` | Working |
| `Notification.permission_prompt` / `elicitation_dialog` | Awaiting you |
| `Stop` / `SessionEnd` / `idle_prompt` | Idle |

## Uninstall

```bash
./scripts/uninstall.sh                    # Remove plugin
sudo rm -rf /Applications/ClaudeLight.app # Remove app
```

## License

MIT © Youcheng Wang

---

[中文文档](README_CN.md)
