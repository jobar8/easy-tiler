"""Demo script for testing the sequence factory."""

from easy_tiler.factories import make_node_factory
from easy_tiler.grid import Grid
from easy_tiler.io import save_png, save_svg


def run_node_demo():
    # 12x10 grid with sequence length of 4
    grid = Grid(12, 10, x_size=60, y_size=60)

    # Factory with sequence length of 4, random colors from a palette
    factory = make_node_factory(
        tile_type='truchet',
        # tile_sequence=[1,0,2,3],
        # tile_sequence=[0,1,2,3],
        # tile_sequence=[1, 2, 0, 3],
        # tile_sequence=[1, 2],
        fg='roll',
        bg='roll',
        # palette='glasbey_dark',
        # palette='glasbey',
        palette='glasbey_light',
        num_colors=48,
        outline=False,
    )

    save_png('node_demo.png', grid, factory, scale=1)
    save_svg('node_demo.svg', grid, factory)
    print('Wrote node_demo.png and node_demo.svg')


if __name__ == '__main__':
    run_node_demo()
