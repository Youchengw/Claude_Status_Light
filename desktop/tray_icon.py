"""System tray icon with menu, mirroring the macOS menu bar experience."""

from __future__ import annotations

from PIL import Image, ImageDraw

from constants import Status

try:
    import pystray
except ImportError:
    pystray = None  # type: ignore[assignment]


def _make_tray_image() -> Image.Image:
    """Draw a 32×32 pixel-art pet silhouette (matches MenuBarStatusView)."""
    q = 1.5
    w, h = 18, 10
    img = Image.new("RGBA", (int(w * q * 2), int(h * q * 2)), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    c = (24, 24, 24, 255)  # dark silhouette

    def rect(x, y, rw, rh):
        draw.rectangle(
            [x * q * 2, y * q * 2, (x + rw) * q * 2 - 1, (y + rh) * q * 2 - 1],
            fill=c,
        )

    # Body
    rect(3, 0, 12, 7)
    # Arms
    rect(1, 4, 2, 2)
    rect(15, 4, 2, 2)
    # Eyes (cutouts — draw in background color)
    draw.rectangle([6 * q * 2, 2 * q * 2, (6 + 1) * q * 2 - 1, (2 + 2) * q * 2 - 1],
                   fill=(0, 0, 0, 0))
    draw.rectangle([11 * q * 2, 2 * q * 2, (11 + 1) * q * 2 - 1, (2 + 2) * q * 2 - 1],
                   fill=(0, 0, 0, 0))
    # Legs
    rect(5, 7, 1, 2)
    rect(7, 7, 1, 2)
    rect(10, 7, 1, 2)
    rect(12, 7, 1, 2)

    return img


class SystemTray:
    """Wraps pystray.Icon with a context menu controlling the floating window."""

    def __init__(
        self,
        on_show: callable,
        on_hide: callable,
        on_reset: callable,
        on_set_status: callable,
        on_quit: callable,
    ) -> None:
        if pystray is None:
            raise RuntimeError("pystray is not installed")
        self._on_show = on_show
        self._on_hide = on_hide
        self._on_reset = on_reset
        self._on_set_status = on_set_status
        self._on_quit = on_quit
        self._visible = True

        self._icon = pystray.Icon(
            "ClaudeLight",
            _make_tray_image(),
            "ClaudeLight",
            menu=self._build_menu(),
        )

    def run_detached(self) -> None:
        import threading
        threading.Thread(target=self._icon.run, daemon=True).start()

    def stop(self) -> None:
        self._icon.stop()

    def _build_menu(self) -> pystray.Menu:
        return pystray.Menu(
            pystray.MenuItem(
                "Hide Floating Light" if self._visible else "Show Floating Light",
                self._toggle,
            ),
            pystray.MenuItem("Reset Position", self._on_reset),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Preview Status", pystray.Menu(
                pystray.MenuItem("Idle", lambda: self._on_set_status(Status.idle)),
                pystray.MenuItem("Working", lambda: self._on_set_status(Status.working)),
                pystray.MenuItem("Approval", lambda: self._on_set_status(Status.approval)),
            )),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self._on_quit),
        )

    def _toggle(self) -> None:
        if self._visible:
            self._on_hide()
            self._visible = False
            self._icon.menu = self._build_menu()
        else:
            self._on_show()
            self._visible = True
            self._icon.menu = self._build_menu()
