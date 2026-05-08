from .grid import Grid
from .renderer import Renderer
from .tiles import (
    CairoTile,
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
    'CairoTile',
    'Grid',
    'PentagonTile',
    'PuckTile',
    'RegularPolygonTile',
    'Renderer',
    'RileyTile',
    'TileBase',
    'TruchetTile',
]
