"""Factories building tiles for the different tiling patterns."""

import random
from collections.abc import Callable
from dataclasses import fields
from typing import Any

import numpy as np
from numpy.random._generator import Generator

from easy_tiler import (
    ArrowTile,
    CairoTile,
    CircleTile,
    PentagonTile,
    PuckTile,
    RegularPolygonTile,
    RileyTile,
    SmithTile,
    SquareTile,
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
    'square': SquareTile,
}

# Names that can be passed straight through to a TileConfig.
_TILE_CONFIG_FIELDS = frozenset(f.name for f in fields(TileConfig) if f.init)

# Names handled by ColorConfig rather than TileConfig.
_COLOR_OPTION_NAMES = frozenset({'gridlines_color', 'stroke', 'stroke_color'})


def _split_options(kwargs: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Split keyword arguments into tile config options and color options.

    Unknown names are ignored so callers can pass extra options safely.
    """
    tile_options: dict[str, Any] = {}
    color_options: dict[str, Any] = {}
    for name, value in kwargs.items():
        if name in _TILE_CONFIG_FIELDS:
            tile_options[name] = value
        elif name in _COLOR_OPTION_NAMES:
            color_options[name] = value
    return tile_options, color_options


def _make_tile(
    tile_type: str,
    *,
    config: TileConfig,
    color_config: ColorConfig,
) -> TileBase:
    try:
        tile_class = _TILE_CLASSES[tile_type]
    except KeyError as exc:
        raise ValueError(f'Invalid tile_type: {tile_type}') from exc

    # The tile class fills in any parameter the config left unset.
    return tile_class(
        config=config,
        color_config=color_config,
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
    tile_options, color_options = _split_options(kwargs)

    # Use parameters to seed randomness for this specific sequence
    random_seed = f'{use_seed}-{num_colors}' if use_seed else None
    rng = random.Random(random_seed)
    custom_palette = CustomPalette(palette, num_colors, rng)
    colors = custom_palette.colors
    primary_colors = rng.sample(colors, k=len(colors))
    secondary_colors = rng.sample(colors, k=len(colors))

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
            seed=random_seed,
            **tile_options,
        )

        color_config = ColorConfig(
            primary_color=primary_color[x % len(primary_color)]
            if isinstance(primary_color, list)
            else primary_color,
            secondary_color=secondary_color[x % len(secondary_color)]
            if isinstance(secondary_color, list)
            else secondary_color,
            palette=custom_palette,
            primary_colors=primary_colors,
            secondary_colors=secondary_colors,
            color_index=x,
            seed=random_seed,
            **color_options,
        )

        return _make_tile(
            tile_type,
            config=tile_config,
            color_config=color_config,
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
    tile_options, color_options = _split_options(kwargs)

    # Use parameters to seed randomness for this specific sequence
    random_seed = f'{tile_type}-{tile_sequence}' if use_seed else None
    rng = random.Random(random_seed)
    custom_palette = CustomPalette(palette, num_colors, rng)
    colors = custom_palette.colors
    primary_colors = rng.sample(colors, k=sequence_length)
    secondary_colors = rng.sample(colors, k=sequence_length)

    def factory(x, y) -> TileBase:
        sequence_idx = x // sequence_length
        offset = x % sequence_length
        actual_rot = tile_sequence[offset]

        tile_config = TileConfig(
            tile_width=0,
            rotation_index=actual_rot,
            seed=random_seed,
            **tile_options,
        )
        color_config = ColorConfig(
            primary_color=primary_color[x % len(primary_color)]
            if isinstance(primary_color, list)
            else primary_color,
            secondary_color=secondary_color[x % len(secondary_color)]
            if isinstance(secondary_color, list)
            else secondary_color,
            palette=custom_palette,
            primary_colors=primary_colors,
            secondary_colors=secondary_colors,
            color_index=offset,
            roll_index=sequence_idx,
            seed=random_seed,
            **color_options,
        )

        return _make_tile(
            tile_type,
            config=tile_config,
            color_config=color_config,
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
            np_rng: Generator = np.random.default_rng(len(tile_type) * len(palette))
        else:
            np_rng: Generator = np.random.default_rng()
        node_sequence = np_rng.integers(low=0, high=10, size=(4, 4))

    tile_options, color_options = _split_options(kwargs)

    random_seed = f'{use_seed}-{tile_type}-{node_sequence}' if use_seed else None
    rng = random.Random(random_seed)
    custom_palette = CustomPalette(palette, num_colors, rng)
    colors = custom_palette.colors

    nr, nc = node_sequence.shape
    primary_colors = rng.choices(colors, k=nr * nc)
    secondary_colors = rng.choices(colors, k=nr * nc)

    def factory(x, y) -> TileBase:
        node_idx = x // nc
        x_offset = x % nc
        y_offset = y % nr
        offset = x_offset + y_offset * nc
        actual_rot = node_sequence[y_offset, x_offset]

        tile_config = TileConfig(
            tile_width=0,
            rotation_index=actual_rot,
            seed=random_seed,
            **tile_options,
        )
        color_config = ColorConfig(
            primary_color=primary_color,
            secondary_color=secondary_color,
            palette=custom_palette,
            primary_colors=primary_colors,
            secondary_colors=secondary_colors,
            color_index=offset,
            roll_index=node_idx,
            seed=random_seed,
            **color_options,
        )

        return _make_tile(
            tile_type,
            config=tile_config,
            color_config=color_config,
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

    tile_options, color_options = _split_options(kwargs)

    random_seed = f'{use_seed}-{rotation_mod}-{color_mod}' if use_seed else None
    rng = random.Random(random_seed)
    custom_palette = CustomPalette(palette, num_colors, rng)
    colors = custom_palette.colors
    primary_colors = (
        rng.choices(colors, k=color_mod) if not isinstance(primary_color, list) else None
    )
    secondary_colors: list[str | tuple[float, float, float, float]] | None = (
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
            seed=random_seed,
            **tile_options,
        )
        color_config = ColorConfig(
            primary_color=primary_color,
            secondary_color=secondary_color,
            palette=custom_palette,
            primary_colors=primary_colors,
            secondary_colors=secondary_colors,
            color_index=sequence_position,
            roll_index=y,
            seed=random_seed,
            **color_options,
        )

        return _make_tile(
            tile_type,
            config=tile_config,
            color_config=color_config,
        )

    return factory
