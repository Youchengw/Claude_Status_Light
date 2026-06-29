"""Watch status.json with watchdog and emit Qt signals on change."""

import json
import os
from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


def status_file_path() -> Path:
    """Return the platform-specific status.json path.

    Priority: CLAUDE_STATUS_LIGHT_FILE env var > platform default.
    """
    override = os.environ.get("CLAUDE_STATUS_LIGHT_FILE", "").strip()
    if override:
        return Path(override)

    import sys

    if sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    elif sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:  # Linux / BSD
        xdg = os.environ.get("XDG_DATA_HOME")
        base = Path(xdg) if xdg else Path.home() / ".local" / "share"

    # Keep "ClaudeStatusLight" on macOS for backward compatibility.
    dirname = "ClaudeStatusLight" if sys.platform == "darwin" else "ClaudeLight"
    return base / dirname / "status.json"


class StatusWatcher(QObject):
    """Monitors status.json and emits status_changed(str, dict)."""

    status_changed = pyqtSignal(str, dict)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._file = status_file_path()
        self._observer = Observer()
        self._started = False

    @property
    def file_path(self) -> Path:
        return self._file

    def start(self) -> None:
        if self._started:
            return
        self._file.parent.mkdir(parents=True, exist_ok=True)
        self._read()
        handler = _Handler(self._on_change)
        self._observer.schedule(handler, str(self._file.parent), recursive=False)
        self._observer.start()
        self._started = True

    def stop(self) -> None:
        if not self._started:
            return
        self._observer.stop()
        self._observer.join(timeout=2)
        self._started = False

    def force_read(self) -> None:
        self._read()

    # ── private ──────────────────────────────────────────────

    def _on_change(self) -> None:
        self._read()

    def _read(self) -> None:
        try:
            data = json.loads(self._file.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return

        status = data.get("status", "idle")
        self.status_changed.emit(status, data)


class _Handler(FileSystemEventHandler):
    def __init__(self, callback) -> None:
        super().__init__()
        self._callback = callback

    def on_modified(self, event) -> None:
        if event.is_directory:
            return
        self._callback()

    def on_created(self, event) -> None:
        if event.is_directory:
            return
        self._callback()
