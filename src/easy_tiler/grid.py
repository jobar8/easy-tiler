"""Grid utilities for easy_tiler."""

import math
from dataclasses import dataclass
from typing import Iterator, Tuple


@dataclass
class Grid:
    width: int  # number of cells in x direction
    height: int  # number of cells in y direction
    x_size: int = 64  # width of each cell in pixels
    y_size: int = 64  # height of each cell in pixels
    origin: Tuple[int, int] = (0, 0)
    x_shift: int = 0
    y_shift: int = 0
    x_skew: float = 0  # skew angle in radians, positive values skew right, negative values skew left
    y_skew: float = 0

    @property
    def skew_angles(self) -> Tuple[float, float]:
        return self.x_skew, self.y_skew

    @property
    def shift(self) -> Tuple[int, int]:
        return self.x_shift, self.y_shift

    @shift.setter
    def shift(self, shift: Tuple[int, int]):
        self.x_shift, self.y_shift = shift

    def cell_to_pixel(self, x: int, y: int) -> Tuple[int, int]:
        """Convert cell coordinates to pixel coordinates, accounting for cell size and shifts."""
        ox, oy = self.origin
        return ox + x * self.x_size + y * self.x_shift, oy + y * self.y_size + x * self.y_shift

    def pixel_size(self) -> Tuple[int, int]:
        """Calculate the total size of the grid in pixels, accounting for cell size, shifts, and skewing."""
        width_px = self.width * self.x_size + self.x_shift * (self.height - 1)
        height_px = self.height * self.y_size + self.y_shift * (self.width - 1)

        # Account for skewing of the grid by calculating the additional width and height needed to accommodate the skewed tiles
        x_skew, y_skew = self.skew_angles
        width_px += math.ceil(math.tan(x_skew) * math.cos(x_skew) * height_px)
        height_px += math.ceil(math.tan(y_skew) * math.cos(y_skew) * width_px)
        return math.ceil(width_px * math.cos(y_skew)), math.ceil(height_px * math.cos(x_skew))

    def iter_cells(self) -> Iterator[Tuple[int, int]]:
        for y in range(self.height):
            for x in range(self.width):
                yield x, y
