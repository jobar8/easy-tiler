from .grid import Grid
from .renderer import Renderer
from .tiles import (
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


def main() -> None:
    print('easy-tiler: run examples/demo.py to generate sample images')


__all__ = [
    'ArrowTile',
    'CairoTile',
    'CircleTile',
    'Grid',
    'PentagonTile',
    'PuckTile',
    'RegularPolygonTile',
    'Renderer',
    'RileyTile',
    'TileBase',
    'TruchetTile'
]
