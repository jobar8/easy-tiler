"""Simple demo to render a grid of truchet tiles."""

import math
from pathlib import Path

from easy_tiler.factories import make_tile_factory
from easy_tiler.grid import Grid
from easy_tiler.io import save_png, save_svg

PI = math.pi

cwd = Path(__file__).parent


def run_demo():
    grid = Grid(8, 6, x_size=80, y_size=80, x_shift=0)

    factory = make_tile_factory(
        tile_type='arrow',
        # rotation_index=0,
        rotation_index='random',
        arrow_width=0.2,
        # primary_color='random',
        primary_color=['blue', 'red', 'green', 'brown'],
        secondary_color='beige',
        # palette='glasbey_category10',
        # palette='ColorsOfTheWind',
        # palette='harrypotter',
        palette='FridaKahlo',
        num_colors=5,
        outline=False,
        outline_color='black',
        use_seed=True,
    )
    png_path = cwd / 'images' / 'arrow_demo.png'
    svg_path = cwd / 'images' / 'arrow_demo.svg'
    save_png(str(png_path), grid, factory, scale=1, background_col='random')
    save_svg(str(svg_path), grid, factory, background_col=None)
    print(f'Wrote {png_path} and {svg_path}')


if __name__ == '__main__':
    run_demo()
