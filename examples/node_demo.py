"""Demo script for testing the sequence factory."""

import numpy as np

from easy_tiler.factories import make_node_factory
from easy_tiler.grid import Grid
from easy_tiler.io import save_png, save_svg


def run_node_demo():
    grid = Grid(12, 10, x_size=60, y_size=60)
    factory = make_node_factory(
        tile_type='truchet',
        node_sequence=np.array([[1, 2, 1], [0, 0, 0], [1, 2, 3]]),
        fg='roll',
        bg='white',
        palette='glasbey_light',
        num_colors=48,
        outline=False,
        outline_color='black',
    )

    save_png('node_demo.png', grid, factory, scale=1, background_col='white')
    save_svg('node_demo.svg', grid, factory)
    print('Wrote node_demo.png and node_demo.svg')


if __name__ == '__main__':
    run_node_demo()
