"""Tile classes for easy_tiler.

Defines a TileBase abstract class and other simple tile implementations.
"""

import abc
import math
from dataclasses import dataclass

import cairo

from .helpers import color


# precompute some constants for efficiency and readability
PI = math.pi
PI2 = math.pi / 2


@dataclass
class TileConfig:
    width: int
    bg_color: tuple | None = None
    fg_color: tuple | None = None

    def __post_init__(self) -> None:
        if self.bg_color is not None and len(self.bg_color) != 4:
            raise ValueError('bg_color must be a tuple of 4 floats (r, g, b, a)')
        if self.fg_color is not None and len(self.fg_color) != 4:
            raise ValueError('fg_color must be a tuple of 4 floats (r, g, b, a)')
        if self.bg_color is None and self.fg_color is None:
            # default to white bg and black fg
            self.bg_color = color(1)
            self.fg_color = color(0)


class TileBase(abc.ABC):
    """Base tile class.

    Subclasses should implement `draw(self, ctx, g)` which performs drawing
    on the provided cairo `Context` using the small graphics config `g`.
    """

    rotations = 4
    flip = False

    def __init__(self, rot: float | int = 0, flipped: bool = False, outline: bool = True):
        self.rot = rot % self.rotations
        self.flipped = bool(flipped)
        self.outline = bool(outline)

    def init_tile(self, ctx: cairo.Context, g: TileConfig):
        wh = g.width
        wh2 = wh / 2.0
        bg_color = g.bg_color if g.bg_color is not None else color(1)
        fg_color = g.fg_color if g.fg_color is not None else color(0)

        # draw background
        ctx.save()
        ctx.set_source_rgba(*bg_color)
        ctx.rectangle(0, 0, wh, wh)

        # Draw outline of tile
        if self.outline:
            ctx.fill_preserve()
            ctx.set_source_rgba(*fg_color)
            ctx.set_line_width(max(1.0, wh * 0.01))
            ctx.stroke()
        else:
            ctx.fill()

        # Apply rotation and flip transformations to the context before drawing the tile.
        ctx.translate(wh2, wh2)
        ctx.rotate(PI2 * self.rot)
        ctx.translate(-wh2, -wh2)

        if self.flipped:
            ctx.translate(wh, 0)
            ctx.scale(-1, 1)

    @abc.abstractmethod
    def draw(self, ctx: cairo.Context, g: TileConfig):
        raise NotImplementedError()

    def draw_tile(self, ctx: cairo.Context, wh: int, bg_color=None, fg_color=None) -> None:
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

    def __init__(self, sides: float | int = 4, inset: float = 0.85, **kwargs):
        super().__init__(**kwargs)
        self.sides = max(3, int(sides))
        self.inset = float(inset)

    def draw(self, ctx: cairo.Context, g: TileConfig):
        wh = g.width
        fg = g.fg_color if g.fg_color is not None else color(0)

        # polygon geometry
        cx = cy = wh / 2.0
        r = (wh / 2.0) * self.inset
        pts = []
        for i in range(self.sides):
            theta = 2.0 * PI * i / self.sides
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
        # stroke with slightly darker foreground
        ctx.fill_preserve()
        ctx.set_line_width(max(1.0, wh * 0.01))
        ctx.set_source_rgba(max(0.0, fg[0] - 0.2), max(0.0, fg[1] - 0.2), max(0.0, fg[2] - 0.2), fg[3])
        ctx.stroke()
        ctx.restore()


class PuckTile(TileBase):
    """Draw a simple tile that looks like a hockey puck: a filled circle with an outline."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def draw(self, ctx: cairo.Context, g: TileConfig):
        wh = g.width
        fg = g.fg_color if g.fg_color is not None else color(0)

        # draw quarter circles based on variant
        ctx.set_source_rgba(*fg)
        r = wh / 2.0
        # top-left and bottom-right corners
        ctx.arc(r, r, r, PI, 1.5 * PI)  # top-left
        ctx.arc(r, r, r, 0.0, 0.5 * PI)  # bottom-right
        ctx.fill()
        ctx.restore()


class TruchetTile(TileBase):
    """Draw a simple Truchet tile with one triangle in one corner."""

    def __init__(self, radius: float = 1.0, **kwargs):
        super().__init__(**kwargs)
        self.radius = radius

    def draw(self, ctx: cairo.Context, g: TileConfig):
        wh = g.width
        self.radius = self.radius * wh
        # bg = g.bg_color if g.bg_color is not None else color(1)
        fg = g.fg_color if g.fg_color is not None else color(0)

        # draw corner and round side
        ctx.set_source_rgba(*fg)
        a = (-wh + math.sqrt(2 * self.radius * self.radius - wh * wh)) / 2
        xc = yc = -a
        angle1 = math.acos((wh + a) / self.radius)
        angle2 = 0.5 * PI - angle1

        ctx.arc(xc, yc, self.radius, angle1, angle2)  # top-left
        ctx.line_to(0, 0)
        ctx.line_to(wh, 0)
        ctx.fill()
        ctx.restore()
