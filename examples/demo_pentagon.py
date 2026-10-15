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
    # grid = Grid(28, 26, x_size=80, y_size=80, x_shift=40, y_shift=0, x_skew=PI / 12, y_skew=0)

    factory = make_tile_factory(
        tile_type='pentagon',
        rot=1,
        fg=None,
        bg='white',
        palette='glasbey_category10',
        num_colors=5,
        outline=True,
        outline_color='black',
        side_length=0.75,
        use_seed=False,
    )
    png_path = cwd / 'images' / 'pentagon_demo.png'
    svg_path = cwd / 'images' / 'pentagon_demo.svg'
    save_png(str(png_path), grid, factory, scale=0.95, background_col='random')
    save_svg(str(svg_path), grid, factory, background_col=None)
    print(f'Wrote {png_path} and {svg_path}')


if __name__ == '__main__':
    run_demo()
