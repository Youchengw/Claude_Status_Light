#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VALID_STATUSES = {"idle", "working", "approval"}
APPROVAL_SOURCES = {"permission-prompt", "elicitation-dialog"}
STALE_APPROVAL_GRACE_SECONDS = 0.5


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


def read_existing_snapshot(status_file: Path) -> dict[str, Any]:
    try:
        with status_file.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def parse_iso8601(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None

    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def should_ignore_update(existing: dict[str, Any], incoming_status: str, incoming_source: str, now: datetime) -> bool:
    current_status = existing.get("status")
    current_source = existing.get("source")
    current_updated_at = parse_iso8601(existing.get("updated_at"))

    if incoming_status != "approval" or incoming_source not in APPROVAL_SOURCES:
        return False

    if current_status != "working" or current_source != "user-prompt-submit":
        return False

    if current_updated_at is None:
        return False

    age_seconds = (now - current_updated_at).total_seconds()
    return 0 <= age_seconds <= STALE_APPROVAL_GRACE_SECONDS


def _log_timing(status_file: Path, status: str, source: str, elapsed_ms: float) -> None:
    """Write a one-line timing record to a debug log for latency profiling."""
    try:
        log_path = status_file.parent / "timing.log"
        ts = datetime.now(timezone.utc).isoformat()
        line = f"{ts} status={status} source={source} elapsed_ms={elapsed_ms:.1f}\n"
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(line)
    except Exception:
        pass  # never let timing interfere with the hook


def main() -> int:
    import time
    t0 = time.perf_counter()

    status = sys.argv[1] if len(sys.argv) > 1 else "idle"
    source = sys.argv[2] if len(sys.argv) > 2 else "hook"
    detail_arg = sys.argv[3] if len(sys.argv) > 3 else None

    if status not in VALID_STATUSES:
        print(json.dumps({"systemMessage": f"Unknown status: {status}"}))
        return 0

    payload = read_stdin_json()

    status_file = resolve_status_file()
    status_file.parent.mkdir(parents=True, exist_ok=True)
    existing_snapshot = read_existing_snapshot(status_file)
    now = datetime.now(timezone.utc)

    if should_ignore_update(existing_snapshot, status, source, now):
        _log_timing(status_file, status, source, (time.perf_counter() - t0) * 1000)
        print("{}")
        return 0

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

    _log_timing(status_file, status, source, (time.perf_counter() - t0) * 1000)

    print("{}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
