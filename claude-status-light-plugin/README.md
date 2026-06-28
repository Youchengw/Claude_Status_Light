# Claude Status Light Plugin

This Claude Code plugin mirrors session activity into:

`~/Library/Application Support/ClaudeStatusLight/status.json`

The companion macOS app in this repo watches that file and switches between:

- `idle` -> green
- `working` -> yellow
- `approval` -> red

## What it tracks

- `UserPromptSubmit` -> yellow
- `PreToolUse` / `PostToolUse` -> yellow
- `Notification.permission_prompt` -> red
- `Notification.idle_prompt` -> green
- `Notification.elicitation_dialog` -> red
- `Stop` / `SessionEnd` -> green

## Quick test

```bash
claude --plugin-dir ./claude-status-light-plugin
```

Or use the wrapper script from the repo root:

```bash
./scripts/run-claude-with-light.sh
```
