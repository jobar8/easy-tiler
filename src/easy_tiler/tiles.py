"""Tile classes for easy_tiler.

Defines a TileBase abstract class and a simple RegularPolygonTile
concrete implementation for testing and examples.
"""
import abc
import math
from dataclasses import dataclass

import cairo

from .helpers import color


@dataclass
class TileConfig:
    width: int
    bg_color: tuple | None = None
    fg_color: tuple | None = None


class TileBase(abc.ABC):
    """Base tile class.

    Subclasses should implement `draw(self, ctx, g)` which performs drawing
    on the provided cairo `Context` using the small graphics state `g`.
    """

    rotations = 4
    flip = False

    def __init__(self, rot: float | int = 0, flipped: bool = False):
        self.rot = rot % self.rotations
        self.flipped = bool(flipped)

    def init_tile(self, ctx: cairo.Context, g: TileConfig):
        # default does nothing; subclasses may populate g or precompute paths
        return

    @abc.abstractmethod
    def draw(self, ctx: cairo.Context, g: TileConfig):
        raise NotImplementedError()

    def draw_tile(self, ctx: cairo.Context, wh: int, bg_color=None, fg_color=None):
        g = TileConfig(wh, bg_color, fg_color)
        self.init_tile(ctx, g)
        self.draw(ctx, g)


class RegularPolygonTile(TileBase):
    """Draw a regular polygon centered in the tile.

    Parameters
    - sides: number of sides (3 = triangle, 4 = square, ...)
    - inset: fraction of half-width to use as radius (0..1)
    - fill_fg: whether to fill polygon with foreground colour
    """

    def __init__(self, sides: float | int = 4, inset: float = 0.85, rot: float | int = 0, flipped: bool = False):
        super().__init__(rot=rot, flipped=flipped)
        self.sides = max(3, int(sides))
        self.inset = float(inset)

    def draw(self, ctx: cairo.Context, g: TileConfig):
        wh = g.width
        bg = g.bg_color if g.bg_color is not None else color(1)
        fg = g.fg_color if g.fg_color is not None else color(0)

        # draw background
        ctx.save()
        ctx.set_source_rgba(*bg)
        ctx.rectangle(0, 0, wh, wh)
        # ctx.fill()
        ctx.fill_preserve()
        ctx.set_source_rgba(*fg)
        ctx.stroke()

        # polygon geometry
        cx = cy = wh / 2.0
        r = (wh / 2.0) * self.inset
        # rotation in radians: treat rot as quarter-turns for compatibility
        angle_offset = (self.rot * (math.pi / 2.0))
        pts = []
        for i in range(self.sides):
            theta = (2.0 * math.pi * i / self.sides) + angle_offset# - math.pi / 2.0
            # print(f"theta for side {i}: {theta:.2f} radians")
            x = cx + r * math.cos(theta)
            y = cy + r * math.sin(theta)
            pts.append((x, y))

        # draw polygon filled with fg
        ctx.set_source_rgba(*fg)
        x0, y0 = pts[0]
        ctx.move_to(x0, y0)
        for x, y in pts[1:]:
            ctx.line_to(x, y)
        ctx.close_path()
        ctx.fill_preserve()
        ctx.set_line_width(max(1.0, wh * 0.01))
        # stroke with slightly darker foreground
        ctx.set_source_rgba(max(0.0, fg[0] - 0.2), max(0.0, fg[1] - 0.2), max(0.0, fg[2] - 0.2), fg[3])
        ctx.stroke()
        ctx.restore()
