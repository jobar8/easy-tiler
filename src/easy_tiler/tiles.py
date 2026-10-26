"""Tile classes for easy_tiler.

Defines a TileBase abstract class and other simple tile implementations.
"""

import abc
import math
import random
from dataclasses import dataclass, field, replace
from typing import Any, ClassVar

import cairo

from easy_tiler.colors import ColorConfig

# precompute some constants for efficiency and readability
PI = math.pi
PI2 = math.pi / 2
PI3 = math.pi / 3
PI6 = math.pi / 6


def debug_print_ctx(ctx: cairo.Context) -> None:
    """Print the current point and matrix of the Cairo context for debugging."""
    x, y = ctx.get_current_point()
    mtrx: cairo.Matrix = ctx.get_matrix()
    print(
        f'x={x:.2f} y={y:.2f} xx={mtrx.xx:.2f} xy={mtrx.xy:.2f} yx={mtrx.yx:.2f}',
        f'yy={mtrx.yy:.2f} x0={mtrx.x0:.2f} y0={mtrx.y0:.2f}',
    )


@dataclass
class TileConfig:
    """The single configuration object used by every tile type.

    All tile parameters live here: the rotation/flip/grid-line settings and the
    shape specific values (``sides``, ``inset``, ``radius``, ``side_length``
    and ``arrow_width``).

    The shape specific values default to ``None``, meaning *not set*. When a
    tile is created it fills in the values it needs from its own ``defaults``
    mapping, so a single config can describe any tile without carrying
    meaningless values around.
    """

    # rendering
    tile_width: int = 0  # Width of the tile in pixels, set by the renderer
    # rotation and orientation
    max_rotations: int = 4
    rotation_angle: float = PI2
    rotation_index: float = 0
    flipped: bool = False
    gridlines: bool = False
    # shape specific parameters, None means "use the tile class default"
    sides: int | None = None
    inset: float | None = None
    radius: float | None = None
    side_length: float | None = None
    arrow_width: float | None = None
    seed: float | str | bytes | bytearray | None = None

    _rng: random.Random = field(init=False)

    def __post_init__(self) -> None:
        self.rotation_index = self.rotation_index % self.max_rotations
        self.flipped = bool(self.flipped)
        self.gridlines = bool(self.gridlines)
        self._rng = random.Random(self.seed)


class TileBase(abc.ABC):
    """Base tile class.

    Subclasses should implement `draw(self, ctx, g)` which performs drawing
    on the provided cairo `Context` using the small graphics config `g`.

    Subclasses may declare:

    - ``defaults``: mapping of config field name to default value, used for
      every parameter the caller did not set explicitly.
    - ``rotation_offset``: shift applied to the rotation index, for tiles that
      are drawn in a rotated frame.
    """

    defaults: ClassVar[dict[str, Any]] = {}
    rotation_offset: ClassVar[int] = 0

    def __init__(
        self,
        *,
        config: TileConfig | None = None,
        color_config: ColorConfig | None = None,
        random_seed: float | str | bytes | bytearray | None = None,
        **overrides: Any,
    ) -> None:
        base = config if config is not None else TileConfig(seed=random_seed)
        # Work on a copy so a config can be shared safely between tiles and a
        # tile never mutates a config owned by the caller.
        self.config = replace(base)
        self.color_config = color_config or ColorConfig(seed=random_seed)

        # Explicit keyword arguments always win over the config.
        for name, value in overrides.items():
            setattr(self.config, name, value)

        # Fill in anything still unset from the tile class defaults.
        for name, value in self.defaults.items():
            if getattr(self.config, name, None) is None:
                setattr(self.config, name, value)

        if self.rotation_offset:
            self.config.rotation_index = (
                self.config.rotation_index + self.rotation_offset
            ) % self.config.max_rotations

    def _value(self, g: TileConfig, name: str) -> Any:
        """Return the effective value of a config parameter."""
        value = getattr(g, name, None)
        return self.defaults.get(name) if value is None else value

    def _stroke_shape(self, ctx: cairo.Context, wh: int) -> None:
        """Stroke the current path with the configured stroke color if enabled."""
        ctx.set_line_width(max(1.0, wh * 0.01))
        ctx.set_source_rgba(*self.color_config.stroke_color)
        ctx.stroke()

    def init_tile(self, ctx: cairo.Context) -> None:
        wh: int = self.config.tile_width
        wh2: float = wh / 2.0

        # draw background
        bg_col = self.color_config.get_secondary_color()
        if bg_col != (0, 0, 0, 0):
            ctx.set_source_rgba(*bg_col)
            ctx.rectangle(0, 0, wh, wh)

        # Draw tile gridlines
        if self.config.gridlines:
            ctx.fill_preserve()
            ctx.set_source_rgba(*self.color_config.gridlines_color)  # type: ignore
            ctx.set_line_width(max(1.0, wh * 0.01))
            ctx.stroke()
        else:
            ctx.fill()

        # Apply rotation and flip transformations to the context before drawing the tile.
        ctx.translate(wh2, wh2)
        ctx.rotate(self.config.rotation_angle * self.config.rotation_index)
        ctx.translate(-wh2, -wh2)

        if self.config.flipped:
            ctx.translate(wh, 0)
            ctx.scale(-1, 1)

    @abc.abstractmethod
    def draw(self, ctx: cairo.Context, g: TileConfig, index: int = 0) -> None:
        raise NotImplementedError()

    def draw_tile(self, ctx: cairo.Context) -> None:
        self.init_tile(ctx)
        self.draw(ctx, self.config)
        # Fill the polygon and stroke the outline if stroke is enabled.
        if self.color_config.stroke:
            ctx.fill_preserve()
            self._stroke_shape(ctx, self.config.tile_width)
        else:
            ctx.fill()
        ctx.restore()


class RegularPolygonTile(TileBase):
    """Draw a regular polygon centered in the tile.

    Parameters
    - sides: number of sides (3 = triangle, 4 = square, ...)
    - inset: fraction of half-width to use as radius (0..1)
    """

    defaults: ClassVar[dict[str, Any]] = {'sides': 4, 'inset': 0.85}

    def draw(self, ctx: cairo.Context, g: TileConfig, index: int = 0) -> None:
        wh = g.tile_width
        sides = max(3, int(self._value(g, 'sides')))
        inset = float(self._value(g, 'inset'))
        primary_color = self.color_config.get_primary_color(index)

        # polygon geometry
        cx = cy = wh / 2.0
        r = (wh / 2.0) * inset
        pts = []
        for i in range(sides):
            theta = 2.0 * PI * i / sides
            x = cx + r * math.cos(theta)
            y = cy + r * math.sin(theta)
            pts.append((x, y))

        # draw polygon filled with primary_color
        ctx.set_source_rgba(*primary_color)
        x0, y0 = pts[0]
        ctx.move_to(x0, y0)
        for x, y in pts[1:]:
            ctx.line_to(x, y)
        ctx.close_path()


class PuckTile(TileBase):
    """Draw a simple tile that looks like a hockey puck: a filled circle with an outline."""

    def draw(self, ctx: cairo.Context, g: TileConfig, index: int = 0) -> None:
        wh = g.tile_width
        primary_color = self.color_config.get_primary_color(index)

        # draw quarter circles based on variant
        ctx.set_source_rgba(*primary_color)
        r = wh / 2.0
        # top-left and bottom-right corners
        ctx.arc(r, r, r, PI, 1.5 * PI)  # top-left
        ctx.arc(r, r, r, 0.0, 0.5 * PI)  # bottom-right


class TruchetTile(TileBase):
    """Draw a simple Truchet tile with one triangle in one corner."""

    def draw(self, ctx: cairo.Context, g: TileConfig, index: int = 0) -> None:
        wh = g.tile_width
        primary_color = self.color_config.get_primary_color(index)

        # draw bottom-left corner
        ctx.set_source_rgba(*primary_color)
        ctx.move_to(0, 0)
        ctx.line_to(wh, wh)
        ctx.line_to(0, wh)
        ctx.line_to(0, 0)


class ArrowTile(TileBase):
    """Draw a Truchet tile with one more triangle."""

    defaults: ClassVar[dict[str, Any]] = {'arrow_width': 0.333}

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if not (0.0 < float(self.config.arrow_width) < 1.0):  # type: ignore[operator]
            raise ValueError('ArrowTile arrow_width must be between 0 and 1.')

    def draw(self, ctx: cairo.Context, g: TileConfig, index: int = 0) -> None:
        wh = g.tile_width
        arrow_width = float(self._value(g, 'arrow_width'))
        primary_color = self.color_config.get_primary_color(index)

        # position of the bottom of the branch
        wa = (1 - arrow_width) / 2.0

        # draw bottom-left corner
        ctx.set_source_rgba(*primary_color)
        ctx.move_to(0, 0)
        ctx.line_to(wh * wa, wh * wa)
        ctx.line_to(wh, 0)
        ctx.line_to(wh * (1 - wa), wh * (1 - wa))
        ctx.line_to(wh, wh)
        ctx.line_to(0, wh)
        ctx.line_to(0, 0)


class RileyTile(TileBase):
    """Draw a Riley tile with one corner and one round side."""

    defaults: ClassVar[dict[str, Any]] = {'radius': 1.0}
    rotation_offset: ClassVar[int] = -1

    def draw(self, ctx: cairo.Context, g: TileConfig, index: int = 0) -> None:
        wh: int = g.tile_width
        radius = float(self._value(g, 'radius')) * wh
        primary_color = self.color_config.get_primary_color(index)

        # draw corner and round side
        ctx.set_source_rgba(*primary_color)
        a = (-wh + math.sqrt(2 * radius * radius - wh * wh)) / 2
        xc = yc = -a
        angle1 = math.acos((wh + a) / radius)
        angle2 = 0.5 * PI - angle1

        ctx.arc(xc, yc, radius, angle1, angle2)  # top-left
        ctx.line_to(0, 0)
        ctx.line_to(wh, 0)


class CircleTile(TileBase):
    """Draw a circle tile with a random radius."""

    defaults: ClassVar[dict[str, Any]] = {'radius': 0.25}
    rotation_offset: ClassVar[int] = -1

    def draw(self, ctx: cairo.Context, g: TileConfig, index: int = 0) -> None:
        radius = g._rng.uniform(0.5, 1.0) * g.tile_width * float(self._value(g, 'radius'))
        primary_color = self.color_config.get_primary_color(index)

        ctx.set_source_rgba(*primary_color)
        ctx.move_to(g.tile_width / 4, g.tile_width / 4)
        ctx.arc(g.tile_width / 4, g.tile_width / 4, radius, 0, 2 * PI)


class SmithTile(TileBase):
    """Draw a Smith tile with two quarter circles."""

    defaults: ClassVar[dict[str, Any]] = {'radius': 0.5}

    def draw(self, ctx: cairo.Context, g: TileConfig, index: int = 0) -> None:
        radius = float(self._value(g, 'radius')) * g.tile_width
        primary_color = self.color_config.get_primary_color(index)

        ctx.set_source_rgba(*primary_color)
        ctx.arc(0, g.tile_width, radius, -PI2, 0)
        ctx.line_to(0, g.tile_width)
        ctx.close_path()
        if self.color_config.stroke:
            ctx.fill_preserve()
            self._stroke_shape(ctx, g.tile_width)
        else:
            ctx.fill()

        ctx.new_path()
        ctx.set_source_rgba(*primary_color)
        ctx.arc(g.tile_width, 0, radius, PI2, PI)
        ctx.line_to(g.tile_width, 0)
        ctx.close_path()


class PentagonTile(TileBase):
    """Draw a pentagon tile that can be used in Cairo tiling."""

    defaults: ClassVar[dict[str, Any]] = {'side_length': 1.0 / (4 * math.cos(PI6))}
    rotation_offset: ClassVar[int] = -1

    def draw(self, ctx: cairo.Context, g: TileConfig, index: int = 0) -> None:
        side_length = g.tile_width * float(self._value(g, 'side_length'))
        primary_color = self.color_config.get_primary_color(index)

        ctx.set_source_rgba(*primary_color)
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


class CairoTile(TileBase):
    """Draw a Cairo tile."""

    @staticmethod
    def draw_pentagon(ctx, side_length: float, primary_color, stroke_color) -> None:
        ctx.set_source_rgba(*primary_color)
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

        # draw outline of the pentagon
        if stroke_color is not None:
            ctx.set_source_rgba(*stroke_color)
            ctx.stroke()
        ctx.move_to(0, 0)

    def draw(self, ctx: cairo.Context, g: TileConfig, index: int = 0) -> None:
        wh = g.tile_width
        side_length = wh / (4 * math.cos(PI6))
        polygon_width = wh / 2
        stroke_color = self.color_config.stroke_color if self.color_config.stroke else None

        # 1st polygon (top)
        ctx.move_to(0, 0)
        self.draw_pentagon(
            ctx,
            side_length,
            self.color_config.get_primary_color(index),
            stroke_color,
        )

        # 2nd polygon (bottom)
        ctx.rel_move_to(polygon_width, polygon_width)
        ctx.rotate(PI)
        self.draw_pentagon(
            ctx,
            side_length,
            self.color_config.get_primary_color(index + 1),
            stroke_color,
        )

        # 3rd polygon (right)
        ctx.rel_move_to(-polygon_width, -polygon_width)
        ctx.rotate(PI2)
        self.draw_pentagon(
            ctx,
            side_length,
            self.color_config.get_primary_color(index + 2),
            stroke_color,
        )

        # 4th polygon (left)
        ctx.rotate(PI)
        self.draw_pentagon(
            ctx,
            side_length,
            self.color_config.get_primary_color(index + 3),
            stroke_color,
        )
