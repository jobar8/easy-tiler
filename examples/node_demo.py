"""Demo script for testing the node factory."""

from pathlib import Path

import numpy as np

from easy_tiler.factories import make_node_factory
from easy_tiler.grid import Grid
from easy_tiler.io import save_png, save_svg

cwd = Path(__file__).parent


def run_node_demo():
    grid = Grid(12, 12, x_size=60, y_size=60)
    factory = make_node_factory(
        tile_type='truchet',
        node_sequence=np.array([[1, 1, 2], [0, 0, 0], [1, 2, 3]]),
        primary_color='roll',
        # primary_color=['beige', 'green', 'brown', 'red', 'yellow'],
        secondary_color=['orange', 'white', 'black'],
        # secondary_color='white',
        # palette='glasbey_light',
        # palette='BlueRidgePkwy',
        palette='CrazyLaceAgate',
        num_colors=48,
        outline=False,
        outline_color='black',
    )
    png_path = cwd / 'images' / 'node_demo.png'
    svg_path = cwd / 'images' / 'node_demo.svg'
    save_png(str(png_path), grid, factory, scale=1, background_col='white')
    save_svg(str(svg_path), grid, factory)
    print(f'Wrote {png_path} and {svg_path}')


if __name__ == '__main__':
    run_node_demo()
