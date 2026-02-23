"""IO helpers for saving surfaces and convenience exporters."""

from __future__ import annotations

import cairo
from .grid import Grid
from .renderer import Renderer
from .tiles import TileBase
from typing import Callable


def save_png(path: str, grid: Grid, tile_getter: Callable[[int, int], TileBase], scale: float = 1.0):
    r = Renderer(scale=scale)
    r.render_png(path, grid, tile_getter)


def save_svg(path: str, grid: Grid, tile_getter: Callable[[int, int], TileBase], scale: float = 1.0):
    r = Renderer(scale=scale)
    r.render_svg(path, grid, tile_getter)
