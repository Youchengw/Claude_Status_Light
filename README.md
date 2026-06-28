# Claude Status Light

一个给 Claude Code 配的 macOS 状态灯小工具。它会在菜单栏和桌面悬浮窗里显示 Claude 当前状态：

- 绿灯: `休息中`
- 黄灯: `工作中`
- 红灯: `等你回应`

桌面悬浮窗现在是一个像素风 Claude 桌宠，头顶横向红绿灯。

这个仓库包含三部分：

1. `ClaudeStatusLight`：原生 SwiftUI 菜单栏 + 悬浮窗 app
2. `claude-status-light-plugin`：Claude Code plugin，通过 hooks 把状态写到本地 `status.json`
3. `ClaudeStatusLight.xcodeproj`：可直接用 Xcode 打开的 macOS App 工程

## 当前效果

- 常驻 macOS 状态栏
- 默认显示一个始终置顶的桌宠悬浮窗
- 面板可以拖动
- 面板会记住你上次拖到的位置
- 菜单栏菜单里可以隐藏/显示面板
- 支持从菜单里打开/关闭开机自启动
- 支持菜单内手动预览三种状态

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
swift run ClaudeStatusLight
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

- `UserPromptSubmit` -> 黄灯
- `PreToolUse` -> 黄灯
- `PostToolUse` -> 黄灯
- `Notification.permission_prompt` -> 红灯
- `Notification.idle_prompt` -> 绿灯
- `Notification.elicitation_dialog` -> 红灯
- `Stop` -> 绿灯
- `SessionEnd` -> 绿灯

## 当前实现取舍

- 这是一个可以直接跑的本地工具，不依赖你先改全局 `~/.claude/settings.json`
- plugin 默认通过 `--plugin-dir` 注入，适合先验证体验
- `approval` 恢复到 `working` 主要依赖后续 hook 事件，所以在某些工具执行阶段，红灯可能会停留到该工具结束

## 最终产物

- app: `~/Applications/ClaudeStatusLight.app`
- zip: `./dist/ClaudeStatusLight-macOS.zip`

如果你下一步还想继续打磨，可以往这几个方向走：

1. 给这个 Xcode 工程补 app icon、签名和 Archive 导出流程
2. 直接帮你把全局 plugin 安装到当前用户环境里
3. 再补一轮视觉细节，比如更丰富的状态动画或更完整的设置项
