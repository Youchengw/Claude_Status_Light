# Claude Status Light

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个给 Claude Code 配的 macOS 状态灯小工具，在菜单栏和桌面悬浮窗里实时显示 Claude 当前状态：

- 绿灯: `Idle`
- 黄灯: `Working`
- 红灯: `Awaiting you`

桌面悬浮窗现在是一个像素风 Claude 桌宠，头顶横向红绿灯。

这个仓库包含三部分：

1. `ClaudeStatusLight`：原生 SwiftUI 菜单栏 + 悬浮窗 app
2. `claude-status-light-plugin`：Claude Code plugin，通过 hooks 把状态写到本地 `status.json`
3. `ClaudeStatusLight.xcodeproj`：可直接用 Xcode 打开的 macOS App 工程

## 当前效果

- 常驻 macOS 状态栏，显示黑白像素小桌宠图标（自动适配浅色/深色模式）
- 默认显示始终置顶的像素桌宠悬浮窗，头顶红绿灯
- 待机时桌宠会轻微上下浮动
- 鼠标移到桌宠上会触发摸头动画
- 面板可拖动，位置自动记忆
- 菜单里可隐藏/显示面板、切换状态预览
- 支持开机自启动（Launch at Login）

## 推荐用法

如果你只是想正常使用，不想每次开 Xcode，直接用 release app：

```bash
./scripts/build-release-app.sh
open ~/Applications/ClaudeStatusLight.app
```

以后日常只需要：

1. 先打开 `ClaudeStatusLight.app`
2. 再打开带 plugin 的 Claude Code 会话

## 状态文件

默认情况下，app 和 plugin 共享这个文件：

`~/Library/Application Support/ClaudeStatusLight/status.json`

仓库自带脚本为了便于本地验证，会把它覆盖到：

`./.runtime/status.json`

你也可以手动写入它来预览界面。

## 快速开始

### 1. 启动桌宠 app

```bash
./scripts/launch-light-app.sh
```

第一次启动会编译并在后台运行 app。

如果你想前台直接跑：

```bash
swift run ClaudeLight
```

### 2. 用带 plugin 的 Claude Code 启动会话

```bash
./scripts/run-claude-with-light.sh
```

这条命令等价于：

```bash
claude --plugin-dir ./claude-status-light-plugin
```

这样 Claude Code 的 hooks 会自动更新灯的状态。

## 全局安装 Claude plugin

如果你希望以后直接用 `claude` 就自动带这个灯，不想每次写 `--plugin-dir`，用这个：

```bash
./scripts/install-global-plugin.sh
```

它会做三件事：

1. 把仓库里的 plugin 以 symlink 方式挂到 `~/.agents/plugins/plugins/claude-status-light`
2. 在 `~/.agents/plugins/.claude-plugin/marketplace.json` 里注册个人 marketplace 条目
3. 调用 `claude plugins install claude-status-light@personal`

装好以后，正常直接运行：

```bash
claude
```

就会自动加载这个 plugin。

查看全局安装状态：

```bash
python3 ./scripts/manage-global-plugin.py status
```

卸载：

```bash
./scripts/uninstall-global-plugin.sh
```

如果你只想做 dry run，可以加：

```bash
python3 ./scripts/manage-global-plugin.py install --skip-claude --home ./.runtime/fake-home
```

## Xcode 工程

仓库里已经带好可直接运行的 macOS 工程：

`ClaudeStatusLight.xcodeproj`

打开后直接运行 `ClaudeStatusLight` target 即可。它复用当前 `Sources/` 里的代码，不会和 Swift Package 维护两份源文件。

如果你想导出一个可直接双击启动的 `.app`：

```bash
./scripts/build-release-app.sh
```

导出结果会放在：

```bash
~/Applications/ClaudeStatusLight.app
```

以后你直接双击这个 app 就可以运行，不用每次都打开工程。

如果你想自定义导出位置，也可以在运行前覆盖：

```bash
CLAUDE_STATUS_LIGHT_OUTPUT_DIR="/your/output/folder" ./scripts/build-release-app.sh
```

如果你想顺手打一个可分享的 zip 包：

```bash
./scripts/package-release-zip.sh
```

导出结果会放在：

```bash
./dist/ClaudeStatusLight-macOS.zip
```

## 日常使用建议

第一次把 app 跑起来以后，建议做这两件事：

1. 在菜单里打开 `Launch at Login`
2. 把桌宠拖到你顺手的位置

这个版本会自动记住你最后一次拖动后的悬浮位置；如果哪天跑偏了，可以在菜单里点 `Reset Floating Light Position`。

## 手动预览三种状态

```bash
./scripts/demo-status.sh idle
./scripts/demo-status.sh working
./scripts/demo-status.sh approval
```

也可以直接从菜单栏里的 `Preview Status` 切换。

## Hook 映射

- `UserPromptSubmit` -> Working
- `PreToolUse` -> Working
- `PostToolUse` -> Working
- `Notification.permission_prompt` -> Awaiting you
- `Notification.idle_prompt` -> Idle
- `Notification.elicitation_dialog` -> Awaiting you
- `Stop` -> Idle
- `SessionEnd` -> Idle

## 当前实现取舍

- 这是一个可以直接跑的本地工具，不依赖你先改全局 `~/.claude/settings.json`
- plugin 默认通过 `--plugin-dir` 注入，适合先验证体验
- `approval` 恢复到 `working` 主要依赖后续 hook 事件，所以在某些工具执行阶段，红灯可能会停留到该工具结束

## 最终产物

- app: `~/Applications/ClaudeStatusLight.app`
- zip: `./dist/ClaudeStatusLight-macOS.zip`

## License

MIT © Youcheng Wang

---

[English](README.md)
