from .colors import ColorConfig
from .grid import Grid
from .renderer import Renderer
from .tiles import (
    ArcTile,
    ArrowTile,
    CairoTile,
    CircleTile,
    DoughnutTile,
    PentagonTile,
    PuckTile,
    RegularPolygonTile,
    RileyTile,
    SmithTile,
    SquareTile,
    TileBase,
    TileConfig,
    TruchetTile,
)


def main() -> None:
    print('easy-tiler: run examples/demo.py to generate sample images')


__all__ = [
    'ArcTile',
    'ArrowTile',
    'CairoTile',
    'CircleTile',
    'ColorConfig',
    'DoughnutTile',
    'Grid',
    'PentagonTile',
    'PuckTile',
    'RegularPolygonTile',
    'Renderer',
    'RileyTile',
    'SmithTile',
    'SquareTile',
    'TileBase',
    'TileConfig',
    'TruchetTile',
]
