"""Shared constants — color values and pixel coordinates match the macOS SwiftUI app."""

from enum import Enum
from dataclasses import dataclass
from typing import NamedTuple


class Status(str, Enum):
    idle = "idle"
    working = "working"
    approval = "approval"


# Match ClaudeStatusStore.swift accentColor / TrafficLamp onColor
ACCENT_COLOR = {
    Status.idle: (97, 247, 148),      # rgb(0.38, 0.97, 0.58)
    Status.working: (255, 199, 59),   # rgb(1.00, 0.78, 0.23)
    Status.approval: (255, 89, 107),  # rgb(1.00, 0.35, 0.42)
}

# Match TrafficLamp offColor
LAMP_OFF_COLOR = {
    Status.idle: (13, 61, 31),        # rgb(0.05, 0.24, 0.12)
    Status.working: (87, 56, 10),     # rgb(0.34, 0.22, 0.04)
    Status.approval: (82, 20, 28),    # rgb(0.32, 0.08, 0.11)
}

# Pixel pet colours (match PixelClaudePetView / PixelTrafficLightView)
SKIN_COLOR = (235, 148, 120)          # rgb(0.92, 0.58, 0.47)
EYE_COLOR = (20, 20, 20)              # black 0.92 opacity
HOUSING_COLOR = (20, 20, 20)          # black 0.88 opacity
HOUSING_INNER_COLOR = (18, 18, 16)    # 0.08, 0.08, 0.07

# Traffic light pixel layout (matches PixelTrafficLightView)
# width=17, height=5, pixel_size → scaled by rendering
TRAFFIC_LIGHT_WIDTH = 17
TRAFFIC_LIGHT_HEIGHT = 5
TRAFFIC_HOUSING = [(0, 0, 17, 5)]                     # x, y, w, h
TRAFFIC_INNER = [(1, 1, 15, 3)]
TRAFFIC_RED = [(2, 2, 4, 2)]
TRAFFIC_YELLOW = [(6, 2, 4, 2)]
TRAFFIC_GREEN = [(10, 2, 4, 2)]

# Body pixel layout (matches PixelClaudePetView bodyPixels)
# width=18, height=10
PET_WIDTH = 18
PET_HEIGHT = 10
BODY_PIXELS = [
    (3, 0, 12, 7),    # main body
    (15, 4, 2, 2),    # right arm
]
EYE_LEFT = (6, 2, 1, 2)
EYE_RIGHT = (11, 2, 1, 2)
EYE_BLINK_LEFT = (6, 3, 1, 1)
EYE_BLINK_RIGHT = (11, 3, 1, 1)
LEGS = [
    (5, 7, 1, 2),
    (7, 7, 1, 2),
    (10, 7, 1, 2),
    (12, 7, 1, 2),
]
LEFT_ARM = (1, 4, 2, 2)


class PixelRect(NamedTuple):
    x: int
    y: int
    width: int
    height: int
    color: tuple[int, int, int]
