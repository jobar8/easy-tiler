from .colors import ColorConfig
from .grid import Grid
from .renderer import Renderer
from .tiles import (
    ArcTile,
    ArrowTile,
    CairoTile,
    CircleTile,
    CornerTile,
    DoughnutTile,
    PentagonTile,
    PuckTile,
    RectangleTile,
    RegularPolygonTile,
    RileyTile,
    SmithTile,
    SquareTile,
    TileBase,
    TileConfig,
    TriangleTile,
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
    'CornerTile',
    'DoughnutTile',
    'Grid',
    'PentagonTile',
    'PuckTile',
    'RectangleTile',
    'RegularPolygonTile',
    'Renderer',
    'RileyTile',
    'SmithTile',
    'SquareTile',
    'TileBase',
    'TileConfig',
    'TriangleTile',
    'TruchetTile',
]
