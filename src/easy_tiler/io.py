"""IO helpers for saving surfaces and convenience exporters."""

from collections.abc import Callable

from easy_tiler.grid import Grid
from easy_tiler.renderer import Renderer
from easy_tiler.tiles import TileBase


def save_png(path: str, grid: Grid, tile_getter: Callable[[int, int], TileBase], **kwargs):
    r = Renderer(**kwargs)
    r.render_png(path, grid, tile_getter)


def save_svg(path: str, grid: Grid, tile_getter: Callable[[int, int], TileBase], **kwargs):
    r = Renderer(**kwargs)
    r.render_svg(path, grid, tile_getter)
