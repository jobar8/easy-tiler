from .grid import Grid
from .renderer import Renderer
from .tiles import (
    ArrowTile,
    CairoTile,
    CircleTile,
    PaletteTileConfig,
    PentagonTile,
    PuckTile,
    RandomColorTileConfig,
    RegularPolygonTile,
    RileyTile,
    SmithTile,
    TileBase,
    TileConfig,
    TruchetTile,
)


def main() -> None:
    print('easy-tiler: run examples/demo.py to generate sample images')


__all__ = [
    'ArrowTile',
    'CairoTile',
    'CircleTile',
    'Grid',
    'PaletteTileConfig',
    'PentagonTile',
    'PuckTile',
    'RandomColorTileConfig',
    'RegularPolygonTile',
    'Renderer',
    'RileyTile',
    'SmithTile',
    'TileBase',
    'TileConfig',
    'TruchetTile',
]
