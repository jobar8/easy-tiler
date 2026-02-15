"""Renderer for composing tiles onto cairo surfaces."""

from __future__ import annotations

import cairo
from typing import Callable

from .grid import Grid
from .tiles import TileBase


class Renderer:
    """Render a Grid using a tile provider function.

    The `tile_getter` is a callable tile_getter(x, y) -> TileBase
    """

    def __init__(self, scale: int = 1):
        self.scale = int(scale)

    def _render_to_context(self, ctx: cairo.Context, grid: Grid, tile_getter: Callable[[int, int], TileBase]):
        width = grid.cell_size
        for x, y in grid.iter_cells():
            tile = tile_getter(x, y)
            px, py = grid.cell_to_pixel(x, y)
            ctx.save()
            ctx.translate(px, py)
            # ensure each tile draws in a wh x wh square starting at 0,0
            tile.draw_tile(ctx, width)
            ctx.restore()

    def render_png(self, path: str, grid: Grid, tile_getter: Callable[[int, int], TileBase]):
        w_px, h_px = grid.pixel_size()
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w_px, h_px)
        ctx = cairo.Context(surface)
        self._render_to_context(ctx, grid, tile_getter)
        surface.write_to_png(path)

    def render_svg(self, path: str, grid: Grid, tile_getter: Callable[[int, int], TileBase]):
        w_px, h_px = grid.pixel_size()
        surface = cairo.SVGSurface(path, w_px, h_px)
        ctx = cairo.Context(surface)
        self._render_to_context(ctx, grid, tile_getter)
        ctx.show_page()
