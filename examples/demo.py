"""Simple demo to render a grid of regular polygon tiles."""

from easy_tiler import Grid, RegularPolygonTile, TileBase
from easy_tiler.io import save_png, save_svg
import random


def make_tile_factory(sides=4):
    def factory(x, y):
        rot = random.randint(0, 3)
        fg = (random.random(), random.random(), random.random(), 1.0)
        bg = (1.0, 1.0, 1.0, 1.0)
        tile = RegularPolygonTile(sides=sides, rot=rot)
        # attach bg/fg via closure by monkeypatching draw_tile call
        def draw_tile_with_bg(ctx, wh, bgfg=None, base_color=None):
            # Call the base implementation to avoid recursive wrapper calls
            return TileBase.draw_tile(tile, ctx, wh, bgfg=[bg, fg], base_color=base_color)

        tile.draw_tile = draw_tile_with_bg  # type: ignore[assignment]
        return tile

    return factory


def run_demo():
    grid = Grid(8, 6, cell_size=80)
    factory = make_tile_factory(sides=6)
    save_png("demo.png", grid, factory)
    save_svg("demo.svg", grid, factory)
    print("Wrote demo.png and demo.svg")


if __name__ == "__main__":
    run_demo()
