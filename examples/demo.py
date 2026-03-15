"""Simple demo to render a grid of polygon tiles."""

import math

from easy_tiler.io import save_png, save_svg
from easy_tiler.factories import make_tile_factory
from easy_tiler.grid import Grid

PI = math.pi


def run_demo():
    grid = Grid(8, 6, x_size=80, y_size=80, x_shift=0)

    factory = make_tile_factory(
        tile_type='polygon',
        fg='random',
        bg='white',
        sides=4,
        outline=False,
        palette='glasbey_dark',
    )
    save_png('demo.png', grid, factory, scale=1)
    save_svg('demo.svg', grid, factory)
    print('Wrote demo.png and demo.svg')


if __name__ == '__main__':
    run_demo()
