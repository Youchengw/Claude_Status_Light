"""Render the pixel-art pet + traffic light onto a QPainter."""

from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QBrush, QColor, QPainter

from constants import (
    ACCENT_COLOR,
    BODY_PIXELS,
    EYE_BLINK_LEFT,
    EYE_BLINK_RIGHT,
    EYE_COLOR,
    EYE_LEFT,
    EYE_RIGHT,
    HOUSING_COLOR,
    HOUSING_INNER_COLOR,
    LAMP_OFF_COLOR,
    LEFT_ARM,
    LEGS,
    PET_HEIGHT,
    PET_WIDTH,
    SKIN_COLOR,
    Status,
    TRAFFIC_GREEN,
    TRAFFIC_LIGHT_HEIGHT,
    TRAFFIC_HOUSING,
    TRAFFIC_INNER,
    TRAFFIC_LIGHT_WIDTH,
    TRAFFIC_RED,
    TRAFFIC_YELLOW,
)


def qcolor(rgb: tuple[int, int, int]) -> QColor:
    return QColor(*rgb)


def draw_pixel_rects(
    painter: QPainter,
    rects: list[tuple[int, int, int, int]],
    color: QColor,
    pixel_size: int,
    origin_x: int = 0,
    origin_y: int = 0,
) -> None:
    painter.setBrush(QBrush(color))
    painter.setPen(Qt.PenStyle.NoPen)
    for x, y, w, h in rects:
        painter.drawRect(
            QRect(origin_x + x * pixel_size, origin_y + y * pixel_size,
                  w * pixel_size, h * pixel_size)
        )


def draw_traffic_light(
    painter: QPainter,
    status: Status,
    pixel_size: int = 4,
    origin_x: int = 0,
    origin_y: int = 0,
) -> None:
    # Housing
    draw_pixel_rects(painter, TRAFFIC_HOUSING, qcolor(HOUSING_COLOR),
                     pixel_size, origin_x, origin_y)
    draw_pixel_rects(painter, TRAFFIC_INNER, qcolor(HOUSING_INNER_COLOR),
                     pixel_size, origin_x, origin_y)

    # Lamps — highlight the active one
    for lamp_rects, lamp_status in [
        (TRAFFIC_RED, Status.approval),
        (TRAFFIC_YELLOW, Status.working),
        (TRAFFIC_GREEN, Status.idle),
    ]:
        color = (
            ACCENT_COLOR[status]
            if status == lamp_status
            else LAMP_OFF_COLOR[lamp_status]
        )
        draw_pixel_rects(painter, lamp_rects, qcolor(color),
                         pixel_size, origin_x, origin_y)


def draw_pet_body(
    painter: QPainter,
    is_blinking: bool,
    arm_offsets: tuple[int, int] = (0, 0),
    pixel_size: int = 6,
    origin_x: int = 0,
    origin_y: int = 0,
) -> None:
    # Body
    draw_pixel_rects(painter, BODY_PIXELS, qcolor(SKIN_COLOR),
                     pixel_size, origin_x, origin_y)

    # Left arm (animated independently)
    ax, ay = arm_offsets
    draw_pixel_rects(
        painter, [LEFT_ARM], qcolor(SKIN_COLOR),
        pixel_size, origin_x + ax, origin_y + ay,
    )

    # Eyes — blink shrinks to 1px tall
    eye_left = EYE_BLINK_LEFT if is_blinking else EYE_LEFT
    eye_right = EYE_BLINK_RIGHT if is_blinking else EYE_RIGHT
    draw_pixel_rects(
        painter, [eye_left, eye_right], qcolor(EYE_COLOR),
        pixel_size, origin_x, origin_y,
    )

    # Legs
    draw_pixel_rects(painter, LEGS, qcolor(SKIN_COLOR),
                     pixel_size, origin_x, origin_y)


def pet_scene_size(pet_pixel_size: int = 6, tl_pixel_size: int = 4) -> tuple[int, int]:
    """Return (width, height) needed to draw the full pet + traffic light."""
    pet_w = PET_WIDTH * pet_pixel_size
    pet_h = PET_HEIGHT * pet_pixel_size
    tl_w = TRAFFIC_LIGHT_WIDTH * tl_pixel_size
    tl_h = TRAFFIC_LIGHT_HEIGHT * tl_pixel_size
    return max(pet_w, tl_w), pet_h + tl_h + tl_pixel_size * 2


def draw_full_scene(
    painter: QPainter,
    status: Status,
    is_blinking: bool,
    float_offset: int = 0,
    arm_offsets: tuple[int, int] = (0, 0),
    pet_pixel_size: int = 6,
    tl_pixel_size: int = 4,
) -> None:
    """Draw traffic light above pet, centered.  Called from paintEvent."""
    total_w, total_h = pet_scene_size(pet_pixel_size, tl_pixel_size)
    pet_w = PET_WIDTH * pet_pixel_size
    tl_w = TRAFFIC_LIGHT_WIDTH * tl_pixel_size

    tl_ox = (total_w - tl_w) // 2
    tl_oy = 0
    pet_ox = (total_w - pet_w) // 2
    pet_oy = tl_pixel_size * TRAFFIC_LIGHT_HEIGHT + tl_pixel_size * 2 + float_offset

    draw_traffic_light(painter, status, tl_pixel_size, tl_ox, tl_oy)
    draw_pet_body(painter, is_blinking, arm_offsets, pet_pixel_size, pet_ox, pet_oy)
