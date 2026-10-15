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
        tile_type='smith',
        # node_sequence=np.array([[0, 3, 2, 1], [0, 0, 0, 0], [1, 2, 3, 3], [1, 2, 3, 0]]),
        node_sequence=np.array([[0, 1, 0, 1], [0, 0, 0, 0], [1, 0, 1, 0], [1, 1, 1, 1]]),
        # node_sequence=None,
        # fg='roll',
        fg='sequence',
        # fg='random_choice',
        # fg=['blue', 'blue',  'green'],
        # bg=['black', 'white', 'black'],
        bg='transparent',
        # palette='glasbey_light',
        # palette='BlueRidgePkwy',
        palette='Budnitz',
        num_colors=48,
        outline=False,
        outline_color='black',
        width=0.5,
        radius=0.52,
        use_seed=True,
    )
    png_path = cwd / 'images' / 'node_demo2.png'
    svg_path = cwd / 'images' / 'node_demo2.svg'
    save_png(str(png_path), grid, factory, scale=1, background_col='white')
    save_svg(str(svg_path), grid, factory)
    print(f'Wrote {png_path} and {svg_path}')


if __name__ == '__main__':
    run_node_demo()
