from .grid import Grid
from .renderer import Renderer
from .tiles import TileBase, RegularPolygonTile, TruchetTile, PuckTile


def main() -> None:
    print("easy-tiler: run examples/demo.py to generate sample images")


__all__ = ["Grid", "Renderer", "TileBase", "RegularPolygonTile", "TruchetTile", "PuckTile"]
