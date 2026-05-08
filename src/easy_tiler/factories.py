"""Simple demo to render a grid of regular polygon tiles."""

import math
import random

import colorcet as cc
import numpy as np

from easy_tiler import (
    CairoTile,
    PentagonTile,
    PuckTile,
    RegularPolygonTile,
    RileyTile,
    TileBase,
    TruchetTile,
)
from easy_tiler.helpers import color


def make_tile_factory(
    tile_type: str = 'polygon',
    rot: str | int = 'random',
    fg: tuple[float, float, float, float] | str = 'random',
    bg: tuple[float, float, float, float] | str = 'random',
    inset: float | None = None,
    flipped: bool = False,
    outline: bool = False,
    outline_color: tuple[float, float, float, float] | str | None = None,
    radius: float = 3.0,
    side_length: float | None = None,
    sides: int = 4,
    palette: str | None = None,
    num_colors: int | None = None,
):
    """
    Make a factory for creating tiles of a specific type with a given configuration.
    """

    if palette is not None:
        colors = cc.palette[palette]
        if num_colors is not None:
            colors = colors[:num_colors]

    actual_outline_color = color(outline_color)

    # Pre-calculate static values outside the closure to optimize performance
    static_inset = math.sqrt(2) if inset is None else inset

    # Pre-resolve colors if they are not random
    static_fg = color(fg) if fg != 'random' else None
    static_bg = color(bg) if bg != 'random' else None

    def factory(
        x: int, y: int
    ) -> RegularPolygonTile | PuckTile | TruchetTile | RileyTile | CairoTile | PentagonTile:
        if rot == 'random':
            actual_rot = random.randint(0, 4)
        else:
            actual_rot = rot

        if static_fg is not None:
            actual_fg = static_fg
        else:
            if palette is not None:
                actual_fg = color(random.choice(colors))
            else:
                actual_fg = (random.random(), random.random(), random.random(), 1.0)

        if static_bg is not None:
            actual_bg = static_bg
        else:
            if palette is not None:
                actual_bg = color(random.choice(colors))
            else:
                actual_bg = (random.random(), random.random(), random.random(), 1.0)

        if tile_type == 'polygon':
            tile = RegularPolygonTile(
                rot=actual_rot, flipped=flipped, outline=outline, sides=sides, inset=static_inset
            )
        elif tile_type == 'puck':
            tile = PuckTile(rot=actual_rot, flipped=flipped, outline=outline)
        elif tile_type == 'truchet':
            tile = TruchetTile(rot=actual_rot, flipped=flipped, outline=outline)
        elif tile_type == 'riley':
            tile = RileyTile(rot=actual_rot, flipped=flipped, outline=outline, radius=radius)
        elif tile_type == 'cairo':
            tile = CairoTile(rot=actual_rot, flipped=flipped, outline=outline)
        elif tile_type == 'pentagon':
            tile = PentagonTile(
                rot=actual_rot, flipped=flipped, outline=outline, side_length=side_length
            )
        else:
            raise ValueError(f'Invalid tile_type: {tile_type}')

        # attach bg/fg via closure by monkeypatching draw_tile call
        def draw_tile_with_bg(ctx, wh, bg_color=None, fg_color=None, outline_color=None):
            # Call the base implementation to avoid recursive wrapper calls
            return TileBase.draw_tile(
                tile,
                ctx,
                wh,
                bg_color=actual_bg,
                fg_color=actual_fg,
                outline_color=actual_outline_color,
            )

        tile.draw_tile = draw_tile_with_bg  # type: ignore[assignment]
        return tile

    return factory


def make_sequence_factory(
    tile_type: str = 'polygon',
    sequence_length: int = 4,
    tile_sequence: list[int] | None = None,
    fg: tuple[float, float, float, float] | str = 'random',
    bg: tuple[float, float, float, float] | str = 'random',
    palette: str = 'glasbey_dark',
    num_colors: int | None = None,
    use_seed: bool = True,
    **kwargs,
):
    """Factory for creating horizontal sequences of tiles."""
    colors = cc.palette[palette]
    if num_colors is not None:
        colors = colors[:num_colors]

    if tile_sequence is None:
        tile_sequence = [0] * sequence_length
    else:
        sequence_length = len(tile_sequence)
    # Get other keyword args
    inset = kwargs.get('inset', 0.85)
    flipped = kwargs.get('flipped', False)
    outline = kwargs.get('outline', False)
    radius = kwargs.get('radius', 1.0)
    sides = kwargs.get('sides', 4)

    # Use parameters to seed randomness for this specific sequence
    if use_seed:
        rng = random.Random(f'{tile_type}-{tile_sequence}')
    else:
        rng = random.Random()
    fg_sequence_colors = rng.choices(colors, k=sequence_length)
    bg_sequence_colors = rng.choices(colors, k=sequence_length)

    def factory(x, y) -> RegularPolygonTile | PuckTile | TruchetTile | RileyTile:
        sequence_idx = x // sequence_length
        offset = x % sequence_length
        rotation = tile_sequence[offset]

        if fg == 'sequence':
            actual_fg = color(fg_sequence_colors[offset])
        elif fg == 'roll':
            sequence_colors = np.roll(fg_sequence_colors, sequence_idx)
            actual_fg = color(sequence_colors[offset])
        elif fg == 'random':
            actual_fg = (rng.random(), rng.random(), rng.random(), 1.0)
        elif fg == 'black':
            actual_fg = color(0)
        else:
            actual_fg = fg

        if bg == 'sequence':
            actual_bg = color(bg_sequence_colors[offset])
        elif bg == 'roll':
            sequence_colors = np.roll(bg_sequence_colors, sequence_idx)
            actual_bg = color(sequence_colors[offset])
        elif bg == 'random':
            actual_bg = (rng.random(), rng.random(), rng.random(), 1.0)
        elif bg == 'white':
            actual_bg = color(1)
        else:
            actual_bg = bg

        if tile_type == 'polygon':
            tile = RegularPolygonTile(
                sides=sides, rot=rotation, inset=inset, flipped=flipped, outline=outline
            )
        elif tile_type == 'puck':
            tile = PuckTile(rot=rotation, flipped=flipped, outline=outline)
        elif tile_type == 'truchet':
            tile = TruchetTile(rot=rotation, flipped=flipped, outline=outline)
        elif tile_type == 'riley':
            tile = RileyTile(rot=rotation, flipped=flipped, outline=outline, radius=radius)
        else:
            raise ValueError(f'Invalid tile_type: {tile_type}')

        # monkeypatch draw_tile to use the calculated colors
        def draw_tile_with_bg(ctx, wh, bg_color=None, fg_color=None):
            return TileBase.draw_tile(tile, ctx, wh, bg_color=actual_bg, fg_color=actual_fg)

        tile.draw_tile = draw_tile_with_bg  # type: ignore[assignment]
        return tile

    return factory


def make_node_factory(
    tile_type: str = 'polygon',
    node_sequence: np.ndarray | None = None,
    fg: tuple[float, float, float, float] | str = 'random',
    bg: tuple[float, float, float, float] | str = 'random',
    palette: str = 'glasbey_dark',
    num_colors: int | None = None,
    **kwargs,
):
    """Factory for creating nodes, i.e. a grid of tiles."""
    if node_sequence is None:
        node_sequence = np.random.randint(0, 4, size=(4, 4))
    colors = cc.palette[palette]
    if num_colors is not None:
        colors = colors[:num_colors]

    # Get other keyword args
    inset = kwargs.get('inset', 0.85)
    flipped = kwargs.get('flipped', False)
    outline = kwargs.get('outline', False)
    radius = kwargs.get('radius', 1.0)
    sides = kwargs.get('sides', 4)

    # Use parameters to seed randomness for this specific sequence
    rng = random.Random(f'{tile_type}-{node_sequence}')
    nr, nc = node_sequence.shape
    fg_sequence_colors = rng.choices(colors, k=nr * nc)
    bg_sequence_colors = rng.choices(colors, k=nr * nc)

    def factory(x, y) -> RegularPolygonTile | PuckTile | TruchetTile | RileyTile:
        node_idx = x // nc
        x_offset = x % nc
        y_offset = y % nr
        offset = x_offset + y_offset * nc
        rotation = node_sequence[y_offset, x_offset]

        if fg == 'roll':
            sequence_colors = np.roll(fg_sequence_colors, node_idx)
            actual_fg = color(sequence_colors[offset])
        elif fg == 'random':
            actual_fg = (rng.random(), rng.random(), rng.random(), 1.0)
        elif fg == 'black':
            actual_fg = color(0)
        else:
            actual_fg = fg

        if bg == 'roll':
            sequence_colors = np.roll(bg_sequence_colors, node_idx)
            actual_bg = color(sequence_colors[offset])
        elif bg == 'random':
            actual_bg = (rng.random(), rng.random(), rng.random(), 1.0)
        elif bg == 'white':
            actual_bg = color(1)
        else:
            actual_bg = bg

        if tile_type == 'polygon':
            tile = RegularPolygonTile(
                sides=sides, rot=rotation, inset=inset, flipped=flipped, outline=outline
            )
        elif tile_type == 'puck':
            tile = PuckTile(rot=rotation, flipped=flipped, outline=outline)
        elif tile_type == 'truchet':
            tile = TruchetTile(rot=rotation, flipped=flipped, outline=outline)
        elif tile_type == 'riley':
            tile = RileyTile(rot=rotation, flipped=flipped, outline=outline, radius=radius)
        else:
            raise ValueError(f'Invalid tile_type: {tile_type}')

        # monkeypatch draw_tile to use the calculated colors
        def draw_tile_with_bg(ctx, wh, bg_color=None, fg_color=None):
            return TileBase.draw_tile(tile, ctx, wh, bg_color=actual_bg, fg_color=actual_fg)

        tile.draw_tile = draw_tile_with_bg  # type: ignore[assignment]
        return tile

    return factory
