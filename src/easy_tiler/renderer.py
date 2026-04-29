"""Renderer for composing tiles onto cairo surfaces."""

import math
from collections.abc import Callable

import cairo

from easy_tiler.grid import Grid
from easy_tiler.helpers import color
from easy_tiler.tiles import TileBase


class Renderer:
    """Render a Grid using a tile provider function.

    The `tile_getter` is a callable tile_getter(x, y) -> TileBase
    """

    def __init__(self, scale: float = 1.0, background_col: str | None = None):
        self.scale = scale
        self.background_col = background_col

    def _render_to_context(
        self, ctx: cairo.Context, grid: Grid, tile_getter: Callable[[int, int], TileBase]
    ):
        width = grid.x_size

        # Appply transform to context to render skewing of the grid
        x_skew, y_skew = grid.skew_angles
        mtrx = cairo.Matrix(1, math.tan(y_skew), math.tan(x_skew), 1, 0, 0)
        ctx.transform(mtrx)

        # scale x by cos(y_skew) and y by cos(x_skew) to preserve aspect ratio of tiles
        ctx.scale(self.scale * math.cos(y_skew), self.scale * math.cos(x_skew))

        for x, y in grid.iter_cells():
            tile = tile_getter(x, y)
            px, py = grid.cell_to_pixel(x, y)
            ctx.save()
            ctx.translate(px, py)
            # ensure each tile draws in a wh x wh square starting at 0,0
            tile.draw_tile(ctx, width)

            if grid.double:
                ctx.save()
                ctx.translate(px + grid.x_size / 2, py + grid.y_size / 2)
                tile.draw_tile(
                    ctx, width
                )  # restore at the end brings it back to previous saved state

    def _prepare_surface(self, ctx: cairo.Context):
        """Fill background if background_col is set."""
        if self.background_col is not None:
            ctx.set_source_rgba(*color(self.background_col))
            print(*self.background_col)
            ctx.paint()

    def render_png(self, path: str, grid: Grid, tile_getter: Callable[[int, int], TileBase]):
        w_px, h_px = grid.pixel_size()
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w_px, h_px)
        ctx = cairo.Context(surface)
        self._prepare_surface(ctx)
        self._render_to_context(ctx, grid, tile_getter)
        surface.write_to_png(path)

    def render_svg(self, path: str, grid: Grid, tile_getter: Callable[[int, int], TileBase]):
        w_px, h_px = grid.pixel_size()
        surface = cairo.SVGSurface(path, w_px, h_px)
        ctx = cairo.Context(surface)
        self._prepare_surface(ctx)
        self._render_to_context(ctx, grid, tile_getter)
        ctx.show_page()
