"""Simple demo to render a grid of Cairo tiles."""

import math
from pathlib import Path

from easy_tiler.factories import make_tile_factory
from easy_tiler.grid import Grid
from easy_tiler.io import save_png, save_svg

PI = math.pi
size = 200
cwd = Path(__file__).parent


def run_demo():
    grid = Grid(
        4,
        3,
        x_size=size,
        y_size=size,
        # x_shift=80/2/math.cos(PI/6),
        # x_skew=-PI/6
        double=True,
    )

    factory = make_tile_factory(
        tile_type='cairo',
        rot=0,
        # fg='random',
        # fg='red',
        fg=['red', 'blue', 'green', 'pink'],
        bg=None,
        # palette='glasbey_category10',
        # palette='glasbey_dark',
        palette='ColorsOfTheWind',
        num_colors=5,
        outline=True,
        outline_color='black',
    )
    png_path = cwd / 'images' / 'cairo_demo.png'
    svg_path = cwd / 'images' / 'cairo_demo.svg'
    save_png(str(png_path), grid, factory, scale=1, background_col='white')
    save_svg(str(svg_path), grid, factory, background_col='white')
    print(f'Wrote {png_path} and {svg_path}')


if __name__ == '__main__':
    run_demo()
