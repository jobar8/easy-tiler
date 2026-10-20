"""Simple demo to render a grid of polygon tiles."""

from pathlib import Path

from easy_tiler.factories import make_tile_factory
from easy_tiler.grid import Grid
from easy_tiler.io import save_png, save_svg

cwd = Path(__file__).parent


def run_demo():
    grid = Grid(8, 6, x_size=80, y_size=80, x_shift=0)

    factory = make_tile_factory(
        tile_type='puck',
        rotation_index='random',
        primary_color=['black', 'blue', 'green', 'red'],
        secondary_color='white',
        outline=False,
    )
    png_path = cwd / 'images' / 'puck_demo.png'
    svg_path = cwd / 'images' / 'puck_demo.svg'
    save_png(str(png_path), grid, factory, scale=1, background_col='white')
    save_svg(str(svg_path), grid, factory)
    print(f'Wrote {png_path} and {svg_path}')


if __name__ == '__main__':
    run_demo()
