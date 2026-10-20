"""Simple demo to render a grid of regular polygon tiles."""

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
    'riley': ('radius',),
    'pentagon': ('side_length',),
    'circle': ('radius',),
    'smith': ('radius',),
}

_DEFAULT_TILE_OPTIONS: dict[str, Any] = {
    'inset': 0.85,
    'flipped': False,
    'outline': False,
    'outline_color': None,
    'radius': 1.0,
    'sides': 4,
    'side_length': 1.0,
    'arrow_width': 0.333,
}


def _get_tile_options(
    kwargs: dict[str, Any],
    defaults: dict[str, Any] = _DEFAULT_TILE_OPTIONS,
) -> dict[str, Any]:
    return defaults | {name: value for name, value in kwargs.items() if name in defaults}


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

    tile_options = {
        name: options[name] for name in _TILE_OPTIONS.get(tile_type, ()) if name in options
    }
    return tile_class(
        config=config,
        color_config=color_config,
        **tile_options,
    )


def make_tile_factory(
    tile_type: str = 'polygon',
    rotation_index: str | float = 'random',
    primary_color: tuple[float, float, float, float]
    | list[str]
    | str
    | list[tuple[float, float, float, float]]
    | None = 'random',
    secondary_color: tuple[float, float, float, float]
    | list[str]
    | str
    | list[tuple[float, float, float, float]]
    | None = 'random',
    palette: str = 'Standard',
    num_colors: int | None = None,
    use_seed: bool = True,
    **kwargs,
) -> Callable[..., TileBase]:
    """
    Make a factory for creating tiles of a specific type with a given configuration.
    """
    tile_options = _get_tile_options(kwargs, _DEFAULT_TILE_OPTIONS)

    # Use parameters to seed randomness for this specific sequence
    random_seed = f'{use_seed}-{num_colors}' if use_seed else None
    rng = random.Random(random_seed)
    custom_palette = CustomPalette(palette, num_colors, rng)
    colors = custom_palette.colors
    fg_sequence_colors = rng.sample(colors, k=len(colors))
    bg_sequence_colors = rng.sample(colors, k=len(colors))

    def factory(x: int, y: int) -> TileBase:  # Return type can be any of the tile classes
        """Factory function to create a tile at position (x, y)."""
        if rotation_index == 'random':
            # Random rotation for 4-sided tiles (0, 1, 2, 3)
            actual_rot = rng.randrange(4)
        elif isinstance(rotation_index, (int, float)):
            actual_rot = rotation_index

        tile_config = TileConfig(
            tile_width=0,
            rotation_index=actual_rot,
            flipped=tile_options['flipped'],
            outline=tile_options['outline'],
            radius=tile_options['radius'],
            sides=tile_options['sides'],
            inset=tile_options['inset'],
            side_length=tile_options['side_length'],
            arrow_width=tile_options['arrow_width'],
            seed=random_seed,
        )

        color_config = ColorConfig(
            fg_color=primary_color[x % len(primary_color)]
            if isinstance(primary_color, list)
            else primary_color,
            bg_color=secondary_color[x % len(secondary_color)]
            if isinstance(secondary_color, list)
            else secondary_color,
            outline_color=tile_options['outline_color'],
            palette=custom_palette,
            fg_sequence_colors=fg_sequence_colors,
            bg_sequence_colors=bg_sequence_colors,
            color_index=x,
            seed=random_seed,
        )

        return _make_tile(
            tile_type,
            config=tile_config,
            color_config=color_config,
            options={
                'sides': tile_options['sides'],
                'inset': tile_options['inset'],
                'radius': tile_options['radius'],
                'side_length': tile_options['side_length'],
            },
        )

    return factory


def make_sequence_factory(
    tile_type: str = 'polygon',
    tile_sequence: list[int] | None = None,
    sequence_length: int = 4,
    primary_color: tuple[float, float, float, float] | list[str] | str = 'random',
    secondary_color: tuple[float, float, float, float] | list[str] | str = 'random',
    palette: str = 'Standard',
    num_colors: int | None = None,
    use_seed: bool = True,
    **kwargs,
):
    """Factory for creating horizontal sequences of tiles."""
    if tile_sequence is None:
        tile_sequence = [0] * sequence_length
    else:
        sequence_length = len(tile_sequence)
    tile_options = _get_tile_options(kwargs, _DEFAULT_TILE_OPTIONS)

    # Use parameters to seed randomness for this specific sequence
    random_seed = f'{tile_type}-{tile_sequence}' if use_seed else None
    rng = random.Random(random_seed)
    custom_palette = CustomPalette(palette, num_colors, rng)
    colors = custom_palette.colors
    fg_sequence_colors = rng.sample(colors, k=sequence_length)
    bg_sequence_colors = rng.sample(colors, k=sequence_length)

    def factory(x, y) -> TileBase:
        sequence_idx = x // sequence_length
        offset = x % sequence_length
        actual_rot = tile_sequence[offset]

        tile_config = TileConfig(
            tile_width=0,
            rotation_index=actual_rot,
            flipped=tile_options['flipped'],
            outline=tile_options['outline'],
            radius=tile_options['radius'],
            sides=tile_options['sides'],
            inset=tile_options['inset'],
            side_length=tile_options['side_length'],
            arrow_width=tile_options['arrow_width'],
            seed=random_seed,
        )
        color_config = ColorConfig(
            fg_color=primary_color[x % len(primary_color)]
            if isinstance(primary_color, list)
            else primary_color,
            bg_color=secondary_color[x % len(secondary_color)]
            if isinstance(secondary_color, list)
            else secondary_color,
            outline_color=tile_options['outline_color'],
            palette=custom_palette,
            fg_sequence_colors=fg_sequence_colors,
            bg_sequence_colors=bg_sequence_colors,
            color_index=offset,
            roll_index=sequence_idx,
            seed=random_seed,
        )

        return _make_tile(
            tile_type,
            config=tile_config,
            color_config=color_config,
            options={
                'sides': tile_options['sides'],
                'inset': tile_options['inset'],
                'radius': tile_options['radius'],
            },
        )

    return factory


def make_node_factory(
    tile_type: str = 'polygon',
    node_sequence: np.ndarray | None = None,
    primary_color: tuple[float, float, float, float] | list[str] | str = 'random',
    secondary_color: tuple[float, float, float, float] | list[str] | str = 'random',
    palette: str = 'Standard',
    num_colors: int | None = None,
    use_seed: bool = True,
    **kwargs,
) -> Callable[..., TileBase]:
    """Factory for creating nodes, i.e. a grid of tiles."""
    if node_sequence is None:
        if use_seed:
            # Use parameters to seed randomness
            np_rng = np.random.default_rng(len(tile_type) * len(palette))
        else:
            np_rng = np.random.default_rng()
        node_sequence = np_rng.integers(low=0, high=10, size=(4, 4))

    tile_options = _get_tile_options(kwargs, _DEFAULT_TILE_OPTIONS)

    random_seed = f'{use_seed}-{tile_type}-{node_sequence}' if use_seed else None
    rng = random.Random(random_seed)
    custom_palette = CustomPalette(palette, num_colors, rng)
    colors = custom_palette.colors

    nr, nc = node_sequence.shape
    fg_sequence_colors = rng.choices(colors, k=nr * nc)
    bg_sequence_colors = rng.choices(colors, k=nr * nc)

    def factory(x, y) -> TileBase:
        node_idx = x // nc
        x_offset = x % nc
        y_offset = y % nr
        offset = x_offset + y_offset * nc
        actual_rot = node_sequence[y_offset, x_offset]

        tile_config = TileConfig(
            tile_width=0,
            rotation_index=actual_rot,
            flipped=tile_options['flipped'],
            outline=tile_options['outline'],
            radius=tile_options['radius'],
            sides=tile_options['sides'],
            inset=tile_options['inset'],
            side_length=tile_options['side_length'],
            arrow_width=tile_options['arrow_width'],
            seed=random_seed,
        )
        color_config = ColorConfig(
            fg_color=primary_color,
            bg_color=secondary_color,
            outline_color=tile_options['outline_color'],
            palette=custom_palette,
            fg_sequence_colors=fg_sequence_colors,
            bg_sequence_colors=bg_sequence_colors,
            color_index=offset,
            roll_index=node_idx,
            seed=random_seed,
        )

        return _make_tile(
            tile_type,
            config=tile_config,
            color_config=color_config,
            options={
                'sides': tile_options['sides'],
                'inset': tile_options['inset'],
                'radius': tile_options['radius'],
            },
        )

    return factory


def make_form_factory(
    tile_type: str = 'polygon',
    a: float = 3.0,
    b: float = 1.0,
    c: float = 0.0,
    rotation_mod: int = 4,
    color_mod: int = 16,
    primary_color: tuple[float, float, float, float] | list[str] | str = 'random',
    secondary_color: tuple[float, float, float, float] | list[str] | str = 'random',
    palette: str = 'Standard',
    num_colors: int | None = None,
    use_seed: bool = True,
    **kwargs,
) -> Callable[..., TileBase]:
    """Factory for creating patterns based on mathematical functions."""

    tile_options = _get_tile_options(kwargs, _DEFAULT_TILE_OPTIONS)

    random_seed = f'{use_seed}-{rotation_mod}-{color_mod}' if use_seed else None
    rng = random.Random(random_seed)
    custom_palette = CustomPalette(palette, num_colors, rng)
    colors = custom_palette.colors
    fg_sequence_colors = (
        rng.choices(colors, k=color_mod) if not isinstance(primary_color, list) else None
    )
    bg_sequence_colors: list[str | tuple[float, float, float, float]] | None = (
        rng.choices(colors, k=color_mod) if not isinstance(secondary_color, list) else None
    )

    def factory(x, y) -> TileBase:
        sequence_position = int(a * x + (b * y) + c)
        actual_rot = sequence_position % rotation_mod
        # Ensure offset is within bounds of the color sequences
        sequence_position = sequence_position % (color_mod)

        tile_config = TileConfig(
            tile_width=0,
            rotation_index=actual_rot,
            flipped=tile_options['flipped'],
            outline=tile_options['outline'],
            radius=tile_options['radius'],
            sides=tile_options['sides'],
            inset=tile_options['inset'],
            side_length=tile_options['side_length'],
            arrow_width=tile_options['arrow_width'],
            seed=random_seed,
        )
        color_config = ColorConfig(
            fg_color=primary_color,
            bg_color=secondary_color,
            outline_color=tile_options['outline_color'],
            palette=custom_palette,
            fg_sequence_colors=fg_sequence_colors,
            bg_sequence_colors=bg_sequence_colors,
            color_index=sequence_position,
            roll_index=y,
            seed=random_seed,
        )

        return _make_tile(
            tile_type,
            config=tile_config,
            color_config=color_config,
            options={
                'sides': tile_options['sides'],
                'inset': tile_options['inset'],
                'radius': tile_options['radius'],
            },
        )

    return factory
