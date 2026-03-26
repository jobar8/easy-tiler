from .grid import Grid
from .renderer import Renderer
from .tiles import PuckTile, RegularPolygonTile, RileyTile, TileBase, TruchetTile


def main() -> None:
    print('easy-tiler: run examples/demo.py to generate sample images')


__all__ = ['Grid', 'PuckTile', 'RegularPolygonTile', 'Renderer', 'RileyTile', 'TileBase', 'TruchetTile']
