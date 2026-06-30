"""System tray icon with menu via QSystemTrayIcon — no extra dependencies."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QBrush, QColor, QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import QMenu, QSystemTrayIcon

from constants import Status


def _make_tray_icon() -> QIcon:
    """Draw a 32×32 pixel-art pet silhouette (matches MenuBarStatusView).

    Uses QPainter on a QPixmap instead of PIL so we can drop the Pillow
    and pystray dependencies entirely.
    """
    q = 1.5
    pixmap = QPixmap(int(18 * q * 2), int(10 * q * 2))
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

    c = QColor(24, 24, 24, 255)  # dark silhouette
    painter.setBrush(QBrush(c))
    painter.setPen(Qt.PenStyle.NoPen)

    def _r(x: int, y: int, w: int, h: int) -> None:
        painter.drawRect(
            int(x * q * 2), int(y * q * 2),
            int(w * q * 2) - 1, int(h * q * 2) - 1,
        )

    # Body
    _r(3, 0, 12, 7)
    # Arms
    _r(1, 4, 2, 2)
    _r(15, 4, 2, 2)
    # Legs
    _r(5, 7, 1, 2)
    _r(7, 7, 1, 2)
    _r(10, 7, 1, 2)
    _r(12, 7, 1, 2)

    painter.end()
    return QIcon(pixmap)


class SystemTray(QSystemTrayIcon):
    """Qt-native system tray icon with a context menu.

    Replaces the old pystray-based tray so that everything runs in the
    Qt main thread — no cross-thread issues, and menus work reliably
    on Linux desktops (GNOME, KDE, Xfce, …).
    """

    def __init__(
        self,
        on_show: callable,
        on_hide: callable,
        on_reset: callable,
        on_set_status: callable,
        on_quit: callable,
    ) -> None:
        super().__init__()
        self._on_show = on_show
        self._on_hide = on_hide
        self._on_reset = on_reset
        self._on_set_status = on_set_status
        self._on_quit = on_quit
        self._visible = True

        self.setIcon(_make_tray_icon())
        self.setToolTip("ClaudeLight")
        self._rebuild_menu()
        self.show()

    # ── public ─────────────────────────────────────────────────

    def stop(self) -> None:
        self.hide()

    # ── private ────────────────────────────────────────────────

    def _rebuild_menu(self) -> None:
        menu = QMenu()

        toggle_label = (
            "Hide Floating Light" if self._visible else "Show Floating Light"
        )
        menu.addAction(toggle_label, self._toggle)
        menu.addAction("Reset Position", self._on_reset)
        menu.addSeparator()

        preview_menu = menu.addMenu("Preview Status")
        preview_menu.addAction("Idle", lambda: self._on_set_status(Status.idle))
        preview_menu.addAction("Working", lambda: self._on_set_status(Status.working))
        preview_menu.addAction("Approval", lambda: self._on_set_status(Status.approval))

        menu.addSeparator()
        menu.addAction("Quit", self._on_quit)

        self.setContextMenu(menu)

    def _toggle(self) -> None:
        if self._visible:
            self._on_hide()
            self._visible = False
        else:
            self._on_show()
            self._visible = True
        self._rebuild_menu()
