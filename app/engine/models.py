from __future__ import annotations

from enum import Enum, IntEnum
from typing import NewType

import numpy as np

STARTING_POSITION = np.array([1] * 12 + [0] * 8 + [-1] * 12, dtype=np.int8)
SquareT = NewType("SquareT", int)


class Color(Enum):
    BLUE = -1
    RED = 1


class Figure(IntEnum):
    RED_KING = Color.RED.value * 2
    RED_MAN = Color.RED.value
    BLUE_KING = Color.BLUE.value * 2
    BLUE_MAN = Color.BLUE.value
    KING = 2
    MAN = 1
    EMPTY = 0


FIGURE_REPR = {
    Figure.RED_MAN: "r",
    Figure.BLUE_MAN: "b",
    Figure.EMPTY: ".",
    Figure.RED_KING: "R",
    Figure.BLUE_KING: "B",
}
