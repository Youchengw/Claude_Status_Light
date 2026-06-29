#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VALID_STATUSES = {"idle", "working", "approval"}


def resolve_status_file() -> Path:
    override = os.environ.get("CLAUDE_STATUS_LIGHT_FILE", "").strip()
    if override:
        return Path(override)

    if sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
        dirname = "ClaudeStatusLight"
    elif sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming")))
        dirname = "ClaudeLight"
    else:  # Linux / BSD
        xdg = os.environ.get("XDG_DATA_HOME")
        base = Path(xdg) if xdg else Path.home() / ".local" / "share"
        dirname = "ClaudeLight"

    return base / dirname / "status.json"


def read_stdin_json() -> dict[str, Any]:
    raw = sys.stdin.read().strip()
    if not raw:
        return {}

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def compact(value: Any) -> Any:
    if value in (None, "", []):
        return None
    return value


def main() -> int:
    status = sys.argv[1] if len(sys.argv) > 1 else "idle"
    source = sys.argv[2] if len(sys.argv) > 2 else "hook"
    detail_arg = sys.argv[3] if len(sys.argv) > 3 else None

    if status not in VALID_STATUSES:
        print(json.dumps({"systemMessage": f"Unknown status: {status}"}))
        return 0

    payload = read_stdin_json()

    status_file = resolve_status_file()
    status_file.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)

    snapshot = {
        "status": status,
        "updated_at": now.isoformat(),
        "source": source,
        "detail": compact(detail_arg) or compact(payload.get("reason")) or compact(payload.get("user_prompt")),
        "session_id": compact(payload.get("session_id")),
        "hook_event_name": compact(payload.get("hook_event_name")),
        "tool_name": compact(payload.get("tool_name")),
        "cwd": compact(payload.get("cwd")),
    }

    with status_file.open("w", encoding="utf-8") as handle:
        json.dump(snapshot, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")

    print("{}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
