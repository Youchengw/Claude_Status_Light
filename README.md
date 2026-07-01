# ClaudeLight

A floating pixel-art desktop pet + menu bar icon that shows [Claude Code](https://claude.ai/code)'s real-time status.

🟢 Idle  |  🟡 Working  |  🔴 Awaiting you

| Status Light | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Head Pat |
|:---:|:---:|:---:|
| ![status demo](assets/demo-status.gif) | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | ![head pat demo](assets/demo-pat.gif) |

## Quick Start

### 1. Get ClaudeLight

| Platform | How to get it |
|----------|---------------|
| **macOS** | Download `ClaudeLight-macOS.zip` from [Releases](https://github.com/Youchengw/ClaudeLight/releases) → drag to `/Applications` |
| **Windows** | Download `ClaudeLight.exe` from [Releases](https://github.com/Youchengw/ClaudeLight/releases) |
| **Linux** | Download `ClaudeLight.tar.gz` from [Releases](https://github.com/Youchengw/ClaudeLight/releases), or `git clone https://github.com/Youchengw/ClaudeLight.git` to run from source |

### 2. Install the plugin

```bash
cd ClaudeLight
./scripts/install.sh
```

> If you haven't cloned the repo yet (macOS / Windows), run `git clone https://github.com/Youchengw/ClaudeLight.git` first.

### 3. Launch ClaudeLight

| Platform | Command |
|----------|---------|
| **macOS** | Double-click `ClaudeLight.app` in `/Applications`, or `swift run ClaudeLight` (dev) |
| **Windows** | Double-click `ClaudeLight.exe` |
| **Linux** | `tar xzf ClaudeLight.tar.gz && chmod +x ClaudeLight && ./ClaudeLight` (or `python desktop/main.py` from source) |

### 4. Use Claude Code

Keep ClaudeLight running and use `claude` as usual — the light follows automatically.

## Features

- Pixel-art desktop pet with traffic light — always on top, draggable, remembers position
- Menu bar icon / system tray icon adapts to light/dark mode
- Idle floating animation + head-pat on mouse hover
- Launch at Login support (macOS)

## Build from Source

**macOS** (native SwiftUI, requires Xcode 16+, macOS 14+):

```bash
./scripts/build-release-app.sh            # Build & install to /Applications
swift run ClaudeLight                     # Run directly via Swift Package Manager
./scripts/package-release-zip.sh          # Package as .zip → ./dist/
```

**Windows / Linux** (Python + PyQt6):

```bash
cd desktop
pip install -r requirements.txt
python main.py                            # Run directly
# Windows: build_windows.bat              # → dist/ClaudeLight.exe
# Linux:   ./build_linux.sh               # → dist/ClaudeLight
```

## How It Works

```
Claude Code → plugin hooks → status.json ← file monitoring ← app
```

| Hook | Status |
|------|--------|
| `UserPromptSubmit` / `PreToolUse` / `PostToolUse` | Working |
| `Notification.permission_prompt` / `elicitation_dialog` | Awaiting you |
| `Stop` / `SessionEnd` / `idle_prompt` | Idle |

## Uninstall

```bash
./scripts/uninstall.sh                    # Remove plugin
sudo rm -rf /Applications/ClaudeLight.app # Remove app (macOS)
```

## License

MIT © Youcheng Wang

---

[中文文档](README_CN.md)
