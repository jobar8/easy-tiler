"""Simple demo to render a grid of regular polygon tiles."""

from easy_tiler import Grid, RegularPolygonTile, TileBase, TruchetTile, PuckTile
from easy_tiler.io import save_png, save_svg
import random
import math


def make_tile_factory(sides=4):
    def factory(x, y):
        rot = random.randint(0, 4)
        # rot = 1 / 2
        # rot = 1
        fg = (random.random(), random.random(), random.random(), 1.0)
        # fg = (random.random(), random.random(), 1.0, 1.0)
        # fg = (0.0, 0.0, 0.0, 1.0)

        bg = (1.0, 1.0, 1.0, 1.0)
        # bg = (1.0, 1.0, 1.0, 0.0)
        inset = math.sqrt(2)
        inset = 0.5
        # tile = RegularPolygonTile(sides=sides, rot=rot, inset=inset, flipped=True)
        tile = PuckTile(rot=rot, flipped=False, outline=False)
        # tile = TruchetTile(rot=rot, flipped=False, variant=0, radius=3.0)

        # attach bg/fg via closure by monkeypatching draw_tile call
        def draw_tile_with_bg(ctx, wh, bg_color=None, fg_color=None):
            # Call the base implementation to avoid recursive wrapper calls
            return TileBase.draw_tile(tile, ctx, wh, bg_color=bg, fg_color=fg)

        tile.draw_tile = draw_tile_with_bg  # type: ignore[assignment]
        return tile

    return factory


def run_demo():
    grid = Grid(8, 6, x_size=80, y_size=80, x_shift=0)
    # grid = Grid(28, 26, x_size=80, y_size=80, x_shift=0, y_shift=0, x_skew=math.pi / 6, y_skew=0)

    factory = make_tile_factory(sides=3)
    save_png('demo.png', grid, factory, scale=1)
    save_svg('demo.svg', grid, factory)
    print('Wrote demo.png and demo.svg')


if __name__ == '__main__':
    run_demo()
