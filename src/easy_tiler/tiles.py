"""Tile classes for easy_tiler.

Defines a TileBase abstract class and other simple tile implementations.
"""

import abc
import math
import random
from dataclasses import dataclass, field

import cairo
import colorcet as cc

from easy_tiler.helpers import color

# precompute some constants for efficiency and readability
PI = math.pi
PI2 = math.pi / 2
PI3 = math.pi / 3
PI6 = math.pi / 6


def debug_print_ctx(ctx: cairo.Context) -> None:
    """Print the current point and matrix of the Cairo context for debugging."""
    x, y = ctx.get_current_point()
    mtrx = ctx.get_matrix()
    print(
        f'x={x:.2f} y={y:.2f} xx={mtrx.xx:.2f} xy={mtrx.xy:.2f} yx={mtrx.yx:.2f}',
        f'yy={mtrx.yy:.2f} x0={mtrx.x0:.2f} y0={mtrx.y0:.2f}',
    )


@dataclass
class TileConfig:
    """Configuration for a tile."""

    width: int = 0
    bg_color: str | tuple | None = None
    fg_color: str | tuple | list | None = None
    outline_color: str | tuple | None = None
    palette: str | None = None
    num_colors: int | None = None

    _colors: list | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        self.outline_color = color(self.outline_color)

        if self.palette is not None:
            self._colors = self.get_palette(self.palette, self.num_colors)

    @classmethod
    def get_palette(cls, palette: str, num_colors: int | None = None) -> list:
        colors = cc.palette[palette]
        if num_colors is not None:
            return colors[:num_colors]
        return colors

    def _resolve_color(self, val, index: int = 0) -> tuple:
        """Resolve a color value to a tuple."""
        if val is None:
            return (0, 0, 0, 0)

        if isinstance(val, list):
            val = val[index % len(val)]

        if val == 'random':
            if self._colors:
                return color(random.choice(self._colors))
            return (random.random(), random.random(), random.random(), 1.0)

        return color(val)

    def get_fg_color(self, index: int = 0) -> tuple:
        """Get the foreground color."""
        return self._resolve_color(self.fg_color, index)

    def get_bg_color(self) -> tuple:
        """Get the background color."""
        return self._resolve_color(self.bg_color)


class TileBase(abc.ABC):
    """Base tile class.

    Subclasses should implement `draw(self, ctx, g)` which performs drawing
    on the provided cairo `Context` using the small graphics config `g`.
    """

    rotations = 4
    flip = False

    def __init__(
        self,
        rot: float = 0,
        flipped: bool = False,
        outline: bool = True,
        config: TileConfig | None = None,
    ):
        self.rot = rot % self.rotations
        self.flipped = bool(flipped)
        self.outline = bool(outline)
        self.config = config or TileConfig()

    def init_tile(self, ctx: cairo.Context, g: TileConfig):
        wh = g.width
        wh2 = wh / 2.0

        # draw background
        bg_col = g.get_bg_color()
        if bg_col != (0, 0, 0, 0):
            ctx.set_source_rgba(*bg_col)
            ctx.rectangle(0, 0, wh, wh)

        # Draw outline of tile
        if self.outline:
            ctx.fill_preserve()
            ctx.set_source_rgba(*g.outline_color)
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

    def draw_tile(self, ctx: cairo.Context, wh: int) -> None:
        self.config.width = wh
        self.init_tile(ctx, self.config)
        self.draw(ctx, self.config)


class RegularPolygonTile(TileBase):
    """Draw a regular polygon centered in the tile.

    Parameters
    - sides: number of sides (3 = triangle, 4 = square, ...)
    - inset: fraction of half-width to use as radius (0..1)
    """

    def __init__(self, sides: float = 4, inset: float = 0.85, **kwargs):
        super().__init__(**kwargs)
        self.sides = max(3, int(sides))
        self.inset = float(inset)

    def draw(self, ctx: cairo.Context, g: TileConfig):
        wh = g.width
        fg = g.get_fg_color(0)

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
        ctx.set_source_rgba(
            max(0.0, fg[0] - 0.2), max(0.0, fg[1] - 0.2), max(0.0, fg[2] - 0.2), fg[3]
        )
        ctx.stroke()
        ctx.restore()


class PuckTile(TileBase):
    """Draw a simple tile that looks like a hockey puck: a filled circle with an outline."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def draw(self, ctx: cairo.Context, g: TileConfig):
        wh = g.width
        fg = g.get_fg_color(0)

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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def draw(self, ctx: cairo.Context, g: TileConfig):
        wh = g.width
        fg = g.get_fg_color(0)

        # draw bottom-left corner
        ctx.set_source_rgba(*fg)
        ctx.move_to(0, 0)
        ctx.line_to(wh, wh)
        ctx.line_to(0, wh)
        ctx.line_to(0, 0)
        ctx.fill()
        ctx.restore()


class RileyTile(TileBase):
    """Draw a Riley tile with one corner and one round side."""

    def __init__(self, radius: float = 1.0, **kwargs):
        super().__init__(**kwargs)
        self.radius = radius
        self.rot = self.rot - 1  # Rotate by -pi/2 to match the orientation of Truchet tiles

    def draw(self, ctx: cairo.Context, g: TileConfig):
        wh = g.width
        self.radius = self.radius * wh
        fg = g.get_fg_color(0)

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


class PentagonTile(TileBase):
    """Draw a pentagon tile that can be used in Cairo tiling."""

    def __init__(self, side_length: float | None = None, **kwargs):
        super().__init__(**kwargs)
        if side_length is None:
            self.side_length = 1.0 / (4 * math.cos(PI6))
        else:
            self.side_length = side_length
        self.rot = self.rot - 1  # Rotate by -pi/2 to match the orientation of Truchet tiles

    def draw(self, ctx: cairo.Context, g: TileConfig):
        side_length = g.width * self.side_length
        fg = g.get_fg_color(0)

        ctx.set_source_rgba(*fg)
        ctx.move_to(0, 0)
        ctx.rotate(-PI6)
        ctx.rel_line_to(side_length, 0)
        ctx.rotate(PI3)
        ctx.rel_line_to(side_length, 0)
        ctx.rotate(PI2)
        ctx.rel_line_to(side_length, 0)
        ctx.rotate(PI3)
        # bottom is shorter
        ctx.rel_line_to((math.sqrt(3) - 1) * side_length, 0)
        ctx.rotate(PI3)
        ctx.rel_line_to(side_length, 0)
        ctx.rotate(2 * PI3)
        ctx.fill_preserve()
        # ctx.fill()
        # ctx.restore()

        # draw outline of the pentagon
        # ctx.set_line_width(max(1.0, wh * 0.01))
        ctx.set_source_rgba(
            max(0.0, fg[0] - 0.2), max(0.0, fg[1] - 0.2), max(0.0, fg[2] - 0.2), fg[3]
        )
        ctx.set_source_rgba(*color(g.outline_color))
        ctx.stroke()
        ctx.restore()


class CairoTile(TileBase):
    """Draw a Cairo tile."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def draw_pentagon(ctx, side_length, fg):
        ctx.set_source_rgba(*fg)
        ctx.rotate(-PI6)
        ctx.rel_line_to(side_length, 0)
        ctx.rotate(PI3)
        ctx.rel_line_to(side_length, 0)
        ctx.rotate(PI2)
        ctx.rel_line_to(side_length, 0)
        ctx.rotate(PI3)
        # bottom is shorter
        ctx.rel_line_to((math.sqrt(3) - 1) * side_length, 0)
        ctx.rotate(PI3)
        ctx.rel_line_to(side_length, 0)
        ctx.rotate(2 * PI3)
        ctx.fill()

        # stroke with slightly darker foreground
        # ctx.set_line_width(max(1.0, wh * 0.01))
        # ctx.set_source_rgba(
        #     max(0.0, fg[0] - 0.2), max(0.0, fg[1] - 0.2), max(0.0, fg[2] - 0.2), fg[3]
        # )
        # ctx.set_source_rgba(0, 0, 0, 1)

        # ctx.stroke_preserve()
        # ctx.stroke()
        ctx.move_to(0, 0)


    def draw(self, ctx: cairo.Context, g: TileConfig):
        wh = g.width
        side_length = wh / (4 * math.cos(PI6))
        polygon_width = 2 * side_length * math.cos(PI6)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_width(1)

        # 1st polygon (top)
        ctx.move_to(0, 0)
        self.draw_pentagon(ctx, side_length, g.get_fg_color(0))

        # 2nd polygon (bottom)
        ctx.rel_move_to(polygon_width, polygon_width)
        ctx.rotate(PI)
        self.draw_pentagon(ctx, side_length, g.get_fg_color(1))

        # # 3rd polygon (right)
        ctx.rotate(PI2)
        self.draw_pentagon(ctx, side_length, g.get_fg_color(2))

        # # 4th polygon (left)
        ctx.rel_move_to(polygon_width, -polygon_width)
        ctx.rotate(PI)
        self.draw_pentagon(ctx, side_length, g.get_fg_color(3))

        ctx.set_source_rgb(0.3, 0.2, 0.5)  # Solid color
        ctx.stroke()
        ctx.restore()
