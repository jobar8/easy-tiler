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
    SmithTile,
    TileBase,
    TruchetTile,
)
from easy_tiler.colors import ColorConfig, CustomPalette
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
    'smith': SmithTile,
}

_TILE_OPTIONS: dict[str, tuple[str, ...]] = {
    'polygon': ('sides', 'inset'),
    'arrow': ('width',),
    'riley': ('radius',),
    'pentagon': ('side_length',),
    'circle': ('radius',),
    'smith': ('radius',),
}


def _make_tile(
    tile_type: str,
    *,
    config: TileConfig,
    color_config: ColorConfig,
    options: dict[str, Any],
) -> TileBase:
    try:
        tile_class = _TILE_CLASSES[tile_type]
    except KeyError as exc:
        raise ValueError(f'Invalid tile_type: {tile_type}') from exc

    tile_options = {name: options[name] for name in _TILE_OPTIONS.get(tile_type, ()) if name in options}
    return tile_class(
        config=config,
        color_config=color_config,
        **tile_options,
    )


def make_tile_factory(
    tile_type: str = 'polygon',
    rot: str | float = 'random',
    fg: tuple[float, float, float, float] | list[str] | str | list[tuple[float, float, float, float]] | None = 'random',
    bg: tuple[float, float, float, float] | list[str] | str | list[tuple[float, float, float, float]] | None = 'random',
    palette: str | None = None,
    num_colors: int | None = None,
    **kwargs,
) -> Callable[..., TileBase]:
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
    arrow_width = kwargs.get('width', 0.333)  # Default width for ArrowTile
    use_seed = kwargs.get('use_seed', True)

    def factory(x: int, y: int) -> TileBase:  # Return type can be any of the tile classes
        """Factory function to create a tile at position (x, y)."""
        random_seed = f'{use_seed}-{x}-{y}' if use_seed else None

        if rot == 'random':
            rng = random.Random(random_seed)
            actual_rot = rng.randrange(4)  # Random rotation for 4-sided tiles (0, 1, 2, 3)
        elif isinstance(rot, (int, float)):
            actual_rot = rot

        tile_config = TileConfig(
            width=0,
            rot=actual_rot,
            flipped=flipped,
            outline=outline,
            radius=radius,
            sides=sides,
            inset=inset,
            side_length=side_length,
            arrow_width=arrow_width,
            seed=random_seed,
        )

        color_config = ColorConfig(
            fg_color=fg[x % len(fg)] if isinstance(fg, list) else fg,
            bg_color=bg[x % len(bg)] if isinstance(bg, list) else bg,
            outline_color=outline_color,
            palette=custom_palette,
            seed=random_seed,
        )

        return _make_tile(
            tile_type,
            config=tile_config,
            color_config=color_config,
            options={
                'sides': sides,
                'inset': inset,
                'radius': radius,
                'side_length': side_length,
                'width': arrow_width,
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
    # fg_sequence_colors = rng.choices(colors, k=sequence_length)
    fg_sequence_colors = colors
    # bg_sequence_colors = rng.choices(colors, k=sequence_length)
    bg_sequence_colors = colors

    def factory(x, y) -> TileBase:
        sequence_idx = x // sequence_length
        offset = x % sequence_length
        rotation = tile_sequence[offset]
        random_seed = f'{tile_type}-{x}-{y}' if use_seed else None

        tile_config = TileConfig(
            width=0,
            rot=rotation,
            flipped=flipped,
            outline=outline,
            radius=radius,
            sides=sides,
            inset=inset,
            side_length=1.0,
            arrow_width=width,
            seed=random_seed,
        )
        color_config = ColorConfig(
            fg_color=fg[x % len(fg)] if isinstance(fg, list) else fg,
            bg_color=bg[x % len(bg)] if isinstance(bg, list) else bg,
            outline_color=outline_color,
            palette=custom_palette,
            seed=random_seed,
            fg_sequence_colors=fg_sequence_colors,
            bg_sequence_colors=bg_sequence_colors,
            color_index=offset,
            roll_index=sequence_idx,
        )

        return _make_tile(
            tile_type,
            config=tile_config,
            color_config=color_config,
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

    random_seed = f'{use_seed}-{tile_type}-{node_sequence}' if use_seed else None
    rng = random.Random(random_seed)

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

        tile_config = TileConfig(
            width=0,
            rot=rotation,
            flipped=flipped,
            outline=outline,
            radius=radius,
            sides=sides,
            inset=inset,
            side_length=1.0,
            arrow_width=width,
            seed=random_seed,
        )
        color_config = ColorConfig(
            fg_color=fg,
            bg_color=bg,
            outline_color=outline_color,
            palette=custom_palette,
            seed=f'{random_seed}-{x}-{y}' if random_seed is not None else None,
            fg_sequence_colors=fg_sequence_colors,
            bg_sequence_colors=bg_sequence_colors,
            color_index=offset,
            roll_index=node_idx,
        )

        return _make_tile(
            tile_type,
            config=tile_config,
            color_config=color_config,
            options={
                'sides': sides,
                'inset': inset,
                'radius': radius,
                'width': width,
            },
        )

    return factory


def make_form_factory(
    tile_type: str = 'polygon',
    a: float = 3.0,
    b: float = 1.0,
    c: float = 0.0,
    rot_mod: int = 4,
    color_mod: int = 16,
    fg: tuple[float, float, float, float] | list[str] | str = 'random',
    bg: tuple[float, float, float, float] | list[str] | str = 'random',
    palette: str = 'glasbey_dark',
    num_colors: int | None = None,
    use_seed: bool = True,
    **kwargs,
) -> Callable[..., TileBase]:
    """Factory for creating patterns based on mathematical functions."""
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

    random_seed = f'{use_seed}-{rot_mod}-{color_mod}' if use_seed else None
    rng = random.Random(random_seed)

    if isinstance(fg, list):
        fg_sequence_colors = [custom_palette.get(f) for f in fg] * (color_mod // len(fg) + 1)
    else:
        fg_sequence_colors = rng.choices(colors, k=color_mod)

    if isinstance(bg, list):
        bg_sequence_colors = [custom_palette.get(f) for f in bg] * (color_mod // len(bg) + 1)
    else:
        bg_sequence_colors = rng.choices(colors, k=color_mod)

    def factory(x, y) -> TileBase:
        sequence_position = int(a * x + (b * y) + c)
        rotation = sequence_position % rot_mod  # Use offset to determine rotation for variety
        sequence_position = sequence_position % (color_mod)  # Ensure offset is within bounds of the color sequences

        tile_config = TileConfig(
            width=0,
            rot=rotation,
            flipped=flipped,
            outline=outline,
            radius=radius,
            sides=sides,
            inset=inset,
            side_length=1.0,
            arrow_width=width,
            seed=random_seed,
        )
        color_config = ColorConfig(
            fg_color=fg,
            bg_color=bg,
            outline_color=outline_color,
            palette=custom_palette,
            seed=f'{random_seed}-{x}-{y}' if random_seed is not None else None,
            fg_sequence_colors=fg_sequence_colors,
            bg_sequence_colors=bg_sequence_colors,
            color_index=sequence_position,
            roll_index=y,
        )

        return _make_tile(
            tile_type,
            config=tile_config,
            color_config=color_config,
            options={
                'sides': sides,
                'inset': inset,
                'radius': radius,
                'width': width,
            },
        )

    return factory
