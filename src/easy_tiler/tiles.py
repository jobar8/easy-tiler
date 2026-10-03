"""Tile classes for easy_tiler.

Defines a TileBase abstract class and other simple tile implementations.
"""

import abc
import math
import random
from dataclasses import dataclass, field

import cairo

from easy_tiler.colors import ColorConfig, CustomPalette

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
    """Geometry-focused configuration for a tile."""

    width: int = 0
    rotations: int = 4
    rot_angle: float = PI2
    rot: float = 0
    flipped: bool = False
    outline: bool = False
    radius: float = 1.0
    sides: int = 4
    inset: float = 0.85
    side_length: float = 1.0
    arrow_width: float = 0.333
    seed: float | str | bytes | bytearray | None = None

    _rng: random.Random = field(init=False)

    def __post_init__(self) -> None:
        self.rot = self.rot % self.rotations
        self.flipped = bool(self.flipped)
        self.outline = bool(self.outline)
        self._rng = random.Random(self.seed)

    @classmethod
    def get_palette(cls, palette: str, num_colors: int | None = None) -> list:
        return CustomPalette(palette, num_colors).colors


class TileBase(abc.ABC):
    """Base tile class.

    Subclasses should implement `draw(self, ctx, g)` which performs drawing
    on the provided cairo `Context` using the small graphics config `g`.
    """

    def __init__(
        self,
        *,
        config: TileConfig | None = None,
        color_config: ColorConfig | None = None,
        random_seed: float | str | bytes | bytearray | None = None,
    ):
        self.config = config or TileConfig(seed=random_seed)
        self.color_config = color_config or ColorConfig(seed=random_seed)

    def init_tile(self, ctx: cairo.Context):
        wh = self.config.width
        wh2 = wh / 2.0

        # draw background
        bg_col = self.color_config.get_bg_color()
        if bg_col != (0, 0, 0, 0):
            ctx.set_source_rgba(*bg_col)
            ctx.rectangle(0, 0, wh, wh)

        # Draw outline of tile
        if self.config.outline:
            ctx.fill_preserve()
            ctx.set_source_rgba(*self.color_config.outline_color)  # type: ignore
            ctx.set_line_width(max(1.0, wh * 0.01))
            ctx.stroke()
        else:
            ctx.fill()

        # Apply rotation and flip transformations to the context before drawing the tile.
        ctx.translate(wh2, wh2)
        ctx.rotate(self.config.rot_angle * self.config.rot)
        ctx.translate(-wh2, -wh2)

        if self.config.flipped:
            ctx.translate(wh, 0)
            ctx.scale(-1, 1)

    @abc.abstractmethod
    def draw(self, ctx: cairo.Context, g: TileConfig):
        raise NotImplementedError()

    def draw_tile(self, ctx: cairo.Context) -> None:
        self.init_tile(ctx)
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
        fg = self.color_config.get_fg_color(0)

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
        fg = self.color_config.get_fg_color(0)

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
        fg = self.color_config.get_fg_color(0)

        # draw bottom-left corner
        ctx.set_source_rgba(*fg)
        ctx.move_to(0, 0)
        ctx.line_to(wh, wh)
        ctx.line_to(0, wh)
        ctx.line_to(0, 0)
        ctx.fill()
        ctx.restore()


class ArrowTile(TileBase):
    """Draw a Truchet tile with one more triangle."""

    def __init__(self, width: float = 0.333, **kwargs):
        super().__init__(**kwargs)
        if not (0.0 < width < 1.0):
            raise ValueError('ArrowTile width must be between 0 and 1.')
        self.width = width

    def draw(self, ctx: cairo.Context, g: TileConfig):
        wh = g.width
        fg = self.color_config.get_fg_color(0)

        # position of the bottom of the branch
        wa = (1 - self.width) / 2.0

        # draw bottom-left corner
        ctx.set_source_rgba(*fg)
        ctx.move_to(0, 0)
        ctx.line_to(wh * wa, wh * wa)
        ctx.line_to(wh, 0)
        ctx.line_to(wh * (1 - wa), wh * (1 - wa))
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
        self.config.rot = (self.config.rot - 1) % self.config.rotations

    def draw(self, ctx: cairo.Context, g: TileConfig):
        wh = g.width
        self.radius = self.radius * wh
        fg = self.color_config.get_fg_color(0)

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


class CircleTile(TileBase):
    """Draw a circle tile that can be used in Cairo tiling."""

    def __init__(self, radius: float = 0.25, **kwargs):
        super().__init__(**kwargs)
        self.radius = radius
        self.config.rot = (self.config.rot - 1) % self.config.rotations

    def draw(self, ctx: cairo.Context, g: TileConfig):
        radius = g._rng.uniform(0.5, 1.0) * g.width * self.radius
        fg = self.color_config.get_fg_color(0)

        ctx.set_source_rgba(*fg)
        ctx.move_to(g.width / 4, g.width / 4)
        ctx.arc(g.width / 4, g.width / 4, radius, 0, 2 * PI)
        ctx.fill()
        ctx.restore()


class SmithTile(TileBase):
    def __init__(self, radius: float = 0.5, **kwargs):
        super().__init__(**kwargs)
        self.radius = radius

    def draw(self, ctx: cairo.Context, g: TileConfig):
        radius = self.radius * g.width
        fg = self.color_config.get_fg_color(0)

        ctx.set_source_rgba(*fg)
        ctx.arc(0, g.width, radius, -PI2, 0)
        ctx.line_to(0, g.width)
        ctx.close_path()
        ctx.fill()

        ctx.arc(g.width, 0, radius, PI2, PI)
        ctx.line_to(g.width, 0)
        ctx.close_path()
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
        self.config.rot = (self.config.rot - 1) % self.config.rotations

    def draw(self, ctx: cairo.Context, g: TileConfig):
        side_length = g.width * self.side_length
        fg = self.color_config.get_fg_color(0)

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

        # draw outline of the pentagon
        ctx.set_source_rgba(*self.color_config._palette.get(self.color_config.outline_color))
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
        ctx.close_path()
        # restore to initial orientation
        ctx.rotate(2 * PI3)
        ctx.fill_preserve()

        # stroke with slightly darker foreground
        # ctx.set_line_width(max(1.0, wh * 0.01))
        # ctx.set_source_rgba(
        #     max(0.0, fg[0] - 0.2), max(0.0, fg[1] - 0.2), max(0.0, fg[2] - 0.2), fg[3]
        # )
        ctx.set_source_rgba(0, 0, 0, 1)

        ctx.stroke()
        ctx.move_to(0, 0)

    def draw(self, ctx: cairo.Context, g: TileConfig):
        wh = g.width
        side_length = wh / (4 * math.cos(PI6))
        polygon_width = wh / 2

        # 1st polygon (top)
        ctx.move_to(0, 0)
        self.draw_pentagon(ctx, side_length, self.color_config.get_fg_color(0))

        # 2nd polygon (bottom)
        ctx.rel_move_to(polygon_width, polygon_width)
        ctx.rotate(PI)
        self.draw_pentagon(ctx, side_length, self.color_config.get_fg_color(1))

        # 3rd polygon (right)
        ctx.rel_move_to(-polygon_width, -polygon_width)
        ctx.rotate(PI2)
        self.draw_pentagon(ctx, side_length, self.color_config.get_fg_color(2))

        # 4th polygon (left)
        ctx.rotate(PI)
        self.draw_pentagon(ctx, side_length, self.color_config.get_fg_color(3))

        ctx.stroke()
        ctx.restore()
