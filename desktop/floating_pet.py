"""Borderless always-on-top floating window with the pixel pet + traffic light."""

import math
import time

from PyQt6.QtCore import (
    QPoint,
    QSettings,
    Qt,
    QTimer,
)
from PyQt6.QtGui import QMouseEvent, QPainter
from PyQt6.QtWidgets import QWidget

from constants import Status
from pixel_renderer import draw_full_scene, pet_scene_size


# Animation timing (match macOS TrafficLightPanelView + PixelClaudePetView)
FLOAT_PERIOD = 2.8          # seconds for one idle float cycle
FLOAT_AMPLITUDE = 3         # pixels
BLINK_INTERVAL = 2800       # ms between blinks
BLINK_DURATION = 140        # ms blink stays
PAT_CYCLE = 1.05            # seconds for one head-pat cycle
FRAME_MS = 16               # ~60 fps
PET_PIXEL_SIZE = 6
TL_PIXEL_SIZE = 4


class FloatingPetWindow(QWidget):
    """Always-on-top, borderless, draggable pixel-pet window."""

    def __init__(self) -> None:
        super().__init__()
        self._status = Status.idle
        self._is_blinking = False
        self._is_hovering = False
        self._float_offset = 0.0
        self._arm_offsets = (0, 0)
        self._last_frame_time = time.monotonic()
        self._dragging = False
        self._drag_offset = QPoint()

        w, h = pet_scene_size(PET_PIXEL_SIZE, TL_PIXEL_SIZE)
        pad = 12
        self._window_w = w + pad
        self._window_h = h + pad + 28  # +28 for status caption area
        self._scene_w = w
        self._scene_h = h

        self._setup_window()
        self._restore_position()
        self._start_animation()

    # ── public ───────────────────────────────────────────────

    def set_status(self, status: Status) -> None:
        if status != self._status:
            self._status = status
            self.update()

    # ── window setup ─────────────────────────────────────────

    def _setup_window(self) -> None:
        self.setWindowTitle("ClaudeLight")
        self.setFixedSize(self._window_w, self._window_h)
        self.setWindowFlags(
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

    # ── drag ─────────────────────────────────────────────────

    def mousePressEvent(self, event: QMouseEvent | None) -> None:
        if event and event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent | None) -> None:
        if self._dragging and event:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent | None) -> None:
        if self._dragging:
            self._dragging = False
            self._save_position()
            if event:
                event.accept()

    # ── hover ────────────────────────────────────────────────

    def enterEvent(self, event) -> None:
        self._is_hovering = True

    def leaveEvent(self, event) -> None:
        self._is_hovering = False

    # ── position persistence ─────────────────────────────────

    def _save_position(self) -> None:
        s = QSettings("ClaudeLight", "ClaudeLight")
        s.setValue("panel/x", self.x())
        s.setValue("panel/y", self.y())

    def _restore_position(self) -> None:
        s = QSettings("ClaudeLight", "ClaudeLight")
        x = s.value("panel/x")
        y = s.value("panel/y")
        if x is not None and y is not None:
            self.move(int(x), int(y))
        else:
            # Default: bottom-right corner
            from PyQt6.QtGui import QGuiApplication
            screen = QGuiApplication.primaryScreen()
            if screen:
                geo = screen.availableGeometry()
                self.move(
                    geo.right() - self._window_w - 28,
                    geo.center().y() - self._window_h // 2,
                )

    def closeEvent(self, event) -> None:
        self._save_position()
        super().closeEvent(event)

    # ── animation loop ───────────────────────────────────────

    def _start_animation(self) -> None:
        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._tick)
        self._anim_timer.start(FRAME_MS)

        self._blink_timer = QTimer(self)
        self._blink_timer.timeout.connect(self._trigger_blink)
        self._blink_timer.start(BLINK_INTERVAL)

    def _trigger_blink(self) -> None:
        self._is_blinking = True
        QTimer.singleShot(BLINK_DURATION, self._end_blink)

    def _end_blink(self) -> None:
        self._is_blinking = False

    def _tick(self) -> None:
        now = time.monotonic()
        delta = now - self._last_frame_time
        self._last_frame_time = now

        # Idle float (match macOS sin animation)
        if self._status == Status.idle:
            phase = (now % FLOAT_PERIOD) / FLOAT_PERIOD
            self._float_offset = math.sin(phase * math.pi * 2) * FLOAT_AMPLITUDE
        else:
            self._float_offset = 0

        # Head-pat (match macOS keyframe animation)
        if self._is_hovering:
            progress = (now % PAT_CYCLE) / PAT_CYCLE
            if progress < 0.25:
                t = progress / 0.25
                self._arm_offsets = (int(t * 6), int(-t * 18))
            elif progress < 0.4:
                self._arm_offsets = (6, -18)
            elif progress < 0.65:
                t = (progress - 0.4) / 0.25
                self._arm_offsets = (int((1 - t) * 6), int(-(1 - t) * 18))
            else:
                self._arm_offsets = (0, 0)
        else:
            self._arm_offsets = (0, 0)

        self.update()

    # ── paint ────────────────────────────────────────────────

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        # Draw scene centered in window
        ox = (self._window_w - self._scene_w) // 2
        oy = (self._window_h - self._scene_h - 28) // 2  # leave room for caption

        painter.save()
        painter.translate(ox, oy)

        draw_full_scene(
            painter,
            self._status,
            self._is_blinking,
            int(self._float_offset),
            self._arm_offsets,
            PET_PIXEL_SIZE,
            TL_PIXEL_SIZE,
        )

        # Status caption (match macOS StatusCaptionView)
        caption_y = self._scene_h + 4
        caption_w = self._scene_w
        caption_h = 20

        painter.setPen(Qt.PenStyle.NoPen)
        from PyQt6.QtGui import QColor
        painter.setBrush(QColor(0, 0, 0, 184))  # 0.72 opacity
        painter.drawRoundedRect(ox, oy + caption_y, caption_w, caption_h, 3, 3)

        from PyQt6.QtGui import QFont
        font = QFont("Consolas", 10, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255, 242))  # 0.95 opacity
        title = {Status.idle: "Idle", Status.working: "Working",
                 Status.approval: "Awaiting you"}[self._status]
        painter.drawText(ox, oy + caption_y, caption_w, caption_h,
                         Qt.AlignmentFlag.AlignCenter, title)

        painter.restore()
        painter.end()
