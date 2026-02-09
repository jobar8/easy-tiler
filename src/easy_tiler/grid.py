"""Grid utilities for easy_tiler."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Tuple


@dataclass
class Grid:
    width: int
    height: int
    cell_size: int = 64
    origin: Tuple[int, int] = (0, 0)

    def cell_to_pixel(self, x: int, y: int) -> Tuple[int, int]:
        ox, oy = self.origin
        return ox + x * self.cell_size, oy + y * self.cell_size

    def pixel_size(self) -> Tuple[int, int]:
        return self.width * self.cell_size, self.height * self.cell_size

    def iter_cells(self) -> Iterator[Tuple[int, int]]:
        for y in range(self.height):
            for x in range(self.width):
                yield x, y
