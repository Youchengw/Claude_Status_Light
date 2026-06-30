#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PLUGIN_NAME = "claude-status-light"
REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_SOURCE = REPO_ROOT / "claude-status-light-plugin"


def detect_python() -> str:
    """Return the best available Python command for this system.

    Tries ``python3`` first (standard on macOS / Linux),
    falls back to ``python`` (standard on Windows),
    then falls back to the current interpreter.
    """
    for cmd in ("python3", "python"):
        if shutil.which(cmd):
            return cmd
    return sys.executable


def patch_hooks_json(plugin_path: Path) -> None:
    """Replace ``python3`` with the platform-appropriate Python command.

    Only touches the *installed copy* of hooks.json — never the repo
    source.  On macOS / Linux the detected command is almost always
    ``python3`` so this is a no-op; on Windows it patches ``python3``
    → ``python``.
    """
    hooks_path = plugin_path / "hooks" / "hooks.json"
    if not hooks_path.exists():
        return

    python_cmd = detect_python()
    if python_cmd == "python3":
        return  # already correct

    content = hooks_path.read_text(encoding="utf-8")
    # Replace ``python3 `` (with trailing space, inside quotes) so we
    # only touch command invocations, not random occurrences of the
    # string "python3".
    patched = content.replace('"python3 "', f'"{python_cmd} "')
    if patched != content:
        hooks_path.write_text(patched, encoding="utf-8")
        print(f"  Patched hooks.json: python3 → {python_cmd}")


@dataclass
class Paths:
    home: Path
    agents_root: Path
    marketplace_root: Path
    marketplace_path: Path
    marketplace_plugins_root: Path
    installed_plugin_path: Path


def build_paths(home_override: str | None) -> Paths:
    home = Path(home_override).expanduser().resolve() if home_override else Path.home()
    agents_root = home / ".agents" / "plugins"
    return Paths(
        home=home,
        agents_root=agents_root,
        marketplace_root=agents_root / ".claude-plugin",
        marketplace_path=agents_root / ".claude-plugin" / "marketplace.json",
        marketplace_plugins_root=agents_root / "plugins",
        installed_plugin_path=agents_root / "plugins" / PLUGIN_NAME,
    )


def ensure_personal_marketplace(paths: Paths) -> dict[str, Any]:
    if paths.marketplace_path.exists():
        with paths.marketplace_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    else:
        data = {
            "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
            "name": "personal",
            "description": "Personal Claude Code plugins installed from local sources.",
            "owner": {
                "name": os.environ.get("USER", "Local User"),
            },
            "plugins": [],
        }

    data.setdefault("name", "personal")
    data.setdefault("$schema", "https://anthropic.com/claude-code/marketplace.schema.json")
    data.setdefault("description", "Personal Claude Code plugins installed from local sources.")
    data.setdefault("owner", {})
    data["owner"].setdefault("name", os.environ.get("USER", "Local User"))
    data.setdefault("plugins", [])
    data.pop("interface", None)
    return data


def write_marketplace(paths: Paths, data: dict[str, Any]) -> None:
    paths.marketplace_root.mkdir(parents=True, exist_ok=True)
    with paths.marketplace_path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def sync_plugin_source(paths: Paths, mode: str) -> None:
    paths.marketplace_plugins_root.mkdir(parents=True, exist_ok=True)

    if paths.installed_plugin_path.exists() or paths.installed_plugin_path.is_symlink():
        current_target = None
        if paths.installed_plugin_path.is_symlink():
            current_target = paths.installed_plugin_path.resolve()
        if current_target == PLUGIN_SOURCE.resolve():
            return
        remove_path(paths.installed_plugin_path)

    if mode == "symlink":
        paths.installed_plugin_path.symlink_to(PLUGIN_SOURCE)
    else:
        shutil.copytree(PLUGIN_SOURCE, paths.installed_plugin_path)


def upsert_marketplace_entry(paths: Paths) -> None:
    data = ensure_personal_marketplace(paths)
    entry = {
        "name": PLUGIN_NAME,
        "description": "Traffic-light status hooks for Claude Code, paired with the floating macOS companion app.",
        "author": {
            "name": "Youcheng Wang",
        },
        "source": f"./plugins/{PLUGIN_NAME}",
        "category": "productivity",
    }

    plugins = data["plugins"]
    for index, plugin in enumerate(plugins):
        if plugin.get("name") == PLUGIN_NAME:
            plugins[index] = entry
            break
    else:
        plugins.append(entry)

    write_marketplace(paths, data)


def remove_marketplace_entry(paths: Paths) -> None:
    data = ensure_personal_marketplace(paths)
    data["plugins"] = [plugin for plugin in data["plugins"] if plugin.get("name") != PLUGIN_NAME]
    write_marketplace(paths, data)


def run_claude(args: list[str], home: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["HOME"] = str(home)
    return subprocess.run(args, env=env, text=True, capture_output=True, check=False)


def marketplace_registered(paths: Paths) -> bool:
    result = run_claude(["claude", "plugins", "marketplace", "list"], paths.home)
    return result.returncode == 0 and "personal" in result.stdout


def ensure_marketplace_registered(paths: Paths) -> None:
    if not marketplace_registered(paths):
        result = run_claude(
            ["claude", "plugins", "marketplace", "add", str(paths.agents_root)],
            paths.home,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "claude plugins marketplace add failed")

    refresh = run_claude(["claude", "plugins", "marketplace", "update", "personal"], paths.home)
    if refresh.returncode != 0:
        raise RuntimeError(refresh.stderr.strip() or refresh.stdout.strip() or "claude plugins marketplace update failed")


def plugin_installed(paths: Paths) -> bool:
    result = run_claude(["claude", "plugins", "list"], paths.home)
    return result.returncode == 0 and PLUGIN_NAME in result.stdout


def install_plugin(paths: Paths) -> None:
    ensure_marketplace_registered(paths)
    install_target = f"{PLUGIN_NAME}@personal"
    if plugin_installed(paths):
        update = run_claude(["claude", "plugins", "update", PLUGIN_NAME], paths.home)
        if update.returncode != 0:
            combined_output = f"{update.stdout}\n{update.stderr}".lower()
            if "not found" in combined_output:
                install = run_claude(["claude", "plugins", "install", install_target], paths.home)
                if install.returncode != 0:
                    raise RuntimeError(install.stderr.strip() or install.stdout.strip() or "claude plugins install failed")
            else:
                raise RuntimeError(update.stderr.strip() or update.stdout.strip() or "claude plugins update failed")
    else:
        install = run_claude(["claude", "plugins", "install", install_target], paths.home)
        if install.returncode != 0:
            raise RuntimeError(install.stderr.strip() or install.stdout.strip() or "claude plugins install failed")

    enable = run_claude(["claude", "plugins", "enable", PLUGIN_NAME], paths.home)
    if enable.returncode != 0 and "already enabled" not in (enable.stdout + enable.stderr).lower():
        raise RuntimeError(enable.stderr.strip() or enable.stdout.strip() or "claude plugins enable failed")


def uninstall_plugin(paths: Paths) -> None:
    if plugin_installed(paths):
        result = run_claude(["claude", "plugins", "uninstall", PLUGIN_NAME], paths.home)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "claude plugins uninstall failed")


def command_install(paths: Paths, mode: str, skip_claude: bool) -> None:
    sync_plugin_source(paths, mode)
    # Patch hooks.json for platforms where ``python3`` is not the
    # standard command (e.g. Windows).  Skip symlinks so the repo
    # source stays pristine.
    if not paths.installed_plugin_path.is_symlink():
        patch_hooks_json(paths.installed_plugin_path)
    upsert_marketplace_entry(paths)
    if not skip_claude:
        install_plugin(paths)


def command_uninstall(paths: Paths, skip_claude: bool) -> None:
    if not skip_claude:
        uninstall_plugin(paths)
    remove_marketplace_entry(paths)
    if paths.installed_plugin_path.exists() or paths.installed_plugin_path.is_symlink():
        remove_path(paths.installed_plugin_path)


def command_status(paths: Paths) -> None:
    data = ensure_personal_marketplace(paths)
    entry = next((plugin for plugin in data["plugins"] if plugin.get("name") == PLUGIN_NAME), None)
    result = {
        "home": str(paths.home),
        "plugin_source": str(PLUGIN_SOURCE),
        "marketplace_path": str(paths.marketplace_path),
        "installed_plugin_path": str(paths.installed_plugin_path),
        "marketplace_entry_present": bool(entry),
        "installed_plugin_exists": paths.installed_plugin_path.exists() or paths.installed_plugin_path.is_symlink(),
        "claude_plugin_installed": plugin_installed(paths),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install or uninstall Claude Status Light into Claude Code's personal marketplace.")
    parser.add_argument("command", choices=["install", "uninstall", "status"])
    parser.add_argument("--mode", choices=["symlink", "copy"], default="symlink")
    parser.add_argument("--skip-claude", action="store_true", help="Skip calling `claude plugins ...`; useful for dry runs and tests.")
    parser.add_argument("--home", help="Override HOME for testing or non-default installs.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths = build_paths(args.home)

    if not PLUGIN_SOURCE.exists():
        print(f"Plugin source not found: {PLUGIN_SOURCE}", file=sys.stderr)
        return 1

    try:
        if args.command == "install":
            command_install(paths, args.mode, args.skip_claude)
        elif args.command == "uninstall":
            command_uninstall(paths, args.skip_claude)
        else:
            command_status(paths)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
