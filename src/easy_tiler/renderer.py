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

    def __init__(
        self,
        grid: Grid,
        tile_getter: Callable[[int, int], TileBase],
        scale: float = 1.0,
        background_col: str | None = None,
    ):
        self.grid = grid
        self.tile_getter = tile_getter
        self.scale = scale
        self.background_color = background_col

    def _render_to_context(self, ctx: cairo.Context):
        """Render the grid to a Cairo context."""
        width = self.grid.x_size

        # Apply transform to context to render skewing of the grid
        x_skew, y_skew = self.grid.skew_angles
        mtrx = cairo.Matrix(1, math.tan(y_skew), math.tan(x_skew), 1, 0, 0)
        ctx.transform(mtrx)

        # scale x by cos(y_skew) and y by cos(x_skew) to preserve aspect ratio of tiles
        ctx.scale(self.scale * math.cos(y_skew), self.scale * math.cos(x_skew))

        for x, y in self.grid.iter_cells():
            tile = self.tile_getter(x, y)
            px, py = self.grid.cell_to_pixel(x, y)
            ctx.save()
            ctx.translate(px, py)
            # ensure each tile draws in a wh x wh square starting at 0,0
            tile.draw_tile(ctx, width)

            if self.grid.double:
                ctx.save()
                ctx.translate(px + self.grid.x_size / 2, py + self.grid.y_size / 2)
                # restore at the end brings it back to previous saved state
                tile.draw_tile(ctx, width)
                ctx.save()
                ctx.restore()

    def _prepare_surface(self, ctx: cairo.Context):
        """Fill background if background_color is set."""
        if self.background_color is not None:
            ctx.set_source_rgba(*color(self.background_color))
            ctx.paint()

    def _set_context(self, ctx: cairo.Context):
        ctx.set_line_cap(cairo.LINE_CAP_BUTT)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_antialias(cairo.ANTIALIAS_BEST)
        ctx.set_line_width(min(0.8, self.grid.x_size * 0.01))

    def render_png(self, path: str):
        w_px, h_px = self.grid.pixel_size()
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w_px, h_px)
        ctx = cairo.Context(surface)
        self._prepare_surface(ctx)
        self._set_context(ctx)
        self._render_to_context(ctx)
        surface.write_to_png(path)

    def render_svg(self, path: str):
        w_px, h_px = self.grid.pixel_size()
        surface = cairo.SVGSurface(path, w_px, h_px)
        ctx = cairo.Context(surface)
        self._prepare_surface(ctx)
        self._set_context(ctx)
        self._render_to_context(ctx)
        ctx.show_page()
