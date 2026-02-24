"""Grid utilities for easy_tiler."""

from dataclasses import dataclass
from typing import Iterator, Tuple


@dataclass
class Grid:
    width: int
    height: int
    x_size: int = 64
    y_size: int = 64
    origin: Tuple[int, int] = (0, 0)
    x_shift: int = 0
    y_shift: int = 0
    x_skew: float = 0
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
        ox, oy = self.origin
        return ox + x * self.x_size + y * self.x_shift, oy + y * self.y_size + x * self.y_shift

    def pixel_size(self) -> Tuple[int, int]:
        return self.width * self.x_size, self.height * self.y_size

    def iter_cells(self) -> Iterator[Tuple[int, int]]:
        for y in range(self.height):
            for x in range(self.width):
                yield x, y
