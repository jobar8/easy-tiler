"""Simple demo to render a grid of regular polygon tiles."""

import math
import random
from collections.abc import Callable
from typing import Any

import numpy as np

from easy_tiler import (
    ArrowTile,
    CairoTile,
    CircleTile,
    PentagonTile,
    PuckTile,
    RegularPolygonTile,
    RileyTile,
    TileBase,
    TruchetTile,
)
from easy_tiler.colors import CustomPalette
from easy_tiler.tiles import TileConfig

_TILE_CLASSES: dict[str, type[TileBase]] = {
    'polygon': RegularPolygonTile,
    'puck': PuckTile,
    'truchet': TruchetTile,
    'arrow': ArrowTile,
    'riley': RileyTile,
    'cairo': CairoTile,
    'pentagon': PentagonTile,
    'circle': CircleTile,
}

_TILE_OPTIONS: dict[str, tuple[str, ...]] = {
    'polygon': ('sides', 'inset'),
    'arrow': ('width',),
    'riley': ('radius',),
    'pentagon': ('side_length',),
    'circle': ('radius',),
}


def _make_tile(
    tile_type: str,
    *,
    rot: Any,
    flipped: bool,
    outline: bool,
    config: TileConfig,
    options: dict[str, Any],
) -> TileBase:
    try:
        tile_class = _TILE_CLASSES[tile_type]
    except KeyError as exc:
        raise ValueError(f'Invalid tile_type: {tile_type}') from exc

    tile_options = {name: options[name] for name in _TILE_OPTIONS.get(tile_type, ()) if name in options}
    return tile_class(rot=rot, flipped=flipped, outline=outline, config=config, **tile_options)


def make_tile_factory(
    tile_type: str = 'polygon',
    rot: str | int = 'random',
    fg: tuple[float, float, float, float] | list[str] | str | list[tuple[float, float, float, float]] | None = 'random',
    bg: tuple[float, float, float, float] | list[str] | str | list[tuple[float, float, float, float]] | None = 'random',
    palette: str | None = None,
    num_colors: int | None = None,
    **kwargs,
):
    """
    Make a factory for creating tiles of a specific type with a given configuration.
    """
    custom_palette = CustomPalette(palette or 'Standard', num_colors)

    # Get other keyword args
    inset = kwargs.get('inset', math.sqrt(2))
    flipped = kwargs.get('flipped', False)
    outline = kwargs.get('outline', False)
    outline_color = kwargs.get('outline_color', None)
    radius = kwargs.get('radius', 3.0)
    sides = kwargs.get('sides', 4)
    side_length = kwargs.get('side_length', 1.0)  # Default side length for PentagonTile
    width = kwargs.get('width', 0.333)  # Default width for ArrowTile
    use_seed = kwargs.get('use_seed', True)

    def resolve_color(value, index: int):
        if isinstance(value, list):
            value = value[index % len(value)]
        if value == 'random' and use_seed:
            return value
        return custom_palette.get(value) if isinstance(value, (str, list, tuple)) else value

    def factory(x: int, y: int) -> TileBase:  # Return type can be any of the tile classes
        """Factory function to create a tile at position (x, y)."""
        if rot == 'random':
            actual_rot = random.randrange(4)
        else:
            actual_rot = rot

        config = TileConfig(
            fg_color=resolve_color(fg, x),
            bg_color=resolve_color(bg, x),
            outline_color=custom_palette.get(outline_color) if isinstance(outline_color, str) else outline_color,
            palette=custom_palette,
            seed=f'{tile_type}-{x}-{y}' if use_seed else None,
        )

        return _make_tile(
            tile_type,
            rot=actual_rot,
            flipped=flipped,
            outline=outline,
            config=config,
            options={
                'sides': sides,
                'inset': inset,
                'radius': radius,
                'side_length': side_length,
                'width': width,
            },
        )

    return factory


def make_sequence_factory(
    tile_type: str = 'polygon',
    sequence_length: int = 4,
    tile_sequence: list[int] | None = None,
    fg: tuple[float, float, float, float] | str = 'random',
    bg: tuple[float, float, float, float] | str = 'random',
    palette: str = 'glasbey_dark',
    num_colors: int | None = None,
    **kwargs,
):
    """Factory for creating horizontal sequences of tiles."""
    custom_palette = CustomPalette(palette, num_colors)
    colors = custom_palette.colors

    if tile_sequence is None:
        tile_sequence = [0] * sequence_length
    else:
        sequence_length = len(tile_sequence)
    # Get other keyword args
    inset = kwargs.get('inset', 0.85)
    flipped = kwargs.get('flipped', False)
    outline = kwargs.get('outline', False)
    outline_color = kwargs.get('outline_color', None)
    radius = kwargs.get('radius', 1.0)
    sides = kwargs.get('sides', 4)
    width = kwargs.get('width', 0.333)  # Default width for ArrowTile
    use_seed = kwargs.get('use_seed', True)

    # Use parameters to seed randomness for this specific sequence
    if use_seed:
        rng = random.Random(f'{tile_type}-{tile_sequence}')
    else:
        rng = random.Random()
    fg_sequence_colors = rng.choices(colors, k=sequence_length)
    bg_sequence_colors = rng.choices(colors, k=sequence_length)

    def factory(x, y) -> TileBase:
        sequence_idx = x // sequence_length
        offset = x % sequence_length
        rotation = tile_sequence[offset]

        if fg == 'sequence':
            actual_fg = custom_palette.get(fg_sequence_colors[offset])
        elif fg == 'roll':
            sequence_colors = np.roll(fg_sequence_colors, sequence_idx)
            actual_fg = custom_palette.get(sequence_colors[offset])
        elif fg == 'random':
            actual_fg = (rng.random(), rng.random(), rng.random(), 1.0)
        elif fg == 'black':
            actual_fg = custom_palette.get('black')
        elif isinstance(fg, list):
            actual_fg = custom_palette.get(fg[x % len(fg)])
        else:
            actual_fg = custom_palette.get(fg)

        if bg == 'sequence':
            actual_bg = custom_palette.get(bg_sequence_colors[offset])
        elif bg == 'roll':
            sequence_colors = np.roll(bg_sequence_colors, sequence_idx)
            actual_bg = custom_palette.get(sequence_colors[offset])
        elif bg == 'random':
            actual_bg = (rng.random(), rng.random(), rng.random(), 1.0)
        elif bg == 'white':
            actual_bg = custom_palette.get('white')
        elif bg == 'black':
            actual_bg = custom_palette.get('black')
        elif isinstance(bg, list):
            actual_bg = custom_palette.get(bg[x % len(bg)])
        else:
            actual_bg = custom_palette.get(bg)

        config = TileConfig(
            fg_color=actual_fg,
            bg_color=actual_bg,
            outline_color=custom_palette.get(outline_color),
            palette=custom_palette,
            seed=f'{tile_type}-{x}-{y}' if use_seed else None,
        )

        return _make_tile(
            tile_type,
            rot=rotation,
            flipped=flipped,
            outline=outline,
            config=config,
            options={
                'sides': sides,
                'inset': inset,
                'radius': radius,
                'width': width,
            },
        )

    return factory


def make_node_factory(
    tile_type: str = 'polygon',
    node_sequence: np.ndarray | None = None,
    fg: tuple[float, float, float, float] | list[str] | str = 'random',
    bg: tuple[float, float, float, float] | list[str] | str = 'random',
    palette: str = 'glasbey_dark',
    num_colors: int | None = None,
    use_seed: bool = True,
    **kwargs,
) -> Callable[..., TileBase]:
    """Factory for creating nodes, i.e. a grid of tiles."""
    if node_sequence is None:
        if use_seed:
            # Use parameters to seed randomness
            rng = np.random.default_rng(len(tile_type) * len(palette))
        else:
            rng = np.random.default_rng()
        node_sequence = rng.integers(low=0, high=10, size=(4, 4))

    custom_palette = CustomPalette(palette, num_colors)
    colors = custom_palette.colors

    # Get other keyword args
    inset = kwargs.get('inset', 0.85)
    flipped = kwargs.get('flipped', False)
    outline = kwargs.get('outline', False)
    outline_color = kwargs.get('outline_color', None)
    radius = kwargs.get('radius', 1.0)
    sides = kwargs.get('sides', 4)
    width = kwargs.get('width', 0.333)

    if use_seed:
        # Use parameters to seed randomness for this specific sequence
        rng = random.Random(f'{tile_type}-{node_sequence}')
    else:
        rng = random.Random()

    nr, nc = node_sequence.shape
    if isinstance(fg, list):
        fg_sequence_colors = [custom_palette.get(f) for f in fg] * (nr * nc // len(fg) + 1)
    else:
        fg_sequence_colors = rng.choices(colors, k=nr * nc)

    if isinstance(bg, list):
        bg_sequence_colors = [custom_palette.get(f) for f in bg] * (nr * nc // len(bg) + 1)
    else:
        bg_sequence_colors = rng.choices(colors, k=nr * nc)

    def factory(x, y) -> TileBase:
        node_idx = x // nc
        x_offset = x % nc
        y_offset = y % nr
        offset = x_offset + y_offset * nc
        rotation = node_sequence[y_offset, x_offset]

        if fg == 'sequence' or isinstance(fg, list):
            actual_fg = custom_palette.get(fg_sequence_colors[offset])
        elif fg == 'roll':
            sequence_colors = np.roll(fg_sequence_colors, node_idx)
            actual_fg = custom_palette.get(sequence_colors[offset])
        elif fg == 'random':
            actual_fg = (rng.random(), rng.random(), rng.random(), 1.0)
        elif fg == 'black':
            actual_fg = custom_palette.get('black')
        else:
            actual_fg = custom_palette.get(fg)

        if bg == 'sequence' or isinstance(bg, list):
            actual_bg = custom_palette.get(bg_sequence_colors[offset])
        elif bg == 'roll':
            sequence_colors = np.roll(bg_sequence_colors, node_idx)
            actual_bg = custom_palette.get(sequence_colors[offset])
        elif bg == 'random':
            actual_bg = (rng.random(), rng.random(), rng.random(), 1.0)
        elif bg == 'white':
            actual_bg = custom_palette.get('white')
        else:
            actual_bg = custom_palette.get(bg)

        config = TileConfig(
            fg_color=actual_fg,
            bg_color=actual_bg,
            outline_color=custom_palette.get(outline_color),
            palette=custom_palette,
            seed=f'{tile_type}-{x}-{y}' if use_seed else None,
        )

        return _make_tile(
            tile_type,
            rot=rotation,
            flipped=flipped,
            outline=outline,
            config=config,
            options={
                'sides': sides,
                'inset': inset,
                'radius': radius,
                'width': width,
            },
        )

    return factory
