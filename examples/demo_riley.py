"""Simple demo to render a grid of riley tiles."""

import math
from pathlib import Path

from easy_tiler.factories import make_tile_factory
from easy_tiler.grid import Grid
from easy_tiler.io import save_png, save_svg

PI = math.pi
cwd = Path(__file__).parent


def run_demo():
    grid = Grid(8, 6, x_size=80, y_size=80, x_shift=0)
    # grid = Grid(28, 26, x_size=80, y_size=80, x_shift=40, y_shift=0, x_skew=PI / 12, y_skew=0)

    factory = make_tile_factory(
        tile_type='riley',
        # rot='random',
        rot=0,
        flipped=False,
        # fg='random',
        fg='sequence',
        # fg=['blue', 'red', 'green', 'brown'],
        # bg='beige',
        bg=None,
        radius=1,
        # palette='glasbey_category10',
        # palette='ColorsOfTheWind',
        # palette='harrypotter',
        palette='FridaKahlo',
        num_colors=5,
        outline=True,
        outline_color='black',
        use_seed=False,
    )
    png_path = cwd / 'images' / 'riley_demo.png'
    svg_path = cwd / 'images' / 'riley_demo.svg'
    save_png(str(png_path), grid, factory, scale=1, background_col='white')
    save_svg(str(svg_path), grid, factory)
    print(f'Wrote {png_path} and {svg_path}')


if __name__ == '__main__':
    run_demo()
