"""Watch status.json with watchdog and emit Qt signals on change."""

import json
import os
from pathlib import Path
from typing import Any

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
        self._last_data: dict | None = None
        self._poll_timer: Any = None  # QTimer

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

        # Polling safety net — catches events that watchdog may miss.
        from PyQt6.QtCore import QTimer
        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._poll)
        self._poll_timer.start(500)

        self._started = True

    def stop(self) -> None:
        if not self._started:
            return
        if self._poll_timer is not None:
            self._poll_timer.stop()
        self._observer.stop()
        self._observer.join(timeout=2)
        self._started = False

    def force_read(self) -> None:
        self._read()

    # ── private ──────────────────────────────────────────────

    def _on_change(self) -> None:
        self._read()

    def _poll(self) -> None:
        self._read()

    def _read(self) -> None:
        try:
            data = json.loads(self._file.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return

        # Only emit if the content actually changed.
        if data != self._last_data:
            self._last_data = data
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
