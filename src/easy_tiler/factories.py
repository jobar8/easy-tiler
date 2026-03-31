"""Simple demo to render a grid of regular polygon tiles."""

import math
import random

import colorcet as cc

from easy_tiler import PuckTile, RegularPolygonTile, RileyTile, TileBase, TruchetTile
from easy_tiler.helpers import color


def make_tile_factory(
    tile_type: str = 'polygon',
    rot: str | int = 'random',
    fg: tuple[float, float, float, float] | str = 'random',
    bg: tuple[float, float, float, float] | str = 'random',
    inset: float | None = None,
    flipped: bool = False,
    outline: bool = False,
    radius: float = 3.0,
    sides: int = 4,
    palette: str | None = None,
    num_colors: int | None = None,
):

    if palette is not None:
        colors = cc.palette[palette]
        if num_colors is not None:
            colors = colors[:num_colors]

    def factory(x, y) -> RegularPolygonTile | PuckTile | TruchetTile | RileyTile:
        if rot == 'random':
            actual_rot = random.randint(0, 4)
        else:
            actual_rot = rot

        if fg == 'random':
            if palette is not None:
                actual_fg = color(random.choice(colors))
            else:
                actual_fg = (random.random(), random.random(), random.random(), 1.0)
        elif fg == 'black':
            actual_fg = color(0)
        else:
            actual_fg = fg

        if bg == 'random':
            if palette is not None:
                actual_bg = color(random.choice(colors))
            else:
                actual_bg = (random.random(), random.random(), random.random(), 1.0)
        elif bg == 'white':
            actual_bg = color(1)
        else:
            actual_bg = bg

        if inset is None:
            actual_inset = math.sqrt(2)

        if tile_type == 'polygon':
            tile = RegularPolygonTile(sides=sides, rot=actual_rot, inset=actual_inset, flipped=flipped, outline=outline)
        elif tile_type == 'puck':
            tile = PuckTile(rot=actual_rot, flipped=flipped, outline=outline)
        elif tile_type == 'truchet':
            tile = TruchetTile(rot=actual_rot, flipped=flipped, outline=outline)
        elif tile_type == 'riley':
            tile = RileyTile(rot=actual_rot, flipped=flipped, outline=outline, radius=radius)
        else:
            raise ValueError(f'Invalid tile_type: {tile_type}')

        # attach bg/fg via closure by monkeypatching draw_tile call
        def draw_tile_with_bg(ctx, wh, bg_color=None, fg_color=None):
            # Call the base implementation to avoid recursive wrapper calls
            return TileBase.draw_tile(tile, ctx, wh, bg_color=actual_bg, fg_color=actual_fg)

        tile.draw_tile = draw_tile_with_bg  # type: ignore[assignment]
        return tile

    return factory


def make_sequence_factory(
    tile_type: str = 'polygon',
    sequence_length: int = 4,
    tile_sequence: list[int] | None = None,
    fg: tuple[float, float, float, float] | str = 'random',
    bg: tuple[float, float, float, float] | str = 'random',
    palette: str | None = None,
    num_colors: int | None = None,
    **kwargs,
):
    """Factory for creating horizontal sequences of tiles."""
    if palette is not None:
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

    def factory(x, y) -> RegularPolygonTile | PuckTile | TruchetTile | RileyTile:
        sequence_idx = x // sequence_length
        offset = x % sequence_length
        rotation = tile_sequence[offset]

        # Use (sequence_idx, y) to seed randomness for this specific sequence
        rng = random.Random(f'{sequence_idx}-{y}')

        if fg == 'random':
            if palette is not None:
                sequence_colors = rng.choices(colors, k=sequence_length)
                actual_fg = color(sequence_colors[offset])
            else:
                actual_fg = (rng.random(), rng.random(), rng.random(), 1.0)
        elif fg == 'black':
            actual_fg = color(0)
        else:
            actual_fg = fg

        if bg == 'random':
            if palette is not None:
                sequence_colors = rng.choices(colors, k=sequence_length)
                actual_bg = color(sequence_colors[offset])
            else:
                actual_bg = (rng.random(), rng.random(), rng.random(), 1.0)
        elif bg == 'white':
            actual_bg = color(1)
        else:
            actual_bg = bg

        if tile_type == 'polygon':
            tile = RegularPolygonTile(sides=sides, rot=rotation, inset=inset, flipped=flipped, outline=outline)
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
