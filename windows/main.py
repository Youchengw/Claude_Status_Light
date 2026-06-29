"""ClaudeLight for Windows — floating pixel pet + system tray icon."""

import sys

from PyQt6.QtWidgets import QApplication

from constants import Status
from floating_pet import FloatingPetWindow
from status_watcher import StatusWatcher
from tray_icon import SystemTray


class App:
    def __init__(self) -> None:
        self._qt = QApplication(sys.argv)
        self._qt.setQuitOnLastWindowClosed(False)

        self._window = FloatingPetWindow()

        self._watcher = StatusWatcher()
        self._watcher.status_changed.connect(self._on_status)
        self._watcher.start()

        self._tray = SystemTray(
            on_show=self._window.show,
            on_hide=self._window.hide,
            on_reset=self._reset_position,
            on_set_status=self._on_set_status,
            on_quit=self.quit,
        )
        self._tray.run_detached()

        self._window.show()

    def _on_status(self, status_str: str, _data: dict) -> None:
        try:
            s = Status(status_str)
        except ValueError:
            s = Status.idle
        self._window.set_status(s)

    def _on_set_status(self, status: Status) -> None:
        # Write status.json for preview (mirrors macOS menu Preview)
        from status_watcher import status_file_path
        import json
        from datetime import datetime, timezone
        f = status_file_path()
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps({
            "status": status.value,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "source": "menu-preview",
            "detail": "Preview from tray",
        }, indent=2), encoding="utf-8")

    def _reset_position(self) -> None:
        self._window.move(100, 100)

    def quit(self) -> None:
        self._watcher.stop()
        self._tray.stop()
        self._window.close()
        self._qt.quit()

    def run(self) -> int:
        return self._qt.exec()


def main() -> int:
    app = App()
    return app.run()


if __name__ == "__main__":
    raise SystemExit(main())
